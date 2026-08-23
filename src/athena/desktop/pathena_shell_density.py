"""Small presentation-only density pass for the final pATHENA shell.

The functional window owns controls and signals. This pass only removes redundant
visible labels after those controls exist, while keeping their accessible names,
tooltips and object identities intact.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QWidget


def apply_shell_density(window: QWidget) -> None:
    """Reduce permanent chat-toolbar chrome without obscuring control purpose."""
    for label in window.findChildren(QLabel, "sessionLabel"):
        label.hide()

    chat_selector = getattr(window, "chat_selector", None)
    if chat_selector is not None:
        chat_selector.setAccessibleName("Conversation")
        chat_selector.setToolTip("Conversation · choose a local conversation")
        chat_selector.setMinimumWidth(280)
        chat_selector.setMaximumWidth(440)

    model_selector = getattr(window, "model_selector", None)
    if model_selector is not None:
        model_selector.setAccessibleName("Model")
        model_selector.setToolTip("Model · choose the local model used for this conversation")
        model_selector.setMinimumWidth(190)
        model_selector.setMaximumWidth(280)

    new_chat_button = getattr(window, "new_chat_button", None)
    if new_chat_button is not None:
        new_chat_button.setAccessibleName("New conversation")

    delete_chat_button = getattr(window, "delete_chat_button", None)
    if delete_chat_button is not None:
        delete_chat_button.setAccessibleName("Delete conversation")
