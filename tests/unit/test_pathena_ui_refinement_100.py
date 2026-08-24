from __future__ import annotations

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QAbstractItemView, QApplication, QListWidget

from athena.desktop.app import create_application
from athena.desktop.canonical_memory_extensions import install_canonical_memory_extensions
from athena.desktop.command_palette import install_command_palette
from athena.desktop.files_workspace import install_files_workspace
from athena.desktop.jobs_workspace import install_jobs_workspace
from athena.desktop.knowledge_acceptance import install_knowledge_acceptance
from athena.desktop.knowledge_workspace import install_knowledge_workspace
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_ui_refinement_100 import UI_REFINEMENT_TASKS
from athena.desktop.pathena_ui_refinement_integrity import apply_complete_ui_refinements
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


def _app() -> QApplication:
    return create_application(["pathena-ui-refinement-100-test"])


def test_all_100_refinements_target_real_installed_desktop_controls() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)

    knowledge = install_knowledge_workspace(window, None)
    acceptance = install_knowledge_acceptance(knowledge, None)
    apply_knowledge_acceptance_presentation(acceptance)
    canonical = install_canonical_memory_extensions(knowledge)

    research = install_research_workspace(window)
    research_results = install_research_results_extension(research)
    apply_research_result_presentation(research_results)
    research_results.refresh_timer.stop()

    jobs = install_jobs_workspace(window, None)
    jobs._refresh_timer.stop()
    jobs._scheduler_status_timer.stop()

    files = install_files_workspace(window)
    files._refresh_timer.stop()

    system = install_system_workspace(window, None)
    backup = install_system_backup(window, system)

    apply_shell_density(window)
    apply_workspace_presentation(window)
    commands = install_command_palette(window)

    try:
        assert len(UI_REFINEMENT_TASKS) == 100
        assert len(set(UI_REFINEMENT_TASKS)) == 100

        applied = apply_complete_ui_refinements(window)

        assert applied == tuple(range(1, 101))
        assert window.property("pathenaUiRefinementAppliedCount") == 100
        assert window.property("pathenaUiRefinementTaskCount") == 100
        assert window.chat_selector.accessibleName() == "Conversation"
        assert window.prompt_input.accessibleName() == "Message"
        assert knowledge.search_input.isClearButtonEnabled()
        assert research_results.proposal_list.accessibleName() == "Research proposals"
        assert backup.backup.snapshots.accessibleName() == "Backup snapshots"
        assert commands.query.accessibleName() == "Search commands"
        assert commands.help_text.accessibleName().startswith("pATHENA capabilities")

        for object_name in (
            "persistentKnowledgeList",
            "persistentClaimList",
            "semanticReviewList",
            "claimRelationList",
            "researchJobList",
            "researchProposalList",
            "durableJobList",
            "sourceList",
            "backupSnapshotList",
            "commandPaletteResults",
        ):
            widget = window.findChild(QListWidget, object_name)
            assert widget is not None
            assert (
                widget.selectionMode()
                == QAbstractItemView.SelectionMode.SingleSelection
            )
    finally:
        canonical.deleteLater()
        acceptance.deleteLater()
        research_results.deleteLater()
        research.deleteLater()
        jobs.deleteLater()
        files.deleteLater()
        backup.deleteLater()
        system.deleteLater()
        commands.deleteLater()
        knowledge.deleteLater()
        window.close()
        window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
