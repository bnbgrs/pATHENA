from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QWidget

from athena.desktop.pathena_design_tokens import PALETTE, SHELL
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _assert_inspector_width(inspector: QFrame) -> None:
    assert inspector.width() == SHELL.inspector_width + inspector.frameWidth()


def test_reference_shell_owns_icon_rail_without_rewiring_navigation() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        assert shell.objectName() == "referenceShell"

        top_bar = shell.findChild(QFrame, "topBar")
        assert top_bar is not None
        assert top_bar.height() == SHELL.top_bar_height

        body = shell.findChild(QFrame, "referenceBody")
        assert body is not None
        icon_rail = body.findChild(QFrame, "iconRail")
        assert icon_rail is not None
        assert icon_rail.width() == SHELL.icon_rail_width
        assert icon_rail.accessibleName() == "Primary navigation"
        assert window.navigation.parentWidget() is icon_rail
        assert window.navigation.width() <= SHELL.icon_rail_width
        assert window.navigation.item(0).text() != "Workspace"
        assert window.navigation.item(0).toolTip() == "Workspace"

        legacy_host = shell.findChild(QWidget, "legacyShellHost")
        assert legacy_host is not None
        legacy_rail = legacy_host.findChild(QFrame, "rail")
        assert legacy_rail is not None
        assert legacy_host.isHidden()
        assert legacy_rail.isHidden()
        assert not icon_rail.isAncestorOf(window.pallas_visual)
        assert window.pallas_visual.isHidden()

        window.navigation.setCurrentRow(3)
        assert window.pages.currentIndex() == 3
        assert window.page_title.text() == "Jobs"
    finally:
        window.close()


def test_reference_shell_owns_cobalt_navigation_selection() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        stylesheet = window.navigation.styleSheet()
        assert PALETTE.accent in stylesheet
        assert PALETTE.surface_selected in stylesheet
        assert "#F26A21" not in stylesheet.upper()
    finally:
        window.close()


def test_reference_body_directly_owns_workspace_and_persistent_inspector() -> None:
    app = _app()
    window = PathenaMainWindow()
    app.processEvents()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        body = shell.findChild(QFrame, "referenceBody")
        assert body is not None

        center = body.findChild(QFrame, "conversation")
        inspector = body.findChild(QFrame, "inspector")
        assert center is not None
        assert inspector is not None
        assert center.parentWidget() is body
        assert inspector.parentWidget() is body
        _assert_inspector_width(inspector)
        assert inspector.accessibleName() == "Inspector"
        assert not inspector.isHidden()
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
        assert window.pages.currentIndex() == 1
        assert buttons[1].isChecked()

        status = window.findChild(QLabel, "localPrivateStatus")
        assert status is not None
        assert status.text() == "Local · Private"
    finally:
        window.close()


def test_reference_inspector_is_persistent_and_composer_action_is_compact() -> None:
    app = _app()
    window = PathenaMainWindow()
    app.processEvents()
    try:
        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        _assert_inspector_width(inspector)
        assert not inspector.isHidden()
        assert window.details_button.isHidden()

        assert window.send_button.text() == "→"
        assert window.send_button.accessibleName() == "Send message"
        assert window.prompt_input.objectName() == "promptInput"
    finally:
        window.close()
