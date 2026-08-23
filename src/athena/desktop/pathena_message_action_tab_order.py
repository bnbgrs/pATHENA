"""Deterministic keyboard tab order for existing per-message chat actions."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QLineEdit, QPushButton, QWidget

_ACTION_ORDER = {
    "copyMessageButton": 0,
    "rememberMessageButton": 1,
    "addKnowledgeButton": 2,
}


class MessageActionTabOrderController(QObject):
    """Order dynamic message actions without changing callbacks or enablement."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.document = getattr(window, "chat_messages_widget", None)
        self.composer = getattr(window, "prompt_input", None)
        if isinstance(self.document, QWidget):
            self.document.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.document and event.type() == QEvent.Type.ChildAdded:
            QTimer.singleShot(0, self.sync)
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        if not isinstance(self.document, QWidget):
            return
        groups = self._message_groups()
        ordered: list[QPushButton] = []
        for group_index, buttons in enumerate(groups):
            for action_index, button in enumerate(buttons):
                button.setProperty("pathenaMessageTabOrderManaged", True)
                button.setProperty("pathenaMessageTabGroup", group_index)
                button.setProperty("pathenaMessageTabActionIndex", action_index)
                ordered.append(button)
                if action_index > 0:
                    QWidget.setTabOrder(buttons[action_index - 1], button)

        for index in range(1, len(ordered)):
            previous = ordered[index - 1]
            current = ordered[index]
            if previous.property("pathenaMessageTabGroup") != current.property(
                "pathenaMessageTabGroup"
            ):
                QWidget.setTabOrder(previous, current)

        if ordered and isinstance(self.composer, QLineEdit):
            QWidget.setTabOrder(ordered[-1], self.composer)
            self.composer.setProperty("pathenaMessageTabReturnTarget", True)

        self.window.setProperty("pathenaMessageTabOrderCount", len(ordered))

    def _message_groups(self) -> list[list[QPushButton]]:
        assert isinstance(self.document, QWidget)
        containers = self.document.findChildren(QWidget, "chatMessage")
        keyed: list[tuple[int, int, list[QPushButton]]] = []
        for insertion_index, container in enumerate(containers):
            buttons = [
                button
                for button in container.findChildren(QPushButton)
                if button.objectName() in _ACTION_ORDER
            ]
            if not buttons:
                continue
            buttons.sort(key=lambda button: _ACTION_ORDER[button.objectName()])
            sequence = self._sequence(buttons)
            keyed.append((sequence, insertion_index, buttons))
        keyed.sort(key=lambda entry: (entry[0], entry[1]))
        return [buttons for _sequence, _index, buttons in keyed]

    @staticmethod
    def _sequence(buttons: list[QPushButton]) -> int:
        for button in buttons:
            value = button.property("messageSequence")
            if isinstance(value, int):
                return value
        return 2**31 - 1


def install_message_action_tab_order(
    window: QWidget,
) -> MessageActionTabOrderController:
    """Install deterministic tab ordering for current and future message rows."""
    controller = MessageActionTabOrderController(window)
    window.setProperty("pathenaMessageActionTabOrderController", controller)
    window.setProperty("pathenaMessageActionTabOrderManaged", True)
    return controller
