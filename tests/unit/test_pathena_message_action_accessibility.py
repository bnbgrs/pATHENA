from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.desktop.pathena_message_action_accessibility_6900 import (
    MessageActionAccessibilityController,
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


def test_existing_message_action_becomes_keyboard_focusable() -> None:
    _app()
    window = _Window()
    button = QPushButton("REMEMBER", window.chat_messages_widget)
    button.setObjectName("rememberMessageButton")
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    controller = MessageActionAccessibilityController(window)
    controller.sync()

    assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert button.accessibleName() == "Remember message"
    assert button.property("pathenaMessageActionKeyboard") is True


def test_accessibility_layer_does_not_change_enablement() -> None:
    _app()
    window = _Window()
    button = QPushButton("ADD", window.chat_messages_widget)
    button.setObjectName("addKnowledgeButton")
    button.setEnabled(False)

    controller = MessageActionAccessibilityController(window)
    controller.sync()

    assert button.isEnabled() is False
    assert button.accessibleName() == "Add message to Knowledge"


def test_copy_action_gets_explicit_clipboard_purpose() -> None:
    _app()
    window = _Window()
    button = QPushButton("COPY", window.chat_messages_widget)
    button.setObjectName("copyMessageButton")

    controller = MessageActionAccessibilityController(window)
    controller.sync()

    assert "clipboard" in button.accessibleDescription().casefold()
    assert button.property("pathenaMessageActionPurpose") == "copy message"


def test_unknown_button_is_left_untouched() -> None:
    _app()
    window = _Window()
    button = QPushButton("OTHER", window.chat_messages_widget)
    button.setObjectName("unrelatedAction")
    button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    controller = MessageActionAccessibilityController(window)
    controller.sync()

    assert button.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert button.property("pathenaMessageActionKeyboard") is None
