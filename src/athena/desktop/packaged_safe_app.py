"""UI-only packaged Windows entry point for the pATHENA Safe Preview."""

from __future__ import annotations

import sys
from collections.abc import Sequence

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
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_quiet_workspace import apply_quiet_workspace_refinement
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


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
    app.setApplicationDisplayName("pATHENA UI Safe Preview")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(PATHENA_STYLESHEET)
    return app


def main(argv: Sequence[str] | None = None) -> int:
    app = create_application(argv)

    # UI-only safety mode: construct the normal API controller for presentation
    # wiring, but deliberately start no Core, scheduler, worker, or child process.
    client = CoreApiClient.from_environment()
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
    apply_quiet_workspace_refinement(window)
    command_palette = install_command_palette(window)

    window.show()
    exit_code = app.exec()

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
