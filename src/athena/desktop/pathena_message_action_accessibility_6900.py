"""Keyboard access for existing per-message chat actions.

Copy, Remember and Add to Knowledge already have real callbacks, but message rendering
sets them to ``NoFocus``. This presentation-only controller restores normal keyboard
focus, assigns explicit accessible purpose, and marks a restrained focus-visible state.
It watches the existing chat document for newly rendered messages and never changes
button enablement or action callbacks.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QPushButton, QWidget


@dataclass(frozen=True)
class MessageActionSpec:
    object_name: str
    label: str
    description: str


_ACTIONS: tuple[MessageActionSpec, ...] = (
    MessageActionSpec(
        "copyMessageButton",
        "Copy message",
        "Copy the visible message text to the clipboard.",
    ),
    MessageActionSpec(
        "rememberMessageButton",
        "Remember message",
        "Store this exact persisted message in Personal Memory.",
    ),
    MessageActionSpec(
        "addKnowledgeButton",
        "Add message to Knowledge",
        "Extract Knowledge proposals from this exact persisted message for review.",
    ),
)

_FOCUS_STYLE = """
/* pATHENA message action keyboard focus */
QPushButton[pathenaMessageActionKeyboard="true"]:focus {
    border: 1px solid #4A4A4A;
}
"""


class MessageActionAccessibilityController(QObject):
    """Keep dynamically rendered message actions reachable from the keyboard."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.document = getattr(window, "chat_messages_widget", None)
        self._managed: set[QPushButton] = set()
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
        for spec in _ACTIONS:
            for button in self.document.findChildren(QPushButton, spec.object_name):
                self._apply(button, spec)

    def _apply(self, button: QPushButton, spec: MessageActionSpec) -> None:
        if button in self._managed:
            return
        self._managed.add(button)
        button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        button.setAccessibleName(spec.label)
        button.setAccessibleDescription(spec.description)
        button.setProperty("pathenaMessageActionKeyboard", True)
        button.setProperty("pathenaMessageActionPurpose", spec.label.casefold())
        button.setProperty("pathenaMessageActionExistingCallback", True)
        if spec.description not in button.toolTip():
            current = button.toolTip().strip()
            button.setToolTip(f"{current}\n{spec.description}".strip())


def install_message_action_accessibility(
    window: QWidget,
) -> MessageActionAccessibilityController:
    """Install keyboard accessibility for current and future chat message actions."""
    controller = MessageActionAccessibilityController(window)
    if _FOCUS_STYLE not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_FOCUS_STYLE}")
    window.setProperty("pathenaMessageActionAccessibilityController", controller)
    window.setProperty("pathenaMessageActionAccessibilityManaged", True)
    return controller
