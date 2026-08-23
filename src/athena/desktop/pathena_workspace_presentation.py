"""Presentation-only refinements for pATHENA's functional workspaces.

The installed workspace modules own behaviour and controller/process wiring. This
module deliberately touches only visible copy, sizing and presentation metadata
so those workspaces can evolve independently of the pATHENA design language.
"""

from __future__ import annotations

import re

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QWidget,
)

_WORKSPACE_TITLES = frozenset(
    {
        "KNOWLEDGE / CANONICAL MEMORY",
        "EXHAUSTIVE LOCAL RESEARCH",
        "DURABLE JOB CONTROL",
        "LOCAL SOURCES / FILES",
        "LOCAL RUNTIME / SYSTEM",
    }
)

_LABEL_REPLACEMENTS = {
    "CURRENT CANONICAL KNOWLEDGE": "Canonical knowledge",
    "SELECTED KNOWLEDGE / PROVENANCE": "Details & provenance",
    "CURRENT CANONICAL CLAIMS": "Canonical claims",
    "SELECTED CLAIM / EVIDENCE / PROVENANCE": "Evidence & provenance",
    "PENDING CONTRADICTION DECISIONS": "Contradiction decisions",
    "DECISION / BOTH CLAIMS": "Compare claims",
    "REVIEW INBOX / CURRENT SESSION": "Review inbox",
    "DETAIL": "Status detail",
}

_BUTTON_REPLACEMENTS = {
    "OPEN SOURCE CHAT": "Open chat",
    "REFRESH CORE": "Refresh status",
    "REFRESH KNOWLEDGE": "Refresh",
    "REFRESH VIEW": "Refresh",
    "HISTORY": "History",
    "ACCEPT CONTRADICTION": "Confirm contradiction",
    "REJECT": "Reject",
    "START RESEARCH": "Start research",
    "REFRESH": "Refresh",
    "CANCEL SELECTED": "Cancel",
    "PAUSE": "Pause",
    "RESUME": "Resume",
    "WAKE": "Wake",
    "CANCEL": "Cancel",
    "IMPORT FILE": "Import file",
    "PROCESS / RETRY": "Process / retry",
    "REFRESH NOW": "Refresh",
}

_INTRO_REPLACEMENTS = {
    "knowledgeWorkspace": (
        "Browse durable knowledge, claims, evidence and decisions. Items promoted "
        "from conversations stay reviewable with their provenance."
    ),
    "researchWorkspace": (
        "Run durable local research across captured sources. Research continues in "
        "the background and can be inspected or cancelled here."
    ),
    "jobsWorkspace": (
        "Inspect and control pATHENA's persistent background work. Jobs, retries and "
        "checkpoints survive restarts."
    ),
    "filesWorkspace": (
        "Import local documents into the Raw Archive and prepare supported files for "
        "local retrieval."
    ),
    "systemWorkspace": (
        "Live local runtime status from pATHENA Core and the configured model provider."
    ),
}

_INTRO_PREFIXES = {
    "knowledgeWorkspace": "Browse canonical Knowledge across restarts",
    "researchWorkspace": (
        "Durable research runs against pATHENA's frozen local Source snapshot."
    ),
    "jobsWorkspace": "Canonical pATHENA background work.",
    "filesWorkspace": (
        "Import keeps the original bytes in pATHENA's immutable Raw Archive"
    ),
    "systemWorkspace": "Live operational state from pATHENA Core",
}

_PLACEHOLDERS = {
    "persistentKnowledgeDetails": (
        "Select a knowledge item to inspect its current revision and provenance."
    ),
    "persistentClaimDetails": (
        "Select a claim to inspect its statement, evidence and provenance."
    ),
    "semanticReviewDetails": (
        "Select a pending decision to compare the two claims and their evidence."
    ),
    "researchDetails": "Select a research run to inspect its scope and progress.",
    "jobDetails": "Select a job to inspect its current state and checkpoints.",
    "sourceDetails": "Select a file source to inspect import and processing status.",
}

_LIST_MINIMUM_WIDTHS = {
    "persistentKnowledgeList": 310,
    "persistentClaimList": 310,
    "semanticReviewList": 310,
    "researchJobList": 300,
    "durableJobList": 320,
    "sourceList": 320,
}

_KNOWLEDGE_STATE_REPLACEMENTS = {
    "IDLE": "Idle",
    "CORE UNAVAILABLE": "Core unavailable",
    "PREFLIGHT / PENDING": "Checking…",
    "REVIEW COMPLETE / READY": "Ready to add",
    "DECISION REQUIRED / CANONICAL MERGE": "Decision required",
    "BLOCKED / EXTRACTOR MERGE": "Needs review",
    "BLOCKED / REVIEW REQUIRED": "Needs review",
    "MERGE DECISION SAVED": "Saved",
    "DECISION REQUIRED": "Decision required",
}

_RUNTIME_PATTERN = re.compile(r"^CORE\s+(?P<state>\S+)\s+/\s+CHATS\s+(?P<count>\d+)$")
_SOURCE_PATTERN = re.compile(r"^SOURCE CHAT\s+\S+\s+/\s+MESSAGE\s+\S+$")


def _sync_knowledge_copy(window: QWidget) -> None:
    knowledge = window.findChild(QWidget, "knowledgeWorkspace")
    if knowledge is None:
        return

    state = knowledge.findChild(QLabel, "knowledgeReviewState")
    if state is not None:
        replacement = _KNOWLEDGE_STATE_REPLACEMENTS.get(state.text())
        if replacement is not None:
            state.setText(replacement)

    for label in knowledge.findChildren(QLabel):
        text = label.text()
        runtime_match = _RUNTIME_PATTERN.fullmatch(text)
        if runtime_match is not None:
            raw = text
            status = runtime_match.group("state").replace("_", " ").lower()
            count = int(runtime_match.group("count"))
            noun = "conversation" if count == 1 else "conversations"
            label.setToolTip(raw)
            label.setText(f"Core {status} · {count} {noun}")
            continue

        if text == "CORE  DISCONNECTED  /  CHATS  —":
            label.setToolTip(text)
            label.setText("Core unavailable")
            continue

        if _SOURCE_PATTERN.fullmatch(text) is not None:
            label.setToolTip(text)
            label.setText("From conversation · selected message")


def _sync_research_presentation(window: QWidget) -> None:
    research = window.findChild(QWidget, "researchWorkspace")
    if research is None:
        return
    cancel = research.findChild(QPushButton, "researchCancelButton")
    if cancel is not None:
        cancel.setVisible(cancel.isEnabled())


def _sync_jobs_presentation(window: QWidget) -> None:
    jobs = window.findChild(QWidget, "jobsWorkspace")
    if jobs is None:
        return

    for object_name in (
        "jobPauseButton",
        "jobResumeButton",
        "jobWakeButton",
        "jobCancelButton",
    ):
        button = jobs.findChild(QPushButton, object_name)
        if button is not None:
            button.setVisible(button.isEnabled())

    for label in jobs.findChildren(QLabel):
        text = label.text()
        if text == "SCHEDULER · EXTERNAL":
            label.setText("Scheduler external")
        elif text == "SCHEDULER · STOPPING":
            label.setText("Scheduler stopping…")
        elif text == "SCHEDULER · ACTIVE":
            label.setText("Scheduler active")
        elif text == "SCHEDULER · RECOVERY PENDING":
            label.setText("Scheduler reconnecting…")


def _sync_dynamic_workspace_copy(window: QWidget) -> None:
    """Normalize dynamic metadata and disclose only actionable controls."""
    _sync_knowledge_copy(window)
    _sync_research_presentation(window)
    _sync_jobs_presentation(window)


def _install_dynamic_copy_sync(window: QWidget) -> None:
    if window.property("pathenaWorkspaceCopySyncInstalled") is True:
        return
    window.setProperty("pathenaWorkspaceCopySyncInstalled", True)

    timer = QTimer(window)
    timer.setObjectName("pathenaWorkspaceCopySync")
    timer.setInterval(250)
    timer.timeout.connect(lambda: _sync_dynamic_workspace_copy(window))
    timer.start()
    _sync_dynamic_workspace_copy(window)


def _configure_research_presentation(window: QWidget) -> None:
    research = window.findChild(QWidget, "researchWorkspace")
    if research is None:
        return

    query_inputs = research.findChildren(QLineEdit)
    if query_inputs:
        query = query_inputs[0]
        query.setObjectName("researchQueryInput")
        query.setPlaceholderText("What do you want to investigate?")

    for button in research.findChildren(QPushButton):
        if button.text() == "Start research":
            button.setObjectName("researchStartButton")
        elif button.text() == "Cancel":
            button.setObjectName("researchCancelButton")
        elif button.text() == "Refresh":
            button.setObjectName("researchRefreshButton")


def _configure_jobs_presentation(window: QWidget) -> None:
    jobs = window.findChild(QWidget, "jobsWorkspace")
    if jobs is None:
        return

    object_names = {
        "Refresh": "jobRefreshButton",
        "Pause": "jobPauseButton",
        "Resume": "jobResumeButton",
        "Wake": "jobWakeButton",
        "Cancel": "jobCancelButton",
    }
    for button in jobs.findChildren(QPushButton):
        object_name = object_names.get(button.text())
        if object_name is not None:
            button.setObjectName(object_name)


def apply_workspace_presentation(window: QWidget) -> None:
    """Apply pATHENA's quiet presentation to already-installed real workspaces."""
    for label in window.findChildren(QLabel):
        text = label.text()
        if text in _WORKSPACE_TITLES:
            label.hide()
            continue
        replacement = _LABEL_REPLACEMENTS.get(text)
        if replacement is not None:
            label.setText(replacement)

    for workspace_name, replacement in _INTRO_REPLACEMENTS.items():
        workspace = window.findChild(QWidget, workspace_name)
        if workspace is None:
            continue
        prefix = _INTRO_PREFIXES[workspace_name]
        for label in workspace.findChildren(QLabel):
            if label.text().startswith(prefix):
                label.setText(replacement)
                break

    for button in window.findChildren(QPushButton):
        replacement = _BUTTON_REPLACEMENTS.get(button.text())
        if replacement is not None:
            button.setText(replacement)

    for object_name, placeholder in _PLACEHOLDERS.items():
        details = window.findChild(QPlainTextEdit, object_name)
        if details is not None:
            details.setPlaceholderText(placeholder)

    for object_name, width in _LIST_MINIMUM_WIDTHS.items():
        item_list = window.findChild(QListWidget, object_name)
        if item_list is not None:
            item_list.setMinimumWidth(width)

    knowledge_search = window.findChild(QLineEdit, "knowledgeSearchInput")
    if knowledge_search is not None:
        knowledge_search.setPlaceholderText("Search knowledge, claims, or decisions…")

    canonical_tabs = window.findChild(QTabWidget, "canonicalMemoryTabs")
    if canonical_tabs is not None and canonical_tabs.count() >= 4:
        canonical_tabs.setTabText(0, "Knowledge")
        canonical_tabs.setTabText(1, "Claims")
        canonical_tabs.setTabText(2, "Decisions")
        canonical_tabs.setTabText(3, "From chat")

    _configure_research_presentation(window)
    _configure_jobs_presentation(window)
    _install_dynamic_copy_sync(window)
