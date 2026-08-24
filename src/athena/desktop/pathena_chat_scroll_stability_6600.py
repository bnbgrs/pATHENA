"""Preserve deliberate chat reading position across asynchronous geometry changes.

The chat shell already owns tail-follow intent and slider interaction. This
presentation-only controller only acts when the user has deliberately left the tail.
It remembers the current vertical value and reasserts it when wrapped message geometry
or appended non-tail content changes the scroll range. Tail following, drag behavior,
message rendering and domain state remain owned by the existing chat window.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QScrollArea, QScrollBar, QWidget


class ChatScrollStabilityController(QObject):
    """Keep non-tail reading position stable while the chat document settles."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        scroll = getattr(window, "chat_scroll", None)
        self.scroll = scroll if isinstance(scroll, QScrollArea) else None
        self._anchor_value: int | None = None
        self._restoring = False
        self._last_maximum = 0

        if self.scroll is None:
            return

        bar = self.scroll.verticalScrollBar()
        self._last_maximum = bar.maximum()
        bar.valueChanged.connect(self._value_changed)
        bar.rangeChanged.connect(self._range_changed)
        self.scroll.setProperty("pathenaChatScrollStabilityManaged", True)
        self._sync_metadata()

    def _value_changed(self, value: int) -> None:
        if self._restoring or self._programmatic_scroll_active():
            return
        if self._slider_active():
            self._anchor_value = value
            self._sync_metadata()
            return
        if self._follow_tail():
            self._anchor_value = None
        else:
            self._anchor_value = value
        self._sync_metadata()

    def _range_changed(self, _minimum: int, maximum: int) -> None:
        previous_maximum = self._last_maximum
        self._last_maximum = maximum
        if self._follow_tail() or self._slider_active():
            self._anchor_value = None
            self._sync_metadata()
            return
        if self._anchor_value is None:
            bar = self._bar()
            if bar is not None:
                self._anchor_value = bar.value()
        if maximum != previous_maximum:
            QTimer.singleShot(0, self._restore_anchor)
        self._sync_metadata()

    def _restore_anchor(self) -> None:
        if self._follow_tail() or self._slider_active() or self._anchor_value is None:
            return
        bar = self._bar()
        if bar is None:
            return
        target = max(bar.minimum(), min(self._anchor_value, bar.maximum()))
        if bar.value() == target:
            return
        self._restoring = True
        try:
            bar.setValue(target)
        finally:
            self._restoring = False
        if self.scroll is not None:
            self.scroll.setProperty("pathenaChatScrollAnchorRestored", True)
        self._sync_metadata()

    def _sync_metadata(self) -> None:
        if self.scroll is None:
            return
        reading = not self._follow_tail()
        self.scroll.setProperty("pathenaChatReadingPositionProtected", reading)
        self.scroll.setProperty(
            "pathenaChatScrollAnchorValue",
            self._anchor_value if self._anchor_value is not None else -1,
        )
        self.scroll.setProperty(
            "pathenaChatScrollMode",
            "reading" if reading else "follow-tail",
        )
        self.scroll.setAccessibleDescription(
            "Conversation document. New content follows the tail while you remain at "
            "the bottom; deliberate reading position is preserved after scrolling up."
        )

    def _bar(self) -> QScrollBar | None:
        return self.scroll.verticalScrollBar() if self.scroll is not None else None

    def _follow_tail(self) -> bool:
        return bool(getattr(self.window, "_chat_follow_tail", True))

    def _slider_active(self) -> bool:
        return bool(getattr(self.window, "_chat_slider_active", False))

    def _programmatic_scroll_active(self) -> bool:
        return bool(getattr(self.window, "_chat_scroll_programmatic", False))


def install_chat_scroll_stability(window: QWidget) -> ChatScrollStabilityController:
    """Install non-tail chat scroll anchoring on the existing conversation scroll."""
    controller = ChatScrollStabilityController(window)
    window.setProperty("pathenaChatScrollStabilityController", controller)
    window.setProperty("pathenaChatScrollStabilityManaged", True)
    return controller
