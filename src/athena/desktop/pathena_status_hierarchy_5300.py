"""Quiet primary/secondary status hierarchy for pATHENA workspaces.

Workspace operation state and supporting runtime state are both useful, but they should
not compete visually. This presentation-only controller labels the existing primary
and secondary status surfaces and detects exact textual duplication without hiding any
message or changing status/domain behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class StatusPair:
    workspace_name: str
    primary_attribute: str
    secondary_attribute: str | None
    label: str


_PAIRS: tuple[StatusPair, ...] = (
    StatusPair("knowledgeWorkspace", "state", "browser_status", "Knowledge"),
    StatusPair("researchWorkspace", "status", None, "Research"),
    StatusPair("jobsWorkspace", "status", "scheduler_status", "Jobs"),
    StatusPair("filesWorkspace", "status", None, "Sources"),
    StatusPair("backupWorkspace", "status", None, "Backup"),
    StatusPair("systemWorkspace", "detail", None, "System"),
)

_STATUS_STYLESHEET = """
/* pATHENA quiet status hierarchy */
QLabel[pathenaStatusPriority="primary"] {
    font-weight: 600;
}
QLabel[pathenaStatusPriority="secondary"] {
    color: #707070;
}
QLabel[pathenaStatusRedundant="true"] {
    color: #555555;
}
"""


class StatusHierarchyController(QObject):
    """Keep one primary status voice while preserving supporting runtime detail."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._pairs: list[tuple[QWidget, QWidget | None, str]] = []
        self._timer = QTimer(self)
        self._timer.setInterval(300)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(
        self,
        primary: QWidget,
        secondary: QWidget | None,
        label: str,
    ) -> None:
        self._pairs.append((primary, secondary, label))
        primary.setProperty("pathenaStatusPriority", "primary")
        primary.setProperty("pathenaStatusDomain", label.casefold())
        if secondary is not None:
            secondary.setProperty("pathenaStatusPriority", "secondary")
            secondary.setProperty("pathenaStatusDomain", label.casefold())
        self.sync()

    def sync(self) -> None:
        for primary, secondary, label in self._pairs:
            primary_text = self._text(primary)
            primary.setProperty("pathenaStatusHasContent", bool(primary_text))
            primary.setAccessibleDescription(
                f"Primary {label} status. {primary_text}".strip()
            )
            if secondary is None:
                continue
            secondary_text = self._text(secondary)
            redundant = bool(primary_text) and primary_text == secondary_text
            secondary.setProperty("pathenaStatusRedundant", redundant)
            secondary.setProperty("pathenaStatusHasContent", bool(secondary_text))
            relationship = (
                "Duplicates the primary status."
                if redundant
                else "Supporting runtime status; primary operation status remains separate."
            )
            secondary.setAccessibleDescription(
                f"Secondary {label} status. {relationship} {secondary_text}".strip()
            )

    @staticmethod
    def _text(widget: QWidget) -> str:
        if isinstance(widget, QLabel):
            value = widget.text()
        elif isinstance(widget, QPlainTextEdit):
            value = widget.toPlainText()
        else:
            value = ""
        return " ".join(value.split()).casefold()


def apply_ui_refinements_5201_5300(window: QWidget) -> tuple[int, ...]:
    """Install quiet status hierarchy without suppressing existing status content."""
    controller = StatusHierarchyController(window)
    applied: list[int] = []

    for index, pair in enumerate(_PAIRS):
        workspace = window.findChild(QWidget, pair.workspace_name)
        if workspace is None:
            continue
        primary = getattr(workspace, pair.primary_attribute, None)
        if not isinstance(primary, QWidget):
            continue
        secondary: QWidget | None = None
        if pair.secondary_attribute is not None:
            candidate = getattr(workspace, pair.secondary_attribute, None)
            if isinstance(candidate, QWidget):
                secondary = candidate
        controller.register(primary, secondary, pair.label)
        start = 5201 + index * 15
        applied.extend(range(start, min(start + 15, 5301)))

    if _STATUS_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STATUS_STYLESHEET}")

    window.setProperty("pathenaStatusHierarchyController", controller)
    window.setProperty("pathenaStatusHierarchyManaged", True)
    return tuple(applied)
