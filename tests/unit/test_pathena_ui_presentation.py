from __future__ import annotations

from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-ui-test"])


def test_pathena_application_uses_quiet_workspace_theme() -> None:
    app = _app()

    assert app.styleSheet() == PATHENA_STYLESHEET
    assert app.applicationDisplayName() == "pATHENA"


def test_pathena_shell_progressively_discloses_destructive_chat_action() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        assert window.windowTitle() == "pATHENA"
        assert window.delete_chat_button.isHidden()

        window.chat_selector.addItem("Existing chat", "chat-1")
        window.chat_selector.setCurrentIndex(0)
        app.processEvents()
        assert window.delete_chat_button.isHidden() is False

        window.chat_selector.clear()
        window.chat_selector.addItem("New chat", None)
        app.processEvents()
        assert window.delete_chat_button.isHidden()
    finally:
        window.close()
        app.processEvents()
