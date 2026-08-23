from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QTimer

from athena.api.client import CoreApiClient
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.app import create_application
from athena.desktop.canonical_memory_extensions import install_canonical_memory_extensions
from athena.desktop.command_palette import install_command_palette
from athena.desktop.files_workspace import install_files_workspace
from athena.desktop.jobs_workspace import install_jobs_workspace
from athena.desktop.knowledge_acceptance import install_knowledge_acceptance
from athena.desktop.knowledge_workspace import install_knowledge_workspace
from athena.desktop.pathena_interaction_refinement import install_interaction_refinement
from athena.desktop.pathena_jobs_experience_2800 import install_jobs_experience
from athena.desktop.pathena_knowledge_acceptance_presentation import apply_knowledge_acceptance_presentation
from athena.desktop.pathena_layout_refinement_2200 import install_layout_refinement
from athena.desktop.pathena_progressive_workspace_2300 import install_progressive_workspace_refinement
from athena.desktop.pathena_research_experience_2500 import install_research_experience
from athena.desktop.pathena_research_knowledge_transition_2700 import install_research_knowledge_transition
from athena.desktop.pathena_research_proposal_clarity_2600 import install_research_proposal_clarity
from athena.desktop.pathena_research_readability_2400 import install_research_readability
from athena.desktop.pathena_research_result_presentation import apply_research_result_presentation
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_ui_refinement_integrity import apply_complete_ui_refinements
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def build_window() -> PathenaMainWindow:
    client = CoreApiClient.from_environment()
    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)

    knowledge_workspace = install_knowledge_workspace(window, controller)
    knowledge_acceptance = install_knowledge_acceptance(knowledge_workspace, controller)
    apply_knowledge_acceptance_presentation(knowledge_acceptance)
    install_canonical_memory_extensions(knowledge_workspace)

    research_workspace = install_research_workspace(window)
    research_results_extension = install_research_results_extension(research_workspace)
    apply_research_result_presentation(research_results_extension)
    research_results_extension.refresh_timer.stop()

    jobs_workspace = install_jobs_workspace(window, None)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    install_system_backup(window, system_workspace)

    apply_shell_density(window)
    apply_workspace_presentation(window)
    install_command_palette(window)

    jobs_experience = install_jobs_experience(jobs_workspace)
    apply_complete_ui_refinements(window)
    install_interaction_refinement(window)
    install_layout_refinement(window)
    install_progressive_workspace_refinement(window)
    install_research_readability(window, research_results_extension)
    install_research_experience(research_workspace, research_results_extension)
    install_research_proposal_clarity(research_results_extension)
    install_research_knowledge_transition(window, research_results_extension)

    # Keep presentation controllers alive for the lifetime of the window.
    window._snapshot_refs = (  # type: ignore[attr-defined]
        controller,
        knowledge_workspace,
        knowledge_acceptance,
        research_workspace,
        research_results_extension,
        jobs_workspace,
        jobs_experience,
        files_workspace,
        system_workspace,
    )
    return window


def main() -> int:
    app = create_application(["pathena-ui-snapshot"])
    window = build_window()
    window.resize(1480, 900)
    window.show()

    destination = Path(os.environ.get("PATHENA_UI_SNAPSHOT", "artifacts/pathena-ui.png"))
    destination.parent.mkdir(parents=True, exist_ok=True)

    def capture() -> None:
        app.processEvents()
        pixmap = window.grab()
        if not pixmap.save(str(destination), "PNG"):
            raise RuntimeError(f"Unable to save UI snapshot to {destination}")
        print(destination.resolve())
        app.quit()

    QTimer.singleShot(750, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
