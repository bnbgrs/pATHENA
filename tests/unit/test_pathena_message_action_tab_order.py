from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget

from athena.desktop.pathena_message_action_tab_order import (
    MessageActionTabOrderController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _button(parent: QWidget, name: str, sequence: int) -> QPushButton:
    button = QPushButton(name, parent)
    button.setObjectName(name)
    button.setProperty("messageSequence", sequence)
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    return button


def _message(parent: QWidget, sequence: int) -> tuple[QWidget, list[QPushButton]]:
    container = QWidget(parent)
    container.setObjectName("chatMessage")
    buttons = [
        _button(container, "addKnowledgeButton", sequence),
        _button(container, "copyMessageButton", sequence),
        _button(container, "rememberMessageButton", sequence),
    ]
    return container, buttons


def _surface() -> tuple[QWidget, QWidget, QLineEdit]:
    _app()
    window = QWidget()
    document = QWidget(window)
    composer = QLineEdit(window)
    window.chat_messages_widget = document  # type: ignore[attr-defined]
    window.prompt_input = composer  # type: ignore[attr-defined]
    return window, document, composer


def test_groups_follow_message_sequence_and_action_order() -> None:
    window, document, _composer = _surface()
    _message(document, 20)
    _message(document, 10)
    controller = MessageActionTabOrderController(window)

    groups = controller._message_groups()

    assert len(groups) == 2
    assert [button.property("messageSequence") for button in groups[0]] == [10, 10, 10]
    assert [button.objectName() for button in groups[0]] == [
        "copyMessageButton",
        "rememberMessageButton",
        "addKnowledgeButton",
    ]


def test_sync_marks_stable_group_and_action_indices() -> None:
    window, document, composer = _surface()
    _message(document, 1)
    _message(document, 2)

    controller = MessageActionTabOrderController(window)
    controller.sync()

    ordered = [
        button
        for button in document.findChildren(QPushButton)
        if button.property("pathenaMessageTabOrderManaged") is True
    ]
    assert len(ordered) == 6
    assert sorted(int(button.property("pathenaMessageTabGroup")) for button in ordered) == [
        0,
        0,
        0,
        1,
        1,
        1,
    ]
    assert composer.property("pathenaMessageTabReturnTarget") is True
    assert window.property("pathenaMessageTabOrderCount") == 6


def test_disabled_remember_state_is_preserved() -> None:
    window, document, _composer = _surface()
    _container, buttons = _message(document, 1)
    remember = next(
        button for button in buttons if button.objectName() == "rememberMessageButton"
    )
    remember.setEnabled(False)

    MessageActionTabOrderController(window)

    assert remember.isEnabled() is False
    assert remember.property("pathenaMessageTabOrderManaged") is True


def test_new_message_is_included_after_resync() -> None:
    window, document, _composer = _surface()
    _message(document, 1)
    controller = MessageActionTabOrderController(window)
    assert window.property("pathenaMessageTabOrderCount") == 3

    _message(document, 2)
    controller.sync()

    assert window.property("pathenaMessageTabOrderCount") == 6


def test_visual_flow_includes_operation_failure_copy_between_messages() -> None:
    window, document, composer = _surface()
    layout = QVBoxLayout(document)
    first, _first_buttons = _message(document, 1)
    failure = QWidget(document)
    failure.setObjectName("chatOperationFailure")
    failure_copy = _button(failure, "copyMessageButton", 1)
    second, _second_buttons = _message(document, 2)
    layout.addWidget(first)
    layout.addWidget(failure)
    layout.addWidget(second)

    controller = MessageActionTabOrderController(window)
    groups = controller._message_groups()

    assert len(groups) == 3
    assert groups[1] == [failure_copy]
    assert failure_copy.property("pathenaMessageTabContainerRole") == "operation-failure"
    assert window.property("pathenaOperationFailureTabOrderCount") == 1
    assert composer.property("pathenaMessageTabReturnTarget") is True
