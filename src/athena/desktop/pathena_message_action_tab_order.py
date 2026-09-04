"""Deterministic keyboard tab order for existing per-message chat actions."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

_ACTION_ORDER = {
    "copyMessageButton": 0,
    "rememberMessageButton": 1,
    "addKnowledgeButton": 2,
}
_CONTAINER_NAMES = {"chatMessage", "chatOperationFailure"}


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
        # Qt can dispatch child events while parent-owned controllers are being
        # constructed or torn down. Treat an unavailable document binding as a
        # transient lifecycle state instead of failing the UI event loop.
        document = getattr(self, "document", None)
        if watched is document and event.type() == QEvent.Type.ChildAdded:
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
        self.window.setProperty(
            "pathenaOperationFailureTabOrderCount",
            sum(
                1
                for button in ordered
                if button.property("pathenaMessageTabContainerRole") == "operation-failure"
            ),
        )

    def _message_groups(self) -> list[list[QPushButton]]:
        assert isinstance(self.document, QWidget)
        visual = self._visual_groups()
        if visual:
            return visual

        containers = self.document.findChildren(QWidget, "chatMessage")
        keyed: list[tuple[int, int, list[QPushButton]]] = []
        for insertion_index, container in enumerate(containers):
            buttons = self._buttons_for(container)
            if not buttons:
                continue
            sequence = self._sequence(buttons)
            keyed.append((sequence, insertion_index, buttons))
        keyed.sort(key=lambda entry: (entry[0], entry[1]))
        return [buttons for _sequence, _index, buttons in keyed]

    def _visual_groups(self) -> list[list[QPushButton]]:
        assert isinstance(self.document, QWidget)
        layout = self.document.layout()
        if not isinstance(layout, QVBoxLayout):
            return []
        groups: list[list[QPushButton]] = []
        for index in range(layout.count()):
            layout_item = layout.itemAt(index)
            if layout_item is None:
                continue
            container = layout_item.widget()
            if container is None or container.objectName() not in _CONTAINER_NAMES:
                continue
            buttons = self._buttons_for(container)
            if not buttons:
                continue
            role = (
                "operation-failure"
                if container.objectName() == "chatOperationFailure"
                else "message"
            )
            for button in buttons:
                button.setProperty("pathenaMessageTabContainerRole", role)
            groups.append(buttons)
        return groups

    @staticmethod
    def _buttons_for(container: QWidget) -> list[QPushButton]:
        buttons = [
            button
            for button in container.findChildren(QPushButton)
            if button.objectName() in _ACTION_ORDER
        ]
        buttons.sort(key=lambda button: _ACTION_ORDER[button.objectName()])
        return buttons

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
