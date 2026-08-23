"""Quiet progressive disclosure for existing per-message actions.

Message actions remain present, keyboard-focusable and clickable, but they should not
compete with the conversation body on every row. This presentation-only controller
reduces only action opacity while a message is inactive and restores full emphasis for
pointer hover or keyboard focus. Layout, visibility, enablement and callbacks are never
changed.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QPushButton,
    QWidget,
)

_ACTION_NAMES = {
    "copyMessageButton",
    "rememberMessageButton",
    "addKnowledgeButton",
}


class MessageActionQuietController(QObject):
    """Reduce inactive message-action emphasis without hiding controls."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.document = getattr(window, "chat_messages_widget", None)
        self._containers: dict[QWidget, list[QPushButton]] = {}
        self._effects: dict[QPushButton, QGraphicsOpacityEffect] = {}
        if isinstance(self.document, QWidget):
            self.document.installEventFilter(self)
        self.sync()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.document and event.type() == QEvent.Type.ChildAdded:
            QTimer.singleShot(0, self.sync)
        elif isinstance(watched, QWidget) and watched in self._containers:
            if event.type() in {QEvent.Type.Enter, QEvent.Type.Leave}:
                QTimer.singleShot(0, lambda target=watched: self._refresh(target))
        elif isinstance(watched, QPushButton) and watched in self._effects:
            if event.type() in {
                QEvent.Type.FocusIn,
                QEvent.Type.FocusOut,
                QEvent.Type.EnabledChange,
            }:
                container = self._message_container(watched)
                if container is not None:
                    QTimer.singleShot(0, lambda target=container: self._refresh(target))
        return super().eventFilter(watched, event)

    def sync(self) -> None:
        if not isinstance(self.document, QWidget):
            return
        for button in self.document.findChildren(QPushButton):
            if button.objectName() not in _ACTION_NAMES or button in self._effects:
                continue
            container = self._message_container(button)
            if container is None:
                continue
            effect = QGraphicsOpacityEffect(button)
            effect.setOpacity(1.0)
            button.setGraphicsEffect(effect)
            button.setProperty("pathenaMessageActionQuiet", True)
            button.setProperty("pathenaMessageActionLayoutPreserved", True)
            button.installEventFilter(self)
            self._effects[button] = effect
            self._containers.setdefault(container, []).append(button)
            if len(self._containers[container]) == 1:
                container.setAttribute(container.WidgetAttribute.WA_Hover, True)
                container.installEventFilter(self)
                container.setProperty("pathenaMessageActionsProgressive", True)
            self._refresh(container)

    def _refresh(self, container: QWidget) -> None:
        buttons = self._containers.get(container, [])
        active = container.underMouse() or self._container_has_focus(container)
        for button in buttons:
            opacity = 1.0 if active else 0.38 if button.isEnabled() else 0.24
            effect = self._effects.get(button)
            if effect is not None:
                effect.setOpacity(opacity)
            button.setProperty(
                "pathenaMessageActionEmphasis",
                "active" if active else "quiet",
            )

    @staticmethod
    def _container_has_focus(container: QWidget) -> bool:
        focused = QApplication.focusWidget()
        while focused is not None:
            if focused is container:
                return True
            focused = focused.parentWidget()
        return False

    @staticmethod
    def _message_container(button: QPushButton) -> QWidget | None:
        parent = button.parentWidget()
        while parent is not None:
            if parent.objectName() in {"chatMessage", "chatOperationFailure"}:
                return parent
            parent = parent.parentWidget()
        return None


def install_message_action_quiet(window: QWidget) -> MessageActionQuietController:
    """Install quiet progressive disclosure for current and future message actions."""
    controller = MessageActionQuietController(window)
    window.setProperty("pathenaMessageActionQuietController", controller)
    window.setProperty("pathenaMessageActionQuietManaged", True)
    return controller
