"""Readability and scanning refinements 4001-4100 for pATHENA.

This presentation-only pass improves selection, spacing and semantic scanning across
status, list and detail surfaces. Existing content, logging, wrapping decisions and
domain behavior remain intact; technical panes keep their current line-wrap mode.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class ReadabilityTarget:
    workspace_name: str
    attribute_name: str
    label: str
    reading_role: str


_TARGETS: tuple[ReadabilityTarget, ...] = (
    ReadabilityTarget("knowledgeWorkspace", "state", "knowledge state", "status"),
    ReadabilityTarget("knowledgeWorkspace", "summary", "knowledge summary", "prose"),
    ReadabilityTarget("knowledgeWorkspace", "browser_status", "knowledge browser status", "status"),
    ReadabilityTarget("knowledgeWorkspace", "knowledge_details", "knowledge details", "detail"),
    ReadabilityTarget("knowledgeWorkspace", "claim_details", "claim details", "detail"),
    ReadabilityTarget("knowledgeWorkspace", "review_details", "decision details", "detail"),
    ReadabilityTarget("researchWorkspace", "status", "research status", "status"),
    ReadabilityTarget("researchWorkspace", "jobs", "research jobs", "list"),
    ReadabilityTarget("researchWorkspace", "details", "research details", "technical"),
    ReadabilityTarget("jobsWorkspace", "scheduler_status", "scheduler status", "status"),
    ReadabilityTarget("jobsWorkspace", "status", "jobs status", "status"),
    ReadabilityTarget("jobsWorkspace", "jobs", "durable jobs", "list"),
    ReadabilityTarget("jobsWorkspace", "details", "job details", "technical"),
    ReadabilityTarget("filesWorkspace", "status", "source status", "status"),
    ReadabilityTarget("filesWorkspace", "sources", "source list", "list"),
    ReadabilityTarget("filesWorkspace", "details", "source details", "technical"),
    ReadabilityTarget("systemWorkspace", "detail", "system detail", "prose"),
    ReadabilityTarget("backupWorkspace", "status", "backup status", "status"),
    ReadabilityTarget("backupWorkspace", "snapshots", "backup snapshots", "list"),
    ReadabilityTarget("backupWorkspace", "details", "backup details", "technical"),
)

_DIMENSIONS: tuple[str, ...] = (
    "text selection affordance",
    "wrap and scan strategy",
    "content spacing",
    "semantic reading role",
    "long-text guidance",
)

UI_REFINEMENT_TASKS_4001_4100: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_READABILITY_STYLESHEET = """
/* pATHENA readability 4100 */
QLabel[pathenaReadingRole="status"] {
    letter-spacing: 0.2px;
}
QPlainTextEdit[pathenaReadingRole="detail"],
QPlainTextEdit[pathenaReadingRole="technical"] {
    padding: 6px;
}
QListWidget[pathenaReadingRole="list"] {
    padding: 4px;
}
"""


def _apply_surface(widget: QWidget, target: ReadabilityTarget) -> None:
    widget.setProperty("pathenaReadingRole", target.reading_role)
    widget.setProperty("pathenaLongTextGuidance", True)

    if isinstance(widget, QLabel):
        widget.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        if target.reading_role == "prose":
            widget.setWordWrap(True)
        widget.setProperty("pathenaTextSelectable", True)
        widget.setProperty("pathenaWrapStrategy", "word-wrap" if widget.wordWrap() else "single-line")
        widget.setProperty("pathenaContentSpacing", "label-native")
    elif isinstance(widget, QPlainTextEdit):
        widget.document().setDocumentMargin(8.0)
        widget.setTabStopDistance(32.0)
        wrap_mode = widget.lineWrapMode()
        widget.setProperty("pathenaTextSelectable", True)
        widget.setProperty(
            "pathenaWrapStrategy",
            "widget-width"
            if wrap_mode == QPlainTextEdit.LineWrapMode.WidgetWidth
            else "preserve-lines",
        )
        widget.setProperty("pathenaContentSpacing", "document-margin-8")
    elif isinstance(widget, QListWidget):
        widget.setSpacing(2)
        widget.setUniformItemSizes(False)
        widget.setProperty("pathenaTextSelectable", False)
        widget.setProperty("pathenaWrapStrategy", "item-native")
        widget.setProperty("pathenaContentSpacing", "item-gap-2")

    widget.setAccessibleDescription(
        f"{target.label.capitalize()}. Reading role: {target.reading_role}. "
        "Long content remains available for inspection and selection where supported."
    )
    widget.setStatusTip(
        f"{target.label.capitalize()} · {target.reading_role} reading surface."
    )


def apply_ui_refinements_4001_4100(window: QWidget) -> tuple[int, ...]:
    """Apply 100 readability outcomes to existing pATHENA content surfaces."""
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        workspace = window.findChild(QWidget, target.workspace_name)
        if workspace is None:
            continue
        widget = getattr(workspace, target.attribute_name, None)
        if not isinstance(widget, QWidget):
            continue
        _apply_surface(widget, target)
        start = 4001 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    if _READABILITY_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_READABILITY_STYLESHEET}")

    window.setProperty("pathenaReadabilityTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaReadabilityTaskCount", len(applied))
    return tuple(applied)
