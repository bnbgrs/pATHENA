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
from athena.desktop.pathena_async_focus_integrity_6200 import apply_ui_refinements_6101_6200
from athena.desktop.pathena_background_completion_accessibility import (
    install_background_completion_accessibility,
)
from athena.desktop.pathena_backup_action_context_6800 import install_backup_action_context
from athena.desktop.pathena_backup_details_provenance import (
    install_backup_details_provenance,
)
from athena.desktop.pathena_backup_target_context import install_backup_target_context
from athena.desktop.pathena_chat_scroll_stability_6600 import install_chat_scroll_stability
from athena.desktop.pathena_command_palette_truth_6500 import install_command_palette_truth
from athena.desktop.pathena_detail_provenance_6300 import apply_detail_provenance
from athena.desktop.pathena_dialog_focus_return_7200 import install_dialog_focus_return
from athena.desktop.pathena_empty_search_comprehension_7100 import (
    install_empty_search_comprehension,
)
from athena.desktop.pathena_inspector_scanability_6700 import apply_inspector_scanability
from athena.desktop.pathena_interaction_refinement import install_interaction_refinement
from athena.desktop.pathena_jobs_experience_2800 import install_jobs_experience
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_knowledge_selection_continuity import (
    install_knowledge_selection_continuity,
)
from athena.desktop.pathena_knowledge_tab_refresh_handoff import (
    install_knowledge_tab_refresh_handoff,
)
from athena.desktop.pathena_layout_refinement_2200 import install_layout_refinement
from athena.desktop.pathena_message_action_accessibility_6900 import (
    install_message_action_accessibility,
)
from athena.desktop.pathena_message_action_quiet_7000 import install_message_action_quiet
from athena.desktop.pathena_message_action_tab_order import (
    install_message_action_tab_order,
)
from athena.desktop.pathena_progressive_workspace_2300 import (
    install_progressive_workspace_refinement,
)
from athena.desktop.pathena_quiet_success_decay_6400 import apply_quiet_success_decay
from athena.desktop.pathena_research_experience_2500 import install_research_experience
from athena.desktop.pathena_research_knowledge_transition_2700 import (
    install_research_knowledge_transition,
)
from athena.desktop.pathena_research_proposal_clarity_2600 import (
    install_research_proposal_clarity,
)
from athena.desktop.pathena_research_proposal_density import (
    install_research_proposal_density,
)
from athena.desktop.pathena_research_proposal_focus import (
    install_research_proposal_focus,
)
from athena.desktop.pathena_research_readability_2400 import install_research_readability
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_result_scope_clarity import apply_result_scope_clarity
from athena.desktop.pathena_selection_disappearance_handoff import (
    install_selection_disappearance_handoff,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_startup_experience_2900 import install_startup_experience
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_ui_refinement_integrity import apply_complete_ui_refinements
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

    supervisor.ensure_running()
    scheduler_supervisor.ensure_running()

    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)
    knowledge_workspace = install_knowledge_workspace(window, controller)
    knowledge_selection_continuity = install_knowledge_selection_continuity(
        knowledge_workspace
    )
    knowledge_tab_refresh_handoff = install_knowledge_tab_refresh_handoff(knowledge_workspace)
    knowledge_acceptance = install_knowledge_acceptance(knowledge_workspace, controller)
    apply_knowledge_acceptance_presentation(knowledge_acceptance)
    canonical_memory_extensions = install_canonical_memory_extensions(knowledge_workspace)
    research_workspace = install_research_workspace(window)
    research_results_extension = install_research_results_extension(research_workspace)
    apply_research_result_presentation(research_results_extension)
    research_proposal_density = install_research_proposal_density(research_results_extension)
    research_proposal_focus = install_research_proposal_focus(research_results_extension)
    research_results_extension.refresh_timer.stop()
    jobs_workspace = install_jobs_workspace(window, scheduler_supervisor)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    system_backup = install_system_backup(window, system_workspace)
    backup_target_context = install_backup_target_context(system_backup.backup)
    backup_details_provenance = install_backup_details_provenance(system_backup.backup)
    apply_shell_density(window)
    apply_workspace_presentation(window)
    command_palette = install_command_palette(window)
    command_palette_truth = install_command_palette_truth(command_palette)
    empty_search_comprehension = install_empty_search_comprehension(
        window,
        command_palette,
        command_palette_truth,
        canonical_memory_extensions,
    )
    dialog_focus_return = install_dialog_focus_return(window)
    jobs_experience = install_jobs_experience(jobs_workspace)
    startup_experience = install_startup_experience(window)
    apply_complete_ui_refinements(window)
    apply_ui_refinements_6101_6200(window)
    apply_result_scope_clarity(window)
    detail_provenance = apply_detail_provenance(window)
    success_decay = apply_quiet_success_decay(window)
    chat_scroll_stability = install_chat_scroll_stability(window)
    apply_inspector_scanability(window)
    backup_action_context = install_backup_action_context(window)
    message_action_accessibility = install_message_action_accessibility(window)
    message_action_tab_order = install_message_action_tab_order(window)
    message_action_quiet = install_message_action_quiet(window)
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
    background_completion_accessibility = install_background_completion_accessibility(
        files_workspace,
        jobs_workspace,
        system_backup.backup,
        research_results_extension,
    )
    selection_disappearance_handoff = install_selection_disappearance_handoff(
        files_workspace,
        jobs_workspace,
        research_workspace,
        system_backup.backup,
        research_results_extension,
    )
    _schedule_initial_core_refreshes(controller, supervisor, scheduler_supervisor)
    heartbeat = _start_core_refresh_heartbeat(controller, supervisor, scheduler_supervisor)
    window.show()
    exit_code = app.exec()
    heartbeat.stop()
    selection_disappearance_handoff.deleteLater()
    background_completion_accessibility.deleteLater()
    research_knowledge_transition.deleteLater()
    research_proposal_clarity.deleteLater()
    research_experience.deleteLater()
    research_readability.deleteLater()
    progressive_workspace_refinement.deleteLater()
    layout_refinement.deleteLater()
    interaction_refinement.deleteLater()
    message_action_quiet.deleteLater()
    message_action_tab_order.deleteLater()
    message_action_accessibility.deleteLater()
    backup_action_context.deleteLater()
    backup_details_provenance.deleteLater()
    backup_target_context.deleteLater()
    chat_scroll_stability.deleteLater()
    success_decay.deleteLater()
    detail_provenance.deleteLater()
    startup_experience.deleteLater()
    jobs_experience.deleteLater()
    dialog_focus_return.deleteLater()
    empty_search_comprehension.deleteLater()
    canonical_memory_extensions.deleteLater()
    knowledge_acceptance.deleteLater()
    knowledge_tab_refresh_handoff.deleteLater()
    knowledge_selection_continuity.deleteLater()
    knowledge_workspace.deleteLater()
    research_proposal_focus.deleteLater()
    research_proposal_density.deleteLater()
    research_results_extension.deleteLater()
    research_workspace.deleteLater()
    jobs_workspace.deleteLater()
    files_workspace.deleteLater()
    system_backup.deleteLater()
    system_workspace.deleteLater()
    command_palette_truth.deleteLater()
    command_palette.deleteLater()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
