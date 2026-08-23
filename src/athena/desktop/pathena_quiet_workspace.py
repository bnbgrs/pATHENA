"""Small presentation-only refinements for pATHENA's quiet workspace.

This module deliberately operates on existing widgets after all workspaces have
been installed. It changes hierarchy, labels and sizing only; controller and
workspace behaviour stay untouched.
"""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFrame, QLabel, QListWidget, QPushButton, QWidget

from athena.desktop.pathena_window import PathenaMainWindow


def apply_quiet_workspace_refinement(window: PathenaMainWindow) -> None:
    """Reduce permanent chrome and make the conversation the visual anchor."""
    navigation = window.findChild(QListWidget, "navigation")
    if navigation is not None:
        navigation.setFixedWidth(174)
        for index in range(navigation.count()):
            navigation.item(index).setSizeHint(QSize(158, 34))

    rail = window.findChild(QFrame, "rail")
    if rail is not None:
        rail.setFixedWidth(198)

    page_title = window.findChild(QLabel, "pageTitle")
    if page_title is not None:
        page_title.setToolTip("Current workspace")

    # PALLAS remains a recognisable ambient element, but should never compete
    # with the conversation or persistent workspace controls.
    pallas = getattr(window, "pallas_visual", None)
    if isinstance(pallas, QWidget):
        pallas.setFixedSize(104, 164)
        pallas.setToolTip("PALLAS · ambient local context")

    # Secondary actions read as quiet affordances rather than primary controls.
    details = getattr(window, "details_button", None)
    if isinstance(details, QPushButton):
        details.setText("Inspect")
        details.setMaximumWidth(72)
        details.setToolTip("Inspect conversation details and provenance")

    context = getattr(window, "context_button", None)
    if isinstance(context, QPushButton):
        context.setText("Evidence")
        context.setMaximumWidth(78)
        context.setToolTip("Reveal sources and evidence for this response")

    window.new_chat_button.setText("New chat")
    window.new_chat_button.setToolTip("Start a new conversation")
    window.delete_chat_button.setText("Delete")

    window.chat_selector.setMinimumWidth(220)
    window.model_selector.setMinimumWidth(180)
    window.prompt_input.setPlaceholderText("Message pATHENA…")

    # Keep destructive and diagnostic machinery out of the resting state.
    inspector = window.findChild(QFrame, "inspector")
    if inspector is not None:
        inspector.setMinimumWidth(300)
        inspector.setMaximumWidth(360)
