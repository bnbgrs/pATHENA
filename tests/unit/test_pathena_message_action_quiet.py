from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from athena.desktop.pathena_message_action_quiet_7000 import (
    MessageActionQuietController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.chat_messages_widget = QWidget(self)
        layout = QVBoxLayout(self.chat_messages_widget)
        self.message = QWidget(self.chat_messages_widget)
        self.message.setObjectName("chatMessage")
        message_layout = QVBoxLayout(self.message)
        self.button = QPushButton("REMEMBER", self.message)
        self.button.setObjectName("rememberMessageButton")
        message_layout.addWidget(self.button)
        layout.addWidget(self.message)


def test_inactive_enabled_action_is_quiet_not_hidden() -> None:
    _app()
    window = _Window()
    controller = MessageActionQuietController(window)

    controller._refresh(window.message)

    effect = controller._effects[window.button]
    assert effect.opacity() == pytest.approx(0.38)
    assert window.button.isVisible() is False or not window.button.isHidden()
    assert window.button.property("pathenaMessageActionLayoutPreserved") is True


def test_focused_message_action_receives_full_emphasis() -> None:
    app = _app()
    window = _Window()
    window.show()
    controller = MessageActionQuietController(window)
    window.button.setFocus()
    app.processEvents()

    controller._refresh(window.message)

    assert controller._effects[window.button].opacity() == pytest.approx(1.0)
    assert window.button.property("pathenaMessageActionEmphasis") == "active"


def test_disabled_inactive_action_stays_visible_but_more_quiet() -> None:
    _app()
    window = _Window()
    window.button.setEnabled(False)
    controller = MessageActionQuietController(window)

    controller._refresh(window.message)

    assert controller._effects[window.button].opacity() == pytest.approx(0.24)
    assert window.button.isHidden() is False


def test_unknown_message_button_gets_no_opacity_effect() -> None:
    _app()
    window = _Window()
    other = QPushButton("OTHER", window.message)
    other.setObjectName("unrelatedAction")
    controller = MessageActionQuietController(window)

    controller.sync()

    assert other not in controller._effects
