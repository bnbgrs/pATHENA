"""Screenreader-facing semantic state synchronization for pATHENA.

Existing UI layers already expose pathenaUiState, selection identity and detailed
status text. This presentation-only controller keeps accessible names/descriptions in
sync with those real states and selections. It does not announce fabricated progress,
register shortcuts, change focus, or invoke domain actions.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class AccessibleStateTarget:
    object_name: str
    label: str


_TARGETS: tuple[AccessibleStateTarget, ...] = (
    AccessibleStateTarget("knowledgeReviewState", "Knowledge review"),
    AccessibleStateTarget("persistentKnowledgeList", "Knowledge list"),
    AccessibleStateTarget("persistentKnowledgeDetails", "Knowledge details"),
    AccessibleStateTarget("persistentClaimList", "Claim list"),
    AccessibleStateTarget("persistentClaimDetails", "Claim details"),
    AccessibleStateTarget("semanticReviewList", "Contradiction decisions"),
    AccessibleStateTarget("semanticReviewDetails", "Contradiction details"),
    AccessibleStateTarget("researchStatus", "Research status"),
    AccessibleStateTarget("researchJobList", "Research jobs"),
    AccessibleStateTarget("researchDetails", "Research details"),
    AccessibleStateTarget("jobsStatus", "Durable jobs status"),
    AccessibleStateTarget("schedulerStatus", "Scheduler status"),
    AccessibleStateTarget("durableJobList", "Durable jobs"),
    AccessibleStateTarget("jobDetails", "Job details"),
    AccessibleStateTarget("sourceStatus", "Source status"),
    AccessibleStateTarget("sourceList", "Sources"),
    AccessibleStateTarget("sourceDetails", "Source details"),
    AccessibleStateTarget("systemDetail", "System runtime"),
    AccessibleStateTarget("backupSnapshotList", "Backup snapshots"),
    AccessibleStateTarget("backupDetails", "Backup details"),
)

_STATE_WORDS: dict[str, str] = {
    "idle": "ready",
    "busy": "working",
    "success": "complete",
    "error": "needs attention",
    "empty": "empty",
}

_DIMENSIONS: tuple[str, ...] = (
    "accessible state name",
    "accessible state description",
    "selection identity synchronization",
    "state transition synchronization",
    "assistive diagnostic metadata",
)

UI_REFINEMENT_TASKS_5501_5600: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class AccessibleStateSyncController(QObject):
    """Keep assistive descriptions aligned with current semantic UI state."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._labels: dict[QWidget, str] = {}
        self._last_signature: dict[QWidget, tuple[str, str, str, str]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, widget: QWidget, label: str) -> None:
        self._labels[widget] = label
        widget.installEventFilter(self)
        if isinstance(widget, QListWidget):
            widget.currentItemChanged.connect(self._schedule_sync)
        self._sync_one(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget) and isinstance(
            event, QDynamicPropertyChangeEvent
        ):
            property_name = bytes(event.propertyName().data())
            if property_name in {
                b"pathenaUiState",
                b"pathenaSelectedDetailIdentity",
                b"pathenaResultScopeText",
                b"pathenaBackupListScope",
                b"pathenaDenseListAccessibleScope",
            }:
                self._schedule_sync()
        return super().eventFilter(watched, event)

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        for widget in self._labels:
            self._sync_one(widget)

    def _sync_one(self, widget: QWidget) -> None:
        label = self._labels[widget]
        state = str(widget.property("pathenaUiState") or "idle")
        identity = self._selection_identity(widget)
        detail = self._visible_detail(widget)
        list_scope = self._list_scope(widget)
        signature = (state, identity, detail, list_scope)
        if self._last_signature.get(widget) == signature:
            return
        self._last_signature[widget] = signature

        state_word = _STATE_WORDS.get(state, state.replace("_", " "))
        name = f"{label} — {state_word}"
        if identity:
            name = f"{name} — selected {identity}"
        widget.setAccessibleName(name)

        if list_scope:
            parts = [list_scope, f"State: {state_word}."]
        else:
            parts = [f"{label} is {state_word}."]
            if identity:
                parts.append(f"Selected item: {identity}.")
        if detail:
            parts.append(f"Visible detail: {detail}.")
        widget.setAccessibleDescription(" ".join(parts))

        widget.setProperty("pathenaAccessibleUiState", state)
        widget.setProperty("pathenaAccessibleSelectionIdentity", identity)
        widget.setProperty("pathenaAccessibleStateSynchronized", True)
        count = int(widget.property("pathenaAccessibleSyncCount") or 0) + 1
        widget.setProperty("pathenaAccessibleSyncCount", count)

    @staticmethod
    def _list_scope(widget: QWidget) -> str:
        if not isinstance(widget, QListWidget):
            return ""
        for property_name in (
            "pathenaBackupListScope",
            "pathenaResultScopeText",
            "pathenaDenseListAccessibleScope",
        ):
            value = widget.property(property_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    @staticmethod
    def _selection_identity(widget: QWidget) -> str:
        if not isinstance(widget, QListWidget):
            value = widget.property("pathenaSelectedDetailIdentity")
            return str(value) if value else ""
        item = widget.currentItem()
        if item is None:
            return ""
        identity = item.data(Qt.ItemDataRole.UserRole)
        value = identity if identity is not None else item.text()
        return " ".join(str(value).split())[:96]

    @staticmethod
    def _visible_detail(widget: QWidget) -> str:
        value = ""
        if isinstance(widget, QLabel):
            value = widget.text()
        elif isinstance(widget, QPlainTextEdit):
            value = widget.toPlainText()
        normalized = " ".join(value.split())
        return normalized[:160]


def apply_ui_refinements_5501_5600(window: QWidget) -> tuple[int, ...]:
    """Install synchronized assistive state metadata on existing UI surfaces."""
    controller = AccessibleStateSyncController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        controller.register(widget, target.label)
        start = 5501 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaAccessibleStateSyncController", controller)
    window.setProperty("pathenaAccessibleStateSyncManaged", True)
    return tuple(applied)
