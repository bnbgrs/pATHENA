"""One hundred small, presentation-only refinements for the pATHENA desktop.

This module deliberately changes no domain state, API contract or persistence rule.
It runs only after the real workspaces and command palette have been installed.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTabWidget,
    QWidget,
)

TWidget = TypeVar("TWidget", bound=QWidget)

UI_REFINEMENT_TASKS: tuple[str, ...] = (
    "Name primary navigation for assistive technology",
    "Describe primary navigation purpose",
    "Name workspace page stack",
    "Name conversation selector",
    "Describe conversation selector",
    "Name model selector",
    "Describe model selector",
    "Name chat scroll surface",
    "Name chat message canvas",
    "Name local connection status",
    "Name message composer",
    "Describe message composer",
    "Name source-grounding toggle",
    "Describe source-grounding toggle",
    "Name send action",
    "Describe send action shortcut",
    "Name conversation details toggle",
    "Describe conversation details toggle",
    "Name grounded context toggle",
    "Describe grounded context toggle",
    "Name new-conversation action",
    "Describe new-conversation action",
    "Name delete-conversation action",
    "Describe delete-conversation action",
    "Name context-window slider",
    "Name exact context-window field",
    "Name maximum-response slider",
    "Name exact maximum-response field",
    "Name temperature field",
    "Name reasoning toggle",
    "Name canonical-memory tabs",
    "Name canonical-memory search",
    "Enable clear affordance on canonical-memory search",
    "Name canonical Knowledge list",
    "Name canonical Knowledge details",
    "Name canonical Claims list",
    "Name canonical Claim details",
    "Name semantic decision list",
    "Name semantic decision details",
    "Name Claim relation list",
    "Name canonical-memory refresh action",
    "Name decision-mode selector",
    "Name related-Claim navigation action",
    "Name canonical acceptance action",
    "Name Knowledge history action",
    "Name contradiction confirmation action",
    "Name contradiction rejection action",
    "Name merge confirmation action",
    "Name keep-separate action",
    "Name Knowledge copy-details action",
    "Name research question field",
    "Describe research question field",
    "Name research-run filter",
    "Enable clear affordance on research-run filter",
    "Name research-run list",
    "Name research-run details",
    "Name start-research action",
    "Name research refresh action",
    "Name research cancellation action",
    "Name ResearchResult review panel",
    "Name ResearchResult view action",
    "Name proposal creation action",
    "Name proposal refresh action",
    "Name research proposal list",
    "Name proposal acceptance action",
    "Name keep-separate proposal action",
    "Name proposal rejection action",
    "Name durable Jobs list",
    "Name durable Job details",
    "Name scheduler status",
    "Name Jobs refresh action",
    "Name Job pause action",
    "Name Job resume action",
    "Name Job wake action",
    "Name Job cancel action",
    "Name imported Sources list",
    "Name Source details",
    "Name file import action",
    "Name Source process/retry action",
    "Name Sources refresh action",
    "Name System operation tabs",
    "Name runtime status workspace",
    "Name runtime refresh action",
    "Name runtime detail text",
    "Name backup snapshot list",
    "Name backup details",
    "Name backup creation action",
    "Name backup verification action",
    "Name deep backup verification action",
    "Name isolated restore action",
    "Name backup-target listing action",
    "Name backup-target registration action",
    "Name PALLAS semantic field",
    "Remove keyboard focus from PALLAS canvas",
    "Name command-palette query",
    "Name command-palette results",
    "Name in-app help text",
    "Name in-app help dialog",
    "Disable horizontal scrolling on primary data lists",
    "Use single-selection semantics on primary data lists",
)


def _accessible(name: str, description: str = "") -> Callable[[QWidget], None]:
    def apply(widget: QWidget) -> None:
        widget.setAccessibleName(name)
        if description:
            widget.setAccessibleDescription(description)

    return apply


def _apply(
    applied: list[int],
    task_id: int,
    widget: TWidget | None,
    action: Callable[[TWidget], None],
) -> None:
    if widget is None:
        return
    action(widget)
    applied.append(task_id)


def _named_child(root: QWidget, widget_type: type[TWidget], name: str) -> TWidget | None:
    return root.findChild(widget_type, name)


def _button_with_text(root: QWidget, text: str) -> QPushButton | None:
    return next((button for button in root.findChildren(QPushButton) if button.text() == text), None)


def _configure_list(widget: QListWidget) -> None:
    widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)


def _single_selection(widget: QListWidget) -> None:
    widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


def apply_ui_refinements(window: QWidget) -> tuple[int, ...]:
    """Apply the 100 presentation tasks and return the task IDs actually applied."""
    applied: list[int] = []

    navigation = _named_child(window, QListWidget, "navigation")
    pages = getattr(window, "pages", None)
    pages_widget = pages if isinstance(pages, QStackedWidget) else None
    chat_selector = getattr(window, "chat_selector", None)
    chat_combo = chat_selector if isinstance(chat_selector, QComboBox) else None
    model_selector = getattr(window, "model_selector", None)
    model_combo = model_selector if isinstance(model_selector, QComboBox) else None
    chat_scroll = _named_child(window, QScrollArea, "chatScroll")
    chat_messages = _named_child(window, QWidget, "chatMessages")
    status_text = getattr(window, "status_text", None)
    status_label = status_text if isinstance(status_text, QLabel) else None

    _apply(applied, 1, navigation, _accessible("Workspace navigation"))
    _apply(applied, 2, navigation, _accessible("Workspace navigation", "Switch between Chat, Knowledge, Research, Jobs, Files, System and Settings."))
    _apply(applied, 3, pages_widget, _accessible("Current workspace"))
    _apply(applied, 4, chat_combo, _accessible("Conversation"))
    _apply(applied, 5, chat_combo, _accessible("Conversation", "Choose a persisted local conversation or start a new one."))
    _apply(applied, 6, model_combo, _accessible("Local model"))
    _apply(applied, 7, model_combo, _accessible("Local model", "Choose the local language model used for this conversation."))
    _apply(applied, 8, chat_scroll, _accessible("Conversation messages"))
    _apply(applied, 9, chat_messages, _accessible("Message history"))
    _apply(applied, 10, status_label, _accessible("Local connection status"))

    prompt = getattr(window, "prompt_input", None)
    prompt_input = prompt if isinstance(prompt, QLineEdit) else None
    ground = getattr(window, "ground_button", None)
    ground_button = ground if isinstance(ground, QPushButton) else None
    send = getattr(window, "send_button", None)
    send_button = send if isinstance(send, QPushButton) else None
    details_button = _named_child(window, QPushButton, "detailsToggle")
    context_button = _named_child(window, QPushButton, "contextToggle")
    new_chat = getattr(window, "new_chat_button", None)
    new_button = new_chat if isinstance(new_chat, QPushButton) else None
    delete_chat = getattr(window, "delete_chat_button", None)
    delete_button = delete_chat if isinstance(delete_chat, QPushButton) else None

    _apply(applied, 11, prompt_input, _accessible("Message"))
    _apply(applied, 12, prompt_input, _accessible("Message", "Ask pATHENA, explore local knowledge, or continue the selected conversation."))
    _apply(applied, 13, ground_button, _accessible("Use sources"))
    _apply(applied, 14, ground_button, _accessible("Use sources", "Ground the next response in available local sources and evidence."))
    _apply(applied, 15, send_button, _accessible("Send message"))
    _apply(applied, 16, send_button, _accessible("Send message", "Send the current message. Keyboard shortcut: Ctrl+Enter."))
    _apply(applied, 17, details_button, _accessible("Conversation details"))
    _apply(applied, 18, details_button, _accessible("Conversation details", "Show or hide conversation metadata and provenance."))
    _apply(applied, 19, context_button, _accessible("Source context"))
    _apply(applied, 20, context_button, _accessible("Source context", "Show or hide evidence from the latest grounded response."))
    _apply(applied, 21, new_button, _accessible("New conversation"))
    _apply(applied, 22, new_button, _accessible("New conversation", "Start a new persisted conversation."))
    _apply(applied, 23, delete_button, _accessible("Delete conversation"))
    _apply(applied, 24, delete_button, _accessible("Delete conversation", "Delete the currently selected persisted conversation."))

    context_slider = getattr(window, "context_slider", None)
    context_slider_widget = context_slider if isinstance(context_slider, QSlider) else None
    context_spin = getattr(window, "context_spin", None)
    context_spin_widget = context_spin if isinstance(context_spin, QSpinBox) else None
    output_slider = getattr(window, "max_output_slider", None)
    output_slider_widget = output_slider if isinstance(output_slider, QSlider) else None
    output_spin = getattr(window, "max_output_spin", None)
    output_spin_widget = output_spin if isinstance(output_spin, QSpinBox) else None
    temperature = getattr(window, "temperature_spin", None)
    temperature_widget = temperature if isinstance(temperature, QDoubleSpinBox) else None
    thinking = getattr(window, "thinking_checkbox", None)
    thinking_widget = thinking if isinstance(thinking, QCheckBox) else None

    _apply(applied, 25, context_slider_widget, _accessible("Context window"))
    _apply(applied, 26, context_spin_widget, _accessible("Context window in tokens"))
    _apply(applied, 27, output_slider_widget, _accessible("Maximum response length"))
    _apply(applied, 28, output_spin_widget, _accessible("Maximum response tokens"))
    _apply(applied, 29, temperature_widget, _accessible("Temperature"))
    _apply(applied, 30, thinking_widget, _accessible("Reasoning"))

    knowledge = _named_child(window, QWidget, "knowledgeWorkspace")
    knowledge_tabs = _named_child(window, QTabWidget, "canonicalMemoryTabs")
    knowledge_search = _named_child(window, QLineEdit, "knowledgeSearchInput")
    knowledge_list = _named_child(window, QListWidget, "persistentKnowledgeList")
    knowledge_details = _named_child(window, QPlainTextEdit, "persistentKnowledgeDetails")
    claim_list = _named_child(window, QListWidget, "persistentClaimList")
    claim_details = _named_child(window, QPlainTextEdit, "persistentClaimDetails")
    decision_list = _named_child(window, QListWidget, "semanticReviewList")
    decision_details = _named_child(window, QPlainTextEdit, "semanticReviewDetails")
    relation_list = _named_child(window, QListWidget, "claimRelationList")

    _apply(applied, 31, knowledge_tabs, _accessible("Canonical memory views"))
    _apply(applied, 32, knowledge_search, _accessible("Search canonical memory"))
    _apply(applied, 33, knowledge_search, lambda widget: widget.setClearButtonEnabled(True))
    _apply(applied, 34, knowledge_list, _accessible("Canonical knowledge"))
    _apply(applied, 35, knowledge_details, _accessible("Knowledge details and provenance"))
    _apply(applied, 36, claim_list, _accessible("Canonical claims"))
    _apply(applied, 37, claim_details, _accessible("Claim evidence and provenance"))
    _apply(applied, 38, decision_list, _accessible("Canonical memory decisions"))
    _apply(applied, 39, decision_details, _accessible("Decision comparison"))
    _apply(applied, 40, relation_list, _accessible("Related claims and evidence"))

    knowledge_refresh = _button_with_text(knowledge, "Refresh") if knowledge is not None else None
    decision_mode = _named_child(window, QComboBox, "semanticDecisionMode")
    open_related = _named_child(window, QPushButton, "openRelatedClaimButton")
    acceptance = _named_child(window, QPushButton, "knowledgeAcceptanceButton")
    history = _button_with_text(knowledge, "History") if knowledge is not None else None
    confirm_contradiction = _button_with_text(knowledge, "Confirm contradiction") if knowledge is not None else None
    reject_decision = _button_with_text(knowledge, "Reject") if knowledge is not None else None
    merge = _button_with_text(knowledge, "Merge") if knowledge is not None else None
    keep_separate = _button_with_text(knowledge, "Keep separate") if knowledge is not None else None
    copy_details = _button_with_text(knowledge, "Copy details") if knowledge is not None else None

    _apply(applied, 41, knowledge_refresh, _accessible("Refresh canonical memory"))
    _apply(applied, 42, decision_mode, _accessible("Decision type"))
    _apply(applied, 43, open_related, _accessible("Open related claim"))
    _apply(applied, 44, acceptance, _accessible("Add reviewed items to canonical memory"))
    _apply(applied, 45, history, _accessible("Show immutable revision history"))
    _apply(applied, 46, confirm_contradiction, _accessible("Confirm contradiction"))
    _apply(applied, 47, reject_decision, _accessible("Reject decision"))
    _apply(applied, 48, merge, _accessible("Merge with canonical entity"))
    _apply(applied, 49, keep_separate, _accessible("Keep entities separate"))
    _apply(applied, 50, copy_details, _accessible("Copy canonical details"))

    research = _named_child(window, QWidget, "researchWorkspace")
    research_query = _named_child(window, QLineEdit, "researchQueryInput")
    research_filter = _named_child(window, QLineEdit, "researchJobFilter")
    research_jobs = _named_child(window, QListWidget, "researchJobList")
    research_details = _named_child(window, QPlainTextEdit, "researchDetails")
    research_start = _named_child(window, QPushButton, "researchStartButton")
    research_refresh = _named_child(window, QPushButton, "researchRefreshButton")
    research_cancel = _named_child(window, QPushButton, "researchCancelButton")
    result_panel = _named_child(window, QWidget, "researchResultPanel")
    result_button = _named_child(window, QPushButton, "researchResultButton")
    propose_button = _named_child(window, QPushButton, "researchProposeButton")
    proposal_refresh = _named_child(window, QPushButton, "researchProposalRefreshButton")
    proposal_list = _named_child(window, QListWidget, "researchProposalList")
    proposal_accept = _named_child(window, QPushButton, "researchProposalAcceptButton")
    proposal_separate = _named_child(window, QPushButton, "researchProposalSeparateButton")
    proposal_reject = _named_child(window, QPushButton, "researchProposalRejectButton")

    _apply(applied, 51, research_query, _accessible("Research question"))
    _apply(applied, 52, research_query, _accessible("Research question", "Create a durable research run across captured local sources."))
    _apply(applied, 53, research_filter, _accessible("Filter research runs"))
    _apply(applied, 54, research_filter, lambda widget: widget.setClearButtonEnabled(True))
    _apply(applied, 55, research_jobs, _accessible("Research runs"))
    _apply(applied, 56, research_details, _accessible("Research result and run details"))
    _apply(applied, 57, research_start, _accessible("Start research"))
    _apply(applied, 58, research_refresh, _accessible("Refresh research runs"))
    _apply(applied, 59, research_cancel, _accessible("Cancel selected research run"))
    _apply(applied, 60, result_panel, _accessible("Research result and canonical memory review"))
    _apply(applied, 61, result_button, _accessible("View research result"))
    _apply(applied, 62, propose_button, _accessible("Create canonical memory proposals"))
    _apply(applied, 63, proposal_refresh, _accessible("Review research proposals"))
    _apply(applied, 64, proposal_list, _accessible("Research proposals"))
    _apply(applied, 65, proposal_accept, _accessible("Accept proposal"))
    _apply(applied, 66, proposal_separate, _accessible("Accept proposal as separate"))
    _apply(applied, 67, proposal_reject, _accessible("Reject proposal"))

    jobs = _named_child(window, QWidget, "jobsWorkspace")
    durable_jobs = _named_child(window, QListWidget, "durableJobList")
    job_details = _named_child(window, QPlainTextEdit, "jobDetails")
    scheduler_status = next((label for label in jobs.findChildren(QLabel) if label.text().startswith("Scheduler")), None) if jobs is not None else None
    job_refresh = _named_child(window, QPushButton, "jobRefreshButton")
    job_pause = _named_child(window, QPushButton, "jobPauseButton")
    job_resume = _named_child(window, QPushButton, "jobResumeButton")
    job_wake = _named_child(window, QPushButton, "jobWakeButton")
    job_cancel = _named_child(window, QPushButton, "jobCancelButton")

    _apply(applied, 68, durable_jobs, _accessible("Durable background jobs"))
    _apply(applied, 69, job_details, _accessible("Background job details and checkpoints"))
    _apply(applied, 70, scheduler_status, _accessible("Scheduler status"))
    _apply(applied, 71, job_refresh, _accessible("Refresh background jobs"))
    _apply(applied, 72, job_pause, _accessible("Pause selected job"))
    _apply(applied, 73, job_resume, _accessible("Resume selected job"))
    _apply(applied, 74, job_wake, _accessible("Wake selected job"))
    _apply(applied, 75, job_cancel, _accessible("Cancel selected job"))

    files = _named_child(window, QWidget, "filesWorkspace")
    sources = _named_child(window, QListWidget, "sourceList")
    source_details = _named_child(window, QPlainTextEdit, "sourceDetails")
    file_import = _named_child(window, QPushButton, "fileImportButton")
    file_process = _named_child(window, QPushButton, "fileProcessButton")
    file_refresh = _named_child(window, QPushButton, "fileRefreshButton")

    _apply(applied, 76, sources, _accessible("Imported local sources"))
    _apply(applied, 77, source_details, _accessible("Source capture and retrieval details"))
    _apply(applied, 78, file_import, _accessible("Import local file"))
    _apply(applied, 79, file_process, _accessible("Process or retry selected source"))
    _apply(applied, 80, file_refresh, _accessible("Refresh imported sources"))

    system_tabs = _named_child(window, QTabWidget, "systemOperationsTabs")
    system = _named_child(window, QWidget, "systemWorkspace")
    system_refresh = _button_with_text(system, "Refresh") if system is not None else None
    system_detail = next((label for label in system.findChildren(QLabel, "settingsHelp") if label.isWordWrap()), None) if system is not None else None
    backup = _named_child(window, QWidget, "backupWorkspace")
    backup_list = _named_child(window, QListWidget, "backupSnapshotList")
    backup_details = _named_child(window, QPlainTextEdit, "backupDetails")
    backup_create = _named_child(window, QPushButton, "backupCreateButton")
    backup_verify = _named_child(window, QPushButton, "backupVerifyButton")
    backup_deep = _named_child(window, QPushButton, "backupDeepVerifyButton")
    backup_restore = _named_child(window, QPushButton, "backupRestoreButton")
    backup_targets = _named_child(window, QPushButton, "backupTargetsButton")
    backup_add_target = _named_child(window, QPushButton, "backupAddTargetButton")

    _apply(applied, 81, system_tabs, _accessible("System operations"))
    _apply(applied, 82, system, _accessible("Local runtime status"))
    _apply(applied, 83, system_refresh, _accessible("Refresh runtime status"))
    _apply(applied, 84, system_detail, _accessible("Runtime status detail"))
    _apply(applied, 85, backup_list, _accessible("Backup snapshots"))
    _apply(applied, 86, backup_details, _accessible("Backup verification and restore details"))
    _apply(applied, 87, backup_create, _accessible("Create verified backup"))
    _apply(applied, 88, backup_verify, _accessible("Verify selected backup"))
    _apply(applied, 89, backup_deep, _accessible("Deep verify selected backup"))
    _apply(applied, 90, backup_restore, _accessible("Restore selected backup to isolated location"))
    _apply(applied, 91, backup_targets, _accessible("Show backup targets"))
    _apply(applied, 92, backup_add_target, _accessible("Add backup target"))

    pallas = _named_child(window, QWidget, "pallasVisualPlaceholder")
    command_query = _named_child(window, QLineEdit, "commandPaletteQuery")
    command_results = _named_child(window, QListWidget, "commandPaletteResults")
    help_text = _named_child(window, QPlainTextEdit, "helpText")
    help_dialog = _named_child(window, QDialog, "helpDialog")

    _apply(applied, 93, pallas, _accessible("PALLAS semantic field", "A local reactive visualization of the visible workspace context."))
    _apply(applied, 94, pallas, lambda widget: widget.setFocusPolicy(Qt.FocusPolicy.NoFocus))
    _apply(applied, 95, command_query, _accessible("Search commands"))
    _apply(applied, 96, command_results, _accessible("Available commands"))
    _apply(applied, 97, help_text, _accessible("pATHENA capabilities and keyboard help"))
    _apply(applied, 98, help_dialog, _accessible("pATHENA help"))

    primary_lists = tuple(
        widget
        for widget in (
            navigation,
            knowledge_list,
            claim_list,
            decision_list,
            relation_list,
            research_jobs,
            proposal_list,
            durable_jobs,
            sources,
            backup_list,
            command_results,
        )
        if isinstance(widget, QListWidget)
    )
    if primary_lists:
        for widget in primary_lists:
            _configure_list(widget)
        applied.append(99)
        for widget in primary_lists:
            _single_selection(widget)
        applied.append(100)

    window.setProperty("pathenaUiRefinementAppliedCount", len(applied))
    window.setProperty("pathenaUiRefinementTaskCount", len(UI_REFINEMENT_TASKS))
    return tuple(applied)
