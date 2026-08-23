"""Safe packaged Windows entry point for current pATHENA with one owned Core."""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from pathlib import Path

os.environ.setdefault("QT_OPENGL", "software")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QSG_RHI_BACKEND", "software")

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
from athena.desktop.pathena_interaction_refinement import install_interaction_refinement
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_layout_refinement_2200 import install_layout_refinement
from athena.desktop.pathena_progressive_workspace_2300 import (
    install_progressive_workspace_refinement,
)
from athena.desktop.pathena_research_experience_2500 import install_research_experience
from athena.desktop.pathena_research_knowledge_transition_2700 import (
    install_research_knowledge_transition,
)
from athena.desktop.pathena_research_proposal_clarity_2600 import (
    install_research_proposal_clarity,
)
from athena.desktop.pathena_research_readability_2400 import install_research_readability
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_startup_experience_2900 import install_startup_experience
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_ui_refinement_integrity import apply_complete_ui_refinements
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.supervisor import DesktopCoreSupervisor
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace

_INITIAL_CORE_REFRESH_DELAYS_MS = (350, 900, 1_800, 3_500, 6_000, 10_000)
_CORE_REFRESH_HEARTBEAT_MS = 30_000


def _package_directory() -> Path:
    return Path(sys.executable).resolve().parent


def _sibling_executable(package_directory: Path, name: str) -> str:
    return str(package_directory / name)


def _install_helper_routing(package_directory: Path) -> str:
    """Route every Python-style desktop subprocess to the dedicated helper executable.

    Desktop workspaces import the real ``sys`` module and launch ``sys.executable -m ...``.
    In a frozen application that executable would otherwise be pATHENA.exe itself, causing
    recursive desktop startup.  Rebinding the global interpreter path after QApplication
    creation makes all existing and future workspace subprocesses use the packaged helper.
    """
    helper = _sibling_executable(package_directory, "pATHENA-Helper.exe")
    sys.executable = helper
    return helper


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    if existing is not None:
        raise RuntimeError("pATHENA desktop requires QApplication ownership.")

    arguments = list(argv) if argv is not None else list(sys.argv)
    app = QApplication(arguments)
    app.setApplicationName("ATHENA")
    app.setOrganizationName("ATHENA")
    app.setApplicationDisplayName("pATHENA")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(PATHENA_STYLESHEET)
    return app


def _schedule_refreshes(controller: DesktopApiController) -> None:
    for delay_ms in _INITIAL_CORE_REFRESH_DELAYS_MS:
        QTimer.singleShot(delay_ms, controller.refresh)


def _start_refresh_heartbeat(controller: DesktopApiController) -> QTimer:
    timer = QTimer(controller)
    timer.setInterval(_CORE_REFRESH_HEARTBEAT_MS)
    timer.timeout.connect(controller.refresh)
    timer.start()
    return timer


def main(argv: Sequence[str] | None = None) -> int:
    package_directory = _package_directory()
    app = create_application(argv)
    _install_helper_routing(package_directory)

    client = CoreApiClient.from_environment()
    supervisor = DesktopCoreSupervisor(
        client=client,
        executable=_sibling_executable(package_directory, "pATHENA-Core.exe"),
        parent=app,
    )
    app.aboutToQuit.connect(supervisor.stop)

    # Safety rule for packaged preview: one launch attempt only. Never self-heal by
    # respawning a failed Core, so a Core failure cannot become a process storm.
    try:
        supervisor.start()
    except RuntimeError:
        pass

    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)
    knowledge_workspace = install_knowledge_workspace(window, controller)
    knowledge_acceptance = install_knowledge_acceptance(knowledge_workspace, controller)
    apply_knowledge_acceptance_presentation(knowledge_acceptance)
    canonical_memory_extensions = install_canonical_memory_extensions(knowledge_workspace)

    research_workspace = install_research_workspace(window)
    research_results_extension = install_research_results_extension(research_workspace)
    apply_research_result_presentation(research_results_extension)
    research_results_extension.refresh_timer.stop()

    jobs_workspace = install_jobs_workspace(window, None)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    system_backup = install_system_backup(window, system_workspace)

    apply_shell_density(window)
    apply_workspace_presentation(window)
    command_palette = install_command_palette(window)
    startup_experience = install_startup_experience(window)
    apply_complete_ui_refinements(window)
    interaction_refinement = install_interaction_refinement(window)
    layout_refinement = install_layout_refinement(window)
    progressive_workspace_refinement = install_progressive_workspace_refinement(window)
    research_readability = install_research_readability(window, research_results_extension)
    research_experience = install_research_experience(
        research_workspace,
        research_results_extension,
    )
    research_proposal_clarity = install_research_proposal_clarity(
        research_results_extension
    )
    research_knowledge_transition = install_research_knowledge_transition(
        window,
        research_results_extension,
    )

    _schedule_refreshes(controller)
    heartbeat = _start_refresh_heartbeat(controller)
    window.show()
    exit_code = app.exec()

    heartbeat.stop()
    research_knowledge_transition.deleteLater()
    research_proposal_clarity.deleteLater()
    research_experience.deleteLater()
    research_readability.deleteLater()
    progressive_workspace_refinement.deleteLater()
    layout_refinement.deleteLater()
    interaction_refinement.deleteLater()
    startup_experience.deleteLater()
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
