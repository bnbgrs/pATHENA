"""Executable entry point for the native pATHENA desktop shell."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from athena.api.client import CoreApiClient
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.canonical_memory_extensions import install_canonical_memory_extensions
from athena.desktop.command_palette import install_command_palette
from athena.desktop.files_workspace import install_files_workspace
from athena.desktop.jobs_workspace import install_jobs_workspace
from athena.desktop.knowledge_acceptance import install_knowledge_acceptance
from athena.desktop.knowledge_workspace import install_knowledge_workspace
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.scheduler_supervisor import DesktopJobSchedulerSupervisor
from athena.desktop.supervisor import DesktopCoreSupervisor
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace

_INITIAL_CORE_REFRESH_DELAYS_MS = (250, 750, 1_500, 3_000, 5_000, 10_000, 20_000)
_CORE_REFRESH_HEARTBEAT_MS = 30_000


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create or reuse the Qt application and apply pATHENA's visual system."""
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    if existing is not None:
        raise RuntimeError("pATHENA desktop requires QApplication ownership.")

    arguments = list(argv) if argv is not None else list(sys.argv)
    app = QApplication(arguments)
    # Keep the internal application/organization identity stable for compatibility
    # with existing local paths and settings while presenting the pATHENA product.
    app.setApplicationName("ATHENA")
    app.setOrganizationName("ATHENA")
    app.setApplicationDisplayName("pATHENA")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(PATHENA_STYLESHEET)
    return app


def _schedule_initial_core_refreshes(
    controller: DesktopApiController,
    supervisor: DesktopCoreSupervisor | None = None,
    scheduler_supervisor: DesktopJobSchedulerSupervisor | None = None,
) -> None:
    """Bridge slow or failed child-process startup with bounded recovery refreshes."""
    for delay_ms in _INITIAL_CORE_REFRESH_DELAYS_MS:
        if supervisor is None and scheduler_supervisor is None:
            QTimer.singleShot(delay_ms, controller.refresh)
            continue

        def recover_and_refresh() -> None:
            if supervisor is not None:
                supervisor.ensure_running()
            if scheduler_supervisor is not None:
                scheduler_supervisor.ensure_running()
            controller.refresh()

        QTimer.singleShot(delay_ms, recover_and_refresh)


def _start_core_refresh_heartbeat(
    controller: DesktopApiController,
    supervisor: DesktopCoreSupervisor | None = None,
    scheduler_supervisor: DesktopJobSchedulerSupervisor | None = None,
) -> QTimer:
    """Keep Core status and owned background processes self-healing."""
    timer = QTimer(controller)
    timer.setInterval(_CORE_REFRESH_HEARTBEAT_MS)

    if supervisor is None and scheduler_supervisor is None:
        timer.timeout.connect(controller.refresh)
    else:

        def recover_and_refresh() -> None:
            if supervisor is not None:
                supervisor.ensure_running()
            if scheduler_supervisor is not None:
                scheduler_supervisor.ensure_running()
            controller.refresh()

        timer.timeout.connect(recover_and_refresh)

    timer.start()
    return timer


def main(argv: Sequence[str] | None = None) -> int:
    app = create_application(argv)
    client = CoreApiClient.from_environment()
    supervisor = DesktopCoreSupervisor(client=client, parent=app)
    scheduler_supervisor = DesktopJobSchedulerSupervisor(parent=app)
    app.aboutToQuit.connect(scheduler_supervisor.stop)
    app.aboutToQuit.connect(supervisor.stop)

    # Startup is deliberately fail-soft. Transient child launch failures must not
    # kill the user-facing desktop; bounded retries and the heartbeat keep both
    # Core and durable scheduler supervision self-healing.
    supervisor.ensure_running()
    scheduler_supervisor.ensure_running()

    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)
    knowledge_workspace = install_knowledge_workspace(window, controller)
    knowledge_acceptance = install_knowledge_acceptance(
        knowledge_workspace,
        controller,
    )
    canonical_memory_extensions = install_canonical_memory_extensions(
        knowledge_workspace
    )
    research_workspace = install_research_workspace(window)
    research_results_extension = install_research_results_extension(research_workspace)
    # Result/proposal review is a deliberate user decision surface. Keep the
    # selected immutable result stable until the user explicitly refreshes jobs.
    research_results_extension.refresh_timer.stop()
    jobs_workspace = install_jobs_workspace(window, scheduler_supervisor)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    system_backup = install_system_backup(window, system_workspace)
    apply_workspace_presentation(window)
    command_palette = install_command_palette(window)
    _schedule_initial_core_refreshes(
        controller,
        supervisor,
        scheduler_supervisor,
    )
    heartbeat = _start_core_refresh_heartbeat(
        controller,
        supervisor,
        scheduler_supervisor,
    )
    window.show()
    exit_code = app.exec()
    heartbeat.stop()
    canonical_memory_extensions.deleteLater()
    knowledge_acceptance.deleteLater()
    knowledge_workspace.deleteLater()
    research_results_extension.deleteLater()
    research_workspace.deleteLater()
    jobs_workspace.deleteLater()
    files_workspace.deleteLater()
    system_backup.deleteLater()
    system_workspace.deleteLater()
    command_palette.deleteLater()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
