from __future__ import annotations

from PySide6.QtWidgets import QApplication, QFrame

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_help import CapabilityHelpController
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-capability-help-shell-test"])


def test_help_is_shell_hosted_without_extending_primary_page_stack() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()
    try:
        window.navigation.setCurrentRow(2)
        app.processEvents()
        primary_page_count = window.pages.count()
        assert primary_page_count == window.navigation.count() == 7
        assert window.pages.currentIndex() == 2

        palette.open_help()
        app.processEvents()

        shell = window.centralWidget()
        workspace = window.findChild(QFrame, "conversation")
        top_bar = window.findChild(QFrame, "topBar")
        icon_rail = window.findChild(QFrame, "iconRail")
        inspector = window.findChild(QFrame, "inspector")
        assert shell is not None
        assert workspace is not None
        assert top_bar is not None
        assert icon_rail is not None
        assert inspector is not None
        assert palette.help_dialog.parent() is workspace
        assert palette.help_dialog.property("pathenaShellHosted") is True
        assert palette.help_dialog.isVisible()
        assert palette.help_dialog.geometry() == workspace.rect()
        assert top_bar.isVisible()
        assert icon_rail.isVisible()
        assert inspector.isVisible()
        assert window.pages.count() == primary_page_count
        assert window.pages.currentIndex() == 2
        assert window.navigation.currentRow() == 2
        assert window.page_title.text() == "Help"
        assert window.property("pathenaHelpWorkspaceVisible") is True
        assert app.focusWidget() is palette.help_text
        assert "pATHENA capabilities" in palette.help_text.toPlainText()

        palette.help_dialog.hide()
        app.processEvents()

        assert window.pages.count() == primary_page_count
        assert window.pages.currentIndex() == 2
        assert window.navigation.currentRow() == 2
        assert window.page_title.text() == "Research"
        assert window.property("pathenaHelpWorkspaceVisible") is False
    finally:
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_f1_shortcut_uses_transient_shell_help_without_changing_route() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()
    try:
        window.navigation.setCurrentRow(1)
        app.processEvents()
        primary_page_count = window.pages.count()
        current_page = window.pages.currentIndex()

        palette.help_shortcut.activated.emit()
        app.processEvents()

        workspace = window.findChild(QFrame, "conversation")
        assert workspace is not None
        assert palette.help_dialog.isVisible()
        assert palette.help_dialog.parent() is workspace
        assert palette.help_dialog.objectName() == "helpWorkspace"
        assert palette.help_dialog.accessibleName() == "pATHENA help workspace"
        assert window.page_title.accessibleDescription() == "Current workspace: Help."
        assert window.pages.count() == primary_page_count == 7
        assert window.pages.currentIndex() == current_page == 1
        assert window.navigation.currentRow() == 1
    finally:
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()
