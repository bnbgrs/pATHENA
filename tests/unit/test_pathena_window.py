from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QWidget

from athena.desktop.pathena_design_tokens import SHELL
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_reference_shell_replaces_wide_text_sidebar_without_rewiring_navigation() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        assert shell.objectName() == "referenceShell"

        top_bar = shell.findChild(QFrame, "topBar")
        assert top_bar is not None
        assert top_bar.height() == SHELL.top_bar_height

        rail = shell.findChild(QFrame, "rail")
        assert rail is not None
        assert rail.width() == SHELL.icon_rail_width
        assert window.navigation.width() <= SHELL.icon_rail_width
        assert window.navigation.item(0).text() != "Workspace"
        assert window.navigation.item(0).toolTip() == "Workspace"

        window.navigation.setCurrentRow(3)
        assert window.pages.currentIndex() == 3
        assert window.page_title.text() == "Jobs"
    finally:
        window.close()


def test_reference_shell_has_horizontal_primary_navigation_and_private_status() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        buttons = window.findChildren(QPushButton, "topNavButton")
        assert [button.text() for button in buttons] == [
            "WORKSPACE",
            "LIBRARY",
            "RESEARCH",
            "JOBS",
            "SOURCES",
        ]
        assert buttons[0].isChecked()

        buttons[1].click()
        assert window.navigation.currentRow() == 1
        assert buttons[1].isChecked()

        status = window.findChild(QLabel, "localPrivateStatus")
        assert status is not None
        assert status.text() == "Local · Private"
    finally:
        window.close()


def test_reference_inspector_is_persistent_and_composer_action_is_compact() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        assert inspector.width() == SHELL.inspector_width
        assert not inspector.isHidden()
        assert window.details_button.isHidden()

        assert window.send_button.text() == "→"
        assert window.send_button.accessibleName() == "Send message"
        assert window.prompt_input.objectName() == "promptInput"
    finally:
        window.close()
