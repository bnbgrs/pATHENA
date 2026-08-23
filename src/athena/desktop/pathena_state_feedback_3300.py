"""Semantic state-feedback refinements 3201-3300 for pATHENA.

This pass builds on the existing idle/busy/success/error/empty state language. It
turns those real workspace states into consistent assistive descriptions, status
hints, live-state metadata, restrained visual roles and transition metadata. It does
not create or alter any domain action, process transition, persistence path or API.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class FeedbackTarget:
    object_name: str
    label: str


_TARGETS: tuple[FeedbackTarget, ...] = (
    FeedbackTarget("knowledgeReviewState", "knowledge review state"),
    FeedbackTarget("canonicalMemoryTabs", "canonical memory tabs"),
    FeedbackTarget("persistentKnowledgeList", "canonical knowledge list"),
    FeedbackTarget("persistentKnowledgeDetails", "canonical knowledge details"),
    FeedbackTarget("persistentClaimList", "canonical claim list"),
    FeedbackTarget("persistentClaimDetails", "canonical claim details"),
    FeedbackTarget("semanticReviewList", "semantic decision list"),
    FeedbackTarget("semanticReviewDetails", "semantic decision details"),
    FeedbackTarget("researchStatus", "research status"),
    FeedbackTarget("researchJobList", "research job list"),
    FeedbackTarget("researchDetails", "research details"),
    FeedbackTarget("jobsStatus", "durable jobs status"),
    FeedbackTarget("schedulerStatus", "scheduler status"),
    FeedbackTarget("durableJobList", "durable job list"),
    FeedbackTarget("jobDetails", "durable job details"),
    FeedbackTarget("sourceStatus", "source status"),
    FeedbackTarget("sourceList", "source list"),
    FeedbackTarget("sourceDetails", "source details"),
    FeedbackTarget("systemDetail", "system runtime detail"),
    FeedbackTarget("backupSnapshotList", "backup snapshot list"),
)

_DIMENSIONS: tuple[str, ...] = (
    "state explanation",
    "status hint",
    "live-state metadata",
    "quiet visual role",
    "transition metadata",
)

UI_REFINEMENT_TASKS_3201_3300: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_STATE_COPY: dict[str, tuple[str, str]] = {
    "idle": ("ready", "Ready for interaction."),
    "busy": (
        "working",
        "Work is in progress. Related actions may be temporarily unavailable.",
    ),
    "success": ("complete", "The latest operation completed successfully."),
    "error": (
        "attention",
        "The latest operation needs attention. Review the visible detail.",
    ),
    "empty": ("empty", "No content is available for this view yet."),
}

_FEEDBACK_STYLESHEET = """
/* pATHENA semantic feedback 3300 */
QWidget[pathenaFeedbackRole="working"] {
    background: transparent;
}
QWidget[pathenaFeedbackRole="complete"] {
    background: transparent;
}
QWidget[pathenaFeedbackRole="attention"] {
    background: transparent;
}
QWidget[pathenaFeedbackRole="empty"] {
    background: transparent;
}
"""


class StateFeedbackController(QObject):
    """Mirror existing semantic state changes into consistent feedback metadata."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._labels: dict[QWidget, str] = {}
        self._previous_state: dict[QWidget, str] = {}
        self._transition_count: dict[QWidget, int] = {}

    def register(self, widget: QWidget, label: str) -> None:
        self._labels[widget] = label
        widget.installEventFilter(self)
        self._sync(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            isinstance(watched, QWidget)
            and isinstance(event, QDynamicPropertyChangeEvent)
            and bytes(event.propertyName()) == b"pathenaUiState"
        ):
            self._sync(watched)
        return super().eventFilter(watched, event)

    def _sync(self, widget: QWidget) -> None:
        state_value = widget.property("pathenaUiState")
        state = str(state_value) if state_value is not None else "idle"
        role, explanation = _STATE_COPY.get(state, _STATE_COPY["idle"])
        label = self._labels.get(widget, widget.objectName() or "workspace surface")
        previous = self._previous_state.get(widget)

        widget.setAccessibleDescription(f"{label.capitalize()}: {explanation}")
        widget.setProperty("pathenaFeedbackExplanation", explanation)

        widget.setStatusTip(f"{label.capitalize()} — {explanation}")
        widget.setProperty("pathenaFeedbackStatusHint", True)

        widget.setProperty("pathenaLiveUiState", state)
        widget.setProperty("pathenaStateIsBusy", state == "busy")
        widget.setProperty("pathenaStateNeedsAttention", state == "error")

        widget.setProperty("pathenaFeedbackRole", role)
        widget.setProperty("pathenaQuietStateFeedback", True)

        if previous != state:
            count = self._transition_count.get(widget, 0) + 1
            self._transition_count[widget] = count
            widget.setProperty("pathenaPreviousUiState", previous or "")
            widget.setProperty("pathenaStateTransitionCount", count)
            self._previous_state[widget] = state

        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()


def apply_ui_refinements_3201_3300(window: QWidget) -> tuple[int, ...]:
    """Apply 100 feedback outcomes to the existing semantic state surfaces."""
    controller = StateFeedbackController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        start = 3201 + index * len(_DIMENSIONS)
        controller.register(widget, target.label)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    if _FEEDBACK_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_FEEDBACK_STYLESHEET}")

    window.setProperty("pathenaStateFeedbackController", controller)
    window.setProperty(
        "pathenaStateFeedbackTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaStateFeedbackTaskCount", len(applied))
    return tuple(applied)
