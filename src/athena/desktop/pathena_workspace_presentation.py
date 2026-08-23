"""Presentation-only refinements for pATHENA's functional workspaces.

The installed workspace modules own behaviour and controller/process wiring. This
module deliberately touches only visible copy, sizing and presentation metadata
so those workspaces can evolve independently of the pATHENA design language.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QPushButton, QWidget

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
    "REVIEW INBOX / CURRENT SESSION": "Review inbox",
    "DETAIL": "Status detail",
}

_BUTTON_REPLACEMENTS = {
    "OPEN SOURCE CHAT": "Open source chat",
    "REFRESH CORE": "Refresh status",
    "REFRESH KNOWLEDGE": "Refresh",
    "HISTORY": "History",
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
        "Browse durable knowledge and review what is promoted from conversations. "
        "Revisions and provenance remain inspectable."
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
    "researchWorkspace": "Durable research runs against pATHENA's frozen local Source snapshot.",
    "jobsWorkspace": "Canonical pATHENA background work.",
    "filesWorkspace": "Import keeps the original bytes in pATHENA's immutable Raw Archive",
    "systemWorkspace": "Live operational state from pATHENA Core",
}

_PLACEHOLDERS = {
    "persistentKnowledgeDetails": (
        "Select a knowledge item to inspect its current revision and provenance."
    ),
    "researchDetails": "Select a research run to inspect its scope and progress.",
    "jobDetails": "Select a job to inspect its current state and checkpoints.",
    "sourceDetails": "Select a file source to inspect import and processing status.",
}

_LIST_MINIMUM_WIDTHS = {
    "persistentKnowledgeList": 320,
    "researchJobList": 300,
    "durableJobList": 320,
    "sourceList": 320,
}


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
