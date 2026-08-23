"""One hundred small, presentation-only refinements for the pATHENA desktop.

This module deliberately changes no domain state, API contract or persistence rule.
It runs only after the real workspaces and command palette have been installed.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, cast

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


def _named_child(
    root: QWidget,
    widget_type: type[TWidget],
    name: str,
) -> TWidget | None:
    return cast(TWidget | None, root.findChild(widget_type, name))


def _widget_attr(root: QWidget, name: str, widget_type: type[TWidget]) -> TWidget | None:
    value = getattr(root, name, None)
    return value if isinstance(value, widget_type) else None


def _button_with_text(root: QWidget | None, text: str) -> QPushButton | None:
    if root is None:
        return None
    return next(
        (button for button in root.findChildren(QPushButton) if button.text() == text),
        None,
    )


def _label_starting_with(root: QWidget | None, prefix: str) -> QLabel | None:
    if root is None:
        return None
    return next(
        (label for label in root.findChildren(QLabel) if label.text().startswith(prefix)),
        None,
    )


def _runtime_detail(root: QWidget | None) -> QLabel | None:
    if root is None:
        return None
    labels = root.findChildren(QLabel, "settingsHelp")
    return next(
        (
            label
            for label in labels
            if label.text().startswith("Awaiting local Core snapshot")
        ),
        labels[-1] if labels else None,
    )


def _configure_list(widget: QListWidget) -> None:
    widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    widget.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)


def _single_selection(widget: QListWidget) -> None:
    widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


def apply_ui_refinements(window: QWidget) -> tuple[int, ...]:
    """Apply the 100 presentation tasks and return the task IDs actually applied."""
    applied: list[int] = []

    navigation = _named_child(window, QListWidget, "navigation")
    pages = _widget_attr(window, "pages", QStackedWidget)
    chat_combo = _widget_attr(window, "chat_selector", QComboBox)
    model_combo = _widget_attr(window, "model_selector", QComboBox)
    chat_scroll = _named_child(window, QScrollArea, "chatScroll")
    chat_messages = _named_child(window, QWidget, "chatMessages")
    status_label = _widget_attr(window, "status_text", QLabel)

    _apply(applied, 1, navigation, _accessible("Workspace navigation"))
    _apply(
        applied,
        2,
        navigation,
        _accessible(
            "Workspace navigation",
            "Switch between Chat, Knowledge, Research, Jobs, Files, System and Settings.",
        ),
    )
    _apply(applied, 3, pages, _accessible("Current workspace"))
    _apply(applied, 4, chat_combo, _accessible("Conversation"))
    _apply(
        applied,
        5,
        chat_combo,
        _accessible(
            "Conversation",
            "Choose a persisted local conversation or start a new one.",
        ),
    )
    _apply(applied, 6, model_combo, _accessible("Local model"))
    _apply(
        applied,
        7,
        model_combo,
        _accessible(
            "Local model",
            "Choose the local language model used for this conversation.",
        ),
    )
    _apply(applied, 8, chat_scroll, _accessible("Conversation messages"))
    _apply(applied, 9, chat_messages, _accessible("Message history"))
    _apply(applied, 10, status_label, _accessible("Local connection status"))

    prompt = _widget_attr(window, "prompt_input", QLineEdit)
    ground = _widget_attr(window, "ground_button", QPushButton)
    send = _widget_attr(window, "send_button", QPushButton)
    details = _named_child(window, QPushButton, "detailsToggle")
    context = _named_child(window, QPushButton, "contextToggle")
    new_chat = _widget_attr(window, "new_chat_button", QPushButton)
    delete_chat = _widget_attr(window, "delete_chat_button", QPushButton)

    _apply(applied, 11, prompt, _accessible("Message"))
    _apply(
        applied,
        12,
        prompt,
        _accessible(
            "Message",
            "Ask pATHENA, explore local knowledge, or continue the selected conversation.",
        ),
    )
    _apply(applied, 13, ground, _accessible("Use sources"))
    _apply(
        applied,
        14,
        ground,
        _accessible(
            "Use sources",
            "Ground the next response in available local sources and evidence.",
        ),
    )
    _apply(applied, 15, send, _accessible("Send message"))
    _apply(
        applied,
        16,
        send,
        _accessible(
            "Send message",
            "Send the current message. Keyboard shortcut: Ctrl+Enter.",
        ),
    )
    _apply(applied, 17, details, _accessible("Conversation details"))
    _apply(
        applied,
        18,
        details,
        _accessible(
            "Conversation details",
            "Show or hide conversation metadata and provenance.",
        ),
    )
    _apply(applied, 19, context, _accessible("Source context"))
    _apply(
        applied,
        20,
        context,
        _accessible(
            "Source context",
            "Show or hide evidence from the latest grounded response.",
        ),
    )
    _apply(applied, 21, new_chat, _accessible("New conversation"))
    _apply(
        applied,
        22,
        new_chat,
        _accessible("New conversation", "Start a new persisted conversation."),
    )
    _apply(applied, 23, delete_chat, _accessible("Delete conversation"))
    _apply(
        applied,
        24,
        delete_chat,
        _accessible(
            "Delete conversation",
            "Delete the currently selected persisted conversation.",
        ),
    )

    _apply(
        applied,
        25,
        _widget_attr(window, "context_slider", QSlider),
        _accessible("Context window"),
    )
    _apply(
        applied,
        26,
        _widget_attr(window, "context_spin", QSpinBox),
        _accessible("Context window in tokens"),
    )
    _apply(
        applied,
        27,
        _widget_attr(window, "max_output_slider", QSlider),
        _accessible("Maximum response length"),
    )
    _apply(
        applied,
        28,
        _widget_attr(window, "max_output_spin", QSpinBox),
        _accessible("Maximum response tokens"),
    )
    _apply(
        applied,
        29,
        _widget_attr(window, "temperature_spin", QDoubleSpinBox),
        _accessible("Temperature"),
    )
    _apply(
        applied,
        30,
        _widget_attr(window, "thinking_checkbox", QCheckBox),
        _accessible("Reasoning"),
    )

    knowledge = _named_child(window, QWidget, "knowledgeWorkspace")
    knowledge_tabs = _named_child(window, QTabWidget, "canonicalMemoryTabs")
    knowledge_search = _named_child(window, QLineEdit, "knowledgeSearchInput")
    knowledge_list = _named_child(window, QListWidget, "persistentKnowledgeList")
    knowledge_details = _named_child(
        window,
        QPlainTextEdit,
        "persistentKnowledgeDetails",
    )
    claim_list = _named_child(window, QListWidget, "persistentClaimList")
    claim_details = _named_child(window, QPlainTextEdit, "persistentClaimDetails")
    decision_list = _named_child(window, QListWidget, "semanticReviewList")
    decision_details = _named_child(window, QPlainTextEdit, "semanticReviewDetails")
    relation_list = _named_child(window, QListWidget, "claimRelationList")

    _apply(applied, 31, knowledge_tabs, _accessible("Canonical memory views"))
    _apply(applied, 32, knowledge_search, _accessible("Search canonical memory"))
    _apply(
        applied,
        33,
        knowledge_search,
        lambda widget: widget.setClearButtonEnabled(True),
    )
    _apply(applied, 34, knowledge_list, _accessible("Canonical knowledge"))
    _apply(
        applied,
        35,
        knowledge_details,
        _accessible("Knowledge details and provenance"),
    )
    _apply(applied, 36, claim_list, _accessible("Canonical claims"))
    _apply(
        applied,
        37,
        claim_details,
        _accessible("Claim evidence and provenance"),
    )
    _apply(applied, 38, decision_list, _accessible("Canonical memory decisions"))
    _apply(applied, 39, decision_details, _accessible("Decision comparison"))
    _apply(applied, 40, relation_list, _accessible("Related claims and evidence"))

    _apply(
        applied,
        41,
        _button_with_text(knowledge, "Refresh"),
        _accessible("Refresh canonical memory"),
    )
    _apply(
        applied,
        42,
        _named_child(window, QComboBox, "semanticDecisionMode"),
        _accessible("Decision type"),
    )
    _apply(
        applied,
        43,
        _named_child(window, QPushButton, "openRelatedClaimButton"),
        _accessible("Open related claim"),
    )
    _apply(
        applied,
        44,
        _named_child(window, QPushButton, "knowledgeAcceptanceButton"),
        _accessible("Add reviewed items to canonical memory"),
    )
    _apply(
        applied,
        45,
        _button_with_text(knowledge, "History"),
        _accessible("Show immutable revision history"),
    )
    _apply(
        applied,
        46,
        _button_with_text(knowledge, "Confirm contradiction"),
        _accessible("Confirm contradiction"),
    )
    _apply(
        applied,
        47,
        _button_with_text(knowledge, "Reject"),
        _accessible("Reject decision"),
    )
    _apply(
        applied,
        48,
        _button_with_text(knowledge, "Merge"),
        _accessible("Merge with canonical entity"),
    )
    _apply(
        applied,
        49,
        _button_with_text(knowledge, "Keep separate"),
        _accessible("Keep entities separate"),
    )
    _apply(
        applied,
        50,
        _button_with_text(knowledge, "Copy details"),
        _accessible("Copy canonical details"),
    )

    research_query = _named_child(window, QLineEdit, "researchQueryInput")
    research_filter = _named_child(window, QLineEdit, "researchJobFilter")
    research_jobs = _named_child(window, QListWidget, "researchJobList")
    research_details = _named_child(window, QPlainTextEdit, "researchDetails")
    result_panel = _named_child(window, QWidget, "researchResultPanel")
    proposal_list = _named_child(window, QListWidget, "researchProposalList")

    _apply(applied, 51, research_query, _accessible("Research question"))
    _apply(
        applied,
        52,
        research_query,
        _accessible(
            "Research question",
            "Create a durable research run across captured local sources.",
        ),
    )
    _apply(applied, 53, research_filter, _accessible("Filter research runs"))
    _apply(
        applied,
        54,
        research_filter,
        lambda widget: widget.setClearButtonEnabled(True),
    )
    _apply(applied, 55, research_jobs, _accessible("Research runs"))
    _apply(
        applied,
        56,
        research_details,
        _accessible("Research result and run details"),
    )
    _apply(
        applied,
        57,
        _named_child(window, QPushButton, "researchStartButton"),
        _accessible("Start research"),
    )
    _apply(
        applied,
        58,
        _named_child(window, QPushButton, "researchRefreshButton"),
        _accessible("Refresh research runs"),
    )
    _apply(
        applied,
        59,
        _named_child(window, QPushButton, "researchCancelButton"),
        _accessible("Cancel selected research run"),
    )
    _apply(
        applied,
        60,
        result_panel,
        _accessible("Research result and canonical memory review"),
    )
    _apply(
        applied,
        61,
        _named_child(window, QPushButton, "researchResultButton"),
        _accessible("View research result"),
    )
    _apply(
        applied,
        62,
        _named_child(window, QPushButton, "researchProposeButton"),
        _accessible("Create canonical memory proposals"),
    )
    _apply(
        applied,
        63,
        _named_child(window, QPushButton, "researchProposalRefreshButton"),
        _accessible("Review research proposals"),
    )
    _apply(applied, 64, proposal_list, _accessible("Research proposals"))
    _apply(
        applied,
        65,
        _named_child(window, QPushButton, "researchProposalAcceptButton"),
        _accessible("Accept proposal"),
    )
    _apply(
        applied,
        66,
        _named_child(window, QPushButton, "researchProposalSeparateButton"),
        _accessible("Accept proposal as separate"),
    )
    _apply(
        applied,
        67,
        _named_child(window, QPushButton, "researchProposalRejectButton"),
        _accessible("Reject proposal"),
    )

    jobs = _named_child(window, QWidget, "jobsWorkspace")
    durable_jobs = _named_child(window, QListWidget, "durableJobList")
    job_details = _named_child(window, QPlainTextEdit, "jobDetails")

    _apply(applied, 68, durable_jobs, _accessible("Durable background jobs"))
    _apply(
        applied,
        69,
        job_details,
        _accessible("Background job details and checkpoints"),
    )
    _apply(
        applied,
        70,
        _label_starting_with(jobs, "Scheduler"),
        _accessible("Scheduler status"),
    )
    for task_id, object_name, label in (
        (71, "jobRefreshButton", "Refresh background jobs"),
        (72, "jobPauseButton", "Pause selected job"),
        (73, "jobResumeButton", "Resume selected job"),
        (74, "jobWakeButton", "Wake selected job"),
        (75, "jobCancelButton", "Cancel selected job"),
    ):
        _apply(
            applied,
            task_id,
            _named_child(window, QPushButton, object_name),
            _accessible(label),
        )

    sources = _named_child(window, QListWidget, "sourceList")
    source_details = _named_child(window, QPlainTextEdit, "sourceDetails")
    _apply(applied, 76, sources, _accessible("Imported local sources"))
    _apply(
        applied,
        77,
        source_details,
        _accessible("Source capture and retrieval details"),
    )
    for task_id, object_name, label in (
        (78, "fileImportButton", "Import local file"),
        (79, "fileProcessButton", "Process or retry selected source"),
        (80, "fileRefreshButton", "Refresh imported sources"),
    ):
        _apply(
            applied,
            task_id,
            _named_child(window, QPushButton, object_name),
            _accessible(label),
        )

    system = _named_child(window, QWidget, "systemWorkspace")
    _apply(
        applied,
        81,
        _named_child(window, QTabWidget, "systemOperationsTabs"),
        _accessible("System operations"),
    )
    _apply(applied, 82, system, _accessible("Local runtime status"))
    _apply(
        applied,
        83,
        _button_with_text(system, "Refresh"),
        _accessible("Refresh runtime status"),
    )
    _apply(applied, 84, _runtime_detail(system), _accessible("Runtime status detail"))
    _apply(
        applied,
        85,
        _named_child(window, QListWidget, "backupSnapshotList"),
        _accessible("Backup snapshots"),
    )
    _apply(
        applied,
        86,
        _named_child(window, QPlainTextEdit, "backupDetails"),
        _accessible("Backup verification and restore details"),
    )
    for task_id, object_name, label in (
        (87, "backupCreateButton", "Create verified backup"),
        (88, "backupVerifyButton", "Verify selected backup"),
        (89, "backupDeepVerifyButton", "Deep verify selected backup"),
        (90, "backupRestoreButton", "Restore selected backup to isolated location"),
        (91, "backupTargetsButton", "Show backup targets"),
        (92, "backupAddTargetButton", "Add backup target"),
    ):
        _apply(
            applied,
            task_id,
            _named_child(window, QPushButton, object_name),
            _accessible(label),
        )

    pallas = _named_child(window, QWidget, "pallasVisualPlaceholder")
    _apply(
        applied,
        93,
        pallas,
        _accessible(
            "PALLAS semantic field",
            "A local reactive visualization of the visible workspace context.",
        ),
    )
    _apply(
        applied,
        94,
        pallas,
        lambda widget: widget.setFocusPolicy(Qt.FocusPolicy.NoFocus),
    )
    _apply(
        applied,
        95,
        _named_child(window, QLineEdit, "commandPaletteQuery"),
        _accessible("Search commands"),
    )
    command_results = _named_child(window, QListWidget, "commandPaletteResults")
    _apply(applied, 96, command_results, _accessible("Available commands"))
    _apply(
        applied,
        97,
        _named_child(window, QPlainTextEdit, "helpText"),
        _accessible("pATHENA capabilities and keyboard help"),
    )
    _apply(
        applied,
        98,
        _named_child(window, QDialog, "helpDialog"),
        _accessible("pATHENA help"),
    )

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
            _named_child(window, QListWidget, "backupSnapshotList"),
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
