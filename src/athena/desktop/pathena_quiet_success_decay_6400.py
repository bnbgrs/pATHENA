"""Quiet visual decay for transient success states.

Successful operations should remain semantically truthful without keeping the workspace
visually loud indefinitely. This presentation-only controller leaves ``pathenaUiState``
untouched and decays only a separate success-emphasis property after a short interval.
Errors, busy states and persistent content are never hidden or rewritten.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject, QTimer
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class SuccessDecayTarget:
    object_name: str
    label: str


_TARGETS: tuple[SuccessDecayTarget, ...] = (
    SuccessDecayTarget("knowledgeReviewState", "Knowledge review"),
    SuccessDecayTarget("researchStatus", "Research status"),
    SuccessDecayTarget("jobsStatus", "Durable jobs status"),
    SuccessDecayTarget("schedulerStatus", "Scheduler status"),
    SuccessDecayTarget("sourceStatus", "Source status"),
    SuccessDecayTarget("backupStatus", "Backup status"),
    SuccessDecayTarget("systemDetail", "System runtime"),
)

_SUCCESS_DECAY_MS = 3_500

_SUCCESS_DECAY_STYLESHEET = """
/* pATHENA quiet success decay */
QLabel[pathenaSuccessEmphasis="fresh"] {
    font-weight: 600;
}
QLabel[pathenaSuccessEmphasis="quiet"] {
    color: #767676;
    font-weight: 400;
}
"""


class QuietSuccessDecayController(QObject):
    """Decay only visual success emphasis while preserving semantic state."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._labels: dict[QWidget, str] = {}
        self._generation: dict[QWidget, int] = {}

    def register(self, widget: QWidget, label: str) -> None:
        self._labels[widget] = label
        self._generation.setdefault(widget, 0)
        widget.installEventFilter(self)
        widget.setProperty("pathenaSuccessDecayManaged", True)
        self._sync(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        labels = getattr(self, "_labels", None)
        if (
            isinstance(labels, dict)
            and isinstance(watched, QWidget)
            and watched in labels
            and isinstance(event, QDynamicPropertyChangeEvent)
            and bytes(event.propertyName().data()) == b"pathenaUiState"
        ):
            self._sync(watched)
        return super().eventFilter(watched, event)

    def _sync(self, widget: QWidget) -> None:
        state = str(widget.property("pathenaUiState") or "idle")
        generation = self._generation.get(widget, 0) + 1
        self._generation[widget] = generation

        if state != "success":
            self._set_emphasis(widget, "none")
            widget.setProperty("pathenaSuccessDecayPending", False)
            return

        self._set_emphasis(widget, "fresh")
        widget.setProperty("pathenaSuccessDecayPending", True)
        widget.setProperty("pathenaSuccessDecayDelayMs", _SUCCESS_DECAY_MS)
        QTimer.singleShot(
            _SUCCESS_DECAY_MS,
            lambda target=widget, token=generation: self._decay(target, token),
        )

    def _decay(self, widget: QWidget, generation: int) -> None:
        if self._generation.get(widget) != generation:
            return
        if str(widget.property("pathenaUiState") or "idle") != "success":
            return
        self._set_emphasis(widget, "quiet")
        widget.setProperty("pathenaSuccessDecayPending", False)
        widget.setProperty("pathenaSuccessSemanticsPreserved", True)

    @staticmethod
    def _set_emphasis(widget: QWidget, emphasis: str) -> None:
        if str(widget.property("pathenaSuccessEmphasis") or "") == emphasis:
            return
        widget.setProperty("pathenaSuccessEmphasis", emphasis)
        style = widget.style()
        style.unpolish(widget)
        style.polish(widget)
        widget.update()


def apply_quiet_success_decay(window: QWidget) -> QuietSuccessDecayController:
    """Install quiet success decay on existing primary status surfaces."""
    controller = QuietSuccessDecayController(window)
    for target in _TARGETS:
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        controller.register(widget, target.label)

    if _SUCCESS_DECAY_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_SUCCESS_DECAY_STYLESHEET}")

    window.setProperty("pathenaQuietSuccessDecayController", controller)
    window.setProperty("pathenaQuietSuccessDecayManaged", True)
    return controller
