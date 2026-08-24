from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QScrollArea, QWidget

from athena.desktop.pathena_chat_scroll_stability_6600 import (
    ChatScrollStabilityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.chat_scroll = QScrollArea(self)
        self._chat_follow_tail = True
        self._chat_slider_active = False
        self._chat_scroll_programmatic = False


def test_reading_mode_tracks_manual_anchor() -> None:
    _app()
    window = _Window()
    controller = ChatScrollStabilityController(window)
    window._chat_follow_tail = False

    controller._value_changed(42)

    assert controller._anchor_value == 42
    assert window.chat_scroll.property("pathenaChatScrollMode") == "reading"


def test_tail_follow_clears_manual_anchor() -> None:
    _app()
    window = _Window()
    controller = ChatScrollStabilityController(window)
    controller._anchor_value = 37
    window._chat_follow_tail = True

    controller._value_changed(50)

    assert controller._anchor_value is None


def test_programmatic_scroll_does_not_replace_reading_anchor() -> None:
    _app()
    window = _Window()
    controller = ChatScrollStabilityController(window)
    controller._anchor_value = 31
    window._chat_follow_tail = False
    window._chat_scroll_programmatic = True

    controller._value_changed(90)

    assert controller._anchor_value == 31


def test_slider_drag_updates_anchor_without_forcing_tail() -> None:
    _app()
    window = _Window()
    controller = ChatScrollStabilityController(window)
    window._chat_follow_tail = False
    window._chat_slider_active = True

    controller._value_changed(18)

    assert controller._anchor_value == 18
    assert window._chat_follow_tail is False
