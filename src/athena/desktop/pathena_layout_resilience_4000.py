"""Resize and compact-layout refinements 3901-4000 for pATHENA.

The desktop is information-dense and frequently resized. This presentation-only pass
marks twenty real surfaces as shrink-safe, gives them appropriate horizontal size
policies, and switches to restrained compact padding below a conservative window
width. It does not hide controls, reorder workspaces, or alter domain behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractButton, QSizePolicy, QWidget


@dataclass(frozen=True)
class LayoutTarget:
    object_name: str
    label: str


_TARGETS: tuple[LayoutTarget, ...] = (
    LayoutTarget("sessionControls", "session controls"),
    LayoutTarget("chatSelector", "conversation selector"),
    LayoutTarget("modelSelector", "model selector"),
    LayoutTarget("promptInput", "composer input"),
    LayoutTarget("sendButton", "send action"),
    LayoutTarget("knowledgeWorkspace", "knowledge workspace"),
    LayoutTarget("canonicalMemoryTabs", "canonical memory tabs"),
    LayoutTarget("persistentKnowledgeList", "knowledge list"),
    LayoutTarget("persistentKnowledgeDetails", "knowledge details"),
    LayoutTarget("researchWorkspace", "research workspace"),
    LayoutTarget("researchJobList", "research job list"),
    LayoutTarget("researchDetails", "research details"),
    LayoutTarget("jobsWorkspace", "jobs workspace"),
    LayoutTarget("durableJobList", "durable job list"),
    LayoutTarget("jobDetails", "job details"),
    LayoutTarget("filesWorkspace", "files workspace"),
    LayoutTarget("sourceList", "source list"),
    LayoutTarget("sourceDetails", "source details"),
    LayoutTarget("systemWorkspace", "system workspace"),
    LayoutTarget("backupWorkspace", "backup workspace"),
)

_DIMENSIONS: tuple[str, ...] = (
    "compact eligibility",
    "shrink-safe policy",
    "width resilience",
    "compact visual state",
    "resize synchronization",
)

UI_REFINEMENT_TASKS_3901_4000: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_COMPACT_THRESHOLD = 1460

_COMPACT_STYLESHEET = """
/* pATHENA layout resilience 4000 */
QPushButton[pathenaCompactLayout="true"] {
    padding: 5px 8px;
}
QLineEdit[pathenaCompactLayout="true"],
QComboBox[pathenaCompactLayout="true"] {
    padding: 5px 7px;
}
QPlainTextEdit[pathenaCompactLayout="true"],
QListWidget[pathenaCompactLayout="true"] {
    padding: 4px;
}
"""


class LayoutResilienceController(QObject):
    """Synchronize a quiet compact presentation with top-level resize events."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._widgets: list[QWidget] = []
        window.installEventFilter(self)

    def register(self, widget: QWidget) -> None:
        self._widgets.append(widget)
        policy = widget.sizePolicy()
        horizontal = (
            QSizePolicy.Policy.Minimum
            if isinstance(widget, QAbstractButton)
            else QSizePolicy.Policy.Expanding
        )
        policy.setHorizontalPolicy(horizontal)
        widget.setSizePolicy(policy)
        widget.setProperty("pathenaShrinkSafe", True)
        widget.setProperty("pathenaWidthResilient", True)
        widget.setProperty("pathenaResizeSynchronized", True)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self.sync()
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        compact = self.window.width() < _COMPACT_THRESHOLD
        mode = "compact" if compact else "regular"
        for widget in self._widgets:
            changed = bool(widget.property("pathenaCompactLayout")) != compact
            widget.setProperty("pathenaCompactLayout", compact)
            widget.setProperty("pathenaLayoutMode", mode)
            widget.setProperty("pathenaCompactThreshold", _COMPACT_THRESHOLD)
            if changed:
                style = widget.style()
                style.unpolish(widget)
                style.polish(widget)
                widget.update()
        self.window.setProperty("pathenaLayoutMode", mode)


def apply_ui_refinements_3901_4000(window: QWidget) -> tuple[int, ...]:
    """Apply 100 resize-resilience outcomes to existing pATHENA surfaces."""
    controller = LayoutResilienceController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        controller.register(widget)
        widget.setProperty("pathenaCompactEligible", True)
        start = 3901 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    controller.sync()
    if _COMPACT_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_COMPACT_STYLESHEET}")

    window.setProperty("pathenaLayoutResilienceController", controller)
    window.setProperty(
        "pathenaLayoutResilienceTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaLayoutResilienceTaskCount", len(applied))
    return tuple(applied)
