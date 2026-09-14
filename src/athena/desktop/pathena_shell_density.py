"""Small presentation-only density pass for the final pATHENA shell.

The functional window owns controls and signals. This pass only removes redundant
visible labels and aligns final top-level navigation after all workspaces exist,
while keeping accessible names, tooltips and object identities intact.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTabWidget, QWidget

from athena.desktop.pathena_design_tokens import PALETTE, SPACE, TYPE

_SYSTEM_TABS_STYLESHEET = f"""
QTabWidget#systemOperationsTabs::pane {{
    background: transparent;
    border: none;
    border-top: 1px solid {PALETTE.border};
    top: -1px;
}}

QTabWidget#systemOperationsTabs QTabBar::tab {{
    color: {PALETTE.text_subtle};
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    min-height: 32px;
    padding: 0 {SPACE.sm}px;
    margin-right: {SPACE.xxs}px;
    font-family: {TYPE.metadata_family};
    font-size: {TYPE.metadata_px}px;
    font-weight: 500;
}}

QTabWidget#systemOperationsTabs QTabBar::tab:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}

QTabWidget#systemOperationsTabs QTabBar::tab:selected {{
    color: {PALETTE.text};
    background: transparent;
    border-bottom-color: {PALETTE.accent};
}}
"""


def apply_shell_density(window: QWidget) -> None:
    """Reduce permanent shell chrome without obscuring control purpose."""
    for label in window.findChildren(QLabel, "sessionLabel"):
        label.hide()

    chat_selector = getattr(window, "chat_selector", None)
    if chat_selector is not None:
        chat_selector.setAccessibleName("Conversation")
        chat_selector.setToolTip("Conversation · choose a local conversation")
        chat_selector.setMinimumWidth(250)
        chat_selector.setMaximumWidth(360)

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

    system_tabs = window.findChild(QTabWidget, "systemOperationsTabs")
    if system_tabs is not None:
        system_tabs.setDocumentMode(True)
        system_tabs.setUsesScrollButtons(False)
        system_tabs.setStyleSheet(_SYSTEM_TABS_STYLESHEET)
