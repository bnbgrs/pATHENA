from __future__ import annotations

from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_help import CapabilityHelpController
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-capability-help-shell-test"])


def test_help_is_hosted_in_workspace_stack_and_restores_previous_workspace() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()
    try:
        window.navigation.setCurrentRow(2)
        app.processEvents()
        assert window.pages.currentIndex() == 2

        palette.open_help()
        app.processEvents()

        assert palette.help_dialog.parent() is window.pages
        assert palette.help_dialog.property("pathenaShellHosted") is True
        assert window.pages.currentWidget() is palette.help_dialog
        assert window.page_title.text() == "Help"
        assert window.property("pathenaHelpWorkspaceVisible") is True
        assert app.focusWidget() is palette.help_text
        assert "pATHENA capabilities" in palette.help_text.toPlainText()

        palette.help_dialog.hide()
        app.processEvents()

        assert window.pages.currentIndex() == 2
        assert window.navigation.currentRow() == 2
        assert window.page_title.text() == "Research"
        assert window.property("pathenaHelpWorkspaceVisible") is False
    finally:
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_f1_shortcut_uses_the_shell_hosted_help_surface() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()
    try:
        palette.help_shortcut.activated.emit()
        app.processEvents()

        assert window.pages.currentWidget() is palette.help_dialog
        assert palette.help_dialog.objectName() == "helpWorkspace"
        assert palette.help_dialog.accessibleName() == "pATHENA help workspace"
        assert window.page_title.accessibleDescription() == "Current workspace: Help."
    finally:
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()
