from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_help import CapabilityHelpController
from athena.desktop.pathena_v2_shell import install_v2_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-v2-help-header-test"])


def test_v2_help_owns_visible_header_then_restores_selected_route() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    install_v2_shell(window)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()

    try:
        window.navigation.setCurrentRow(6)
        app.processEvents()

        title = window.findChild(QLabel, "v2PageTitle")
        hint = window.findChild(QLabel, "v2PageHint")
        assert title is not None
        assert hint is not None
        assert title.text() == "Settings"
        selected_page = window.pages.currentIndex()
        inspector = window.findChild(QWidget, "inspector")
        assert inspector is not None
        assert inspector.isHidden()

        palette.open_help()
        app.processEvents()

        assert palette.help_dialog.isVisible()
        workspace = window.findChild(QWidget, "v2Workspace")
        assert workspace is not None
        assert palette.help_dialog.parent() is workspace
        assert palette.help_dialog.geometry() == workspace.rect()
        assert window.navigation.currentRow() == 6
        assert window.pages.currentIndex() == selected_page
        assert title.text() == "Help"
        assert title.accessibleDescription() == "Current workspace: Help."
        assert hint.text() == "Current commands, shortcuts, and available capabilities."
        assert app.focusWidget() is controller.help_query

        QTest.keyClick(controller.help_query, Qt.Key.Key_Tab)
        app.processEvents()
        assert app.focusWidget() is controller.help_sections

        QTest.keyClick(controller.help_sections, Qt.Key.Key_Tab)
        app.processEvents()
        assert app.focusWidget() is controller.help_capabilities

        QTest.keyClick(
            controller.help_capabilities,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        app.processEvents()
        assert app.focusWidget() is controller.help_sections

        palette.help_dialog.hide()
        app.processEvents()

        assert not palette.help_dialog.isVisible()
        assert window.navigation.currentRow() == 6
        assert window.pages.currentIndex() == selected_page
        assert title.text() == "Settings"
        assert hint.text() != "Current commands, shortcuts, and available capabilities."
        assert inspector.isHidden()
    finally:
        controller.dispose()
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()
