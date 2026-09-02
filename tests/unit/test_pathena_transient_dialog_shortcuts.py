from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_dialog_focus_return_7200 import install_dialog_focus_return
from athena.desktop.pathena_transient_dialog_shortcuts import (
    install_transient_dialog_shortcut_continuity,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-transient-dialog-shortcuts-test"])


def test_command_and_help_shortcuts_remain_reachable_inside_active_dialogs() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = CommandPaletteController(window)
    continuity = install_transient_dialog_shortcut_continuity(controller)
    try:
        window.show()
        controller.open()
        app.processEvents()

        assert controller.dialog.isVisible()
        assert controller.query.hasFocus()
        assert continuity.help_from_commands.key() == QKeySequence("F1")
        assert (
            continuity.help_from_commands.context()
            == Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

        QTest.keyClick(controller.query, Qt.Key.Key_F1)
        app.processEvents()

        assert controller.help_dialog.isVisible()
        assert not controller.dialog.isVisible()
        assert controller.help_text.hasFocus()
        assert controller.help_text.textCursor().position() == 0
        assert continuity.commands_from_help.key() == QKeySequence("Ctrl+K")
        assert (
            continuity.commands_from_help.context()
            == Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

        controller.query.setText("research")
        QTest.keyClick(
            controller.help_text,
            Qt.Key.Key_K,
            Qt.KeyboardModifier.ControlModifier,
        )
        app.processEvents()

        assert controller.dialog.isVisible()
        assert not controller.help_dialog.isVisible()
        assert controller.query.hasFocus()
        assert controller.query.text() == ""
    finally:
        continuity.deleteLater()
        controller.dialog.hide()
        controller.help_dialog.hide()
        controller.deleteLater()
        window.close()
        app.processEvents()


def test_tab_and_backtab_stay_inside_transient_surfaces() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = CommandPaletteController(window)
    continuity = install_transient_dialog_shortcut_continuity(controller)
    try:
        window.show()
        controller.open()
        app.processEvents()

        QTest.keyClick(controller.query, Qt.Key.Key_Tab)
        app.processEvents()
        assert controller.results.hasFocus()

        QTest.keyClick(
            controller.results,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        app.processEvents()
        assert controller.query.hasFocus()

        controller.open_help()
        app.processEvents()
        assert controller.help_text.hasFocus()

        QTest.keyClick(controller.help_text, Qt.Key.Key_Tab)
        app.processEvents()
        assert controller.help_text.hasFocus()

        QTest.keyClick(
            controller.help_text,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        app.processEvents()
        assert controller.help_text.hasFocus()
    finally:
        continuity.deleteLater()
        controller.dialog.hide()
        controller.help_dialog.hide()
        controller.deleteLater()
        window.close()
        app.processEvents()


def test_transient_handoff_restores_original_workspace_focus_after_escape() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = CommandPaletteController(window)
    continuity = install_transient_dialog_shortcut_continuity(controller)
    focus_return = install_dialog_focus_return(window)
    try:
        window.show()
        window.navigation.setFocus()
        app.processEvents()
        assert window.navigation.hasFocus()

        controller.open()
        app.processEvents()
        assert controller.query.hasFocus()

        QTest.keyClick(controller.query, Qt.Key.Key_F1)
        app.processEvents()
        assert controller.help_text.hasFocus()
        assert controller.help_dialog.property("pathenaFocusReturnInherited") is True

        QTest.keyClick(controller.help_text, Qt.Key.Key_Escape)
        app.processEvents()
        app.processEvents()

        assert not controller.help_dialog.isVisible()
        assert not controller.dialog.isVisible()
        assert window.navigation.hasFocus()
        assert window.navigation.property("pathenaDialogFocusReturn") == "restored"
    finally:
        focus_return.deleteLater()
        continuity.deleteLater()
        controller.dialog.hide()
        controller.help_dialog.hide()
        controller.deleteLater()
        window.close()
        app.processEvents()
