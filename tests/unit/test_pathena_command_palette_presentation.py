from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-command-palette-test"])


def test_command_palette_uses_quiet_product_copy_without_losing_commands() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = CommandPaletteController(window)
    try:
        assert controller.dialog.windowTitle() == "pATHENA Commands"
        assert controller.query.placeholderText() == "Search commands or workspaces…"
        assert controller.query.accessibleName() == "Command search"
        assert "Results update as you type" in controller.query.accessibleDescription()
        assert controller.results.accessibleName() == "Command results"

        titles = {
            label.text()
            for label in controller.dialog.findChildren(QLabel)
            if label.objectName() == "commandPaletteTitle"
        }
        assert titles == {"Commands"}

        labels = {command.label for command in controller._commands}
        assert {
            "Open Chat",
            "Open Knowledge",
            "Open Research",
            "Open Jobs",
            "Open Files",
            "Open System",
            "Open Settings",
        }.issubset(labels)
        assert "New conversation" in labels
        assert "Use sources for next response" in labels
        assert "Open model settings" in labels
        assert "Open help" in labels

        controller._refresh_results("ground")
        assert controller.results.count() == 1
        assert controller.results.item(0).text() == "Use sources for next response"
        assert controller.results.accessibleDescription().startswith("1 matching command.")

        controller._refresh_results("no-command-can-match-this")
        assert controller.results.count() == 0
        assert controller.results.accessibleDescription().startswith("0 matching commands.")

        controller._refresh_results("conversation")
        result_labels = {
            controller.results.item(index).text()
            for index in range(controller.results.count())
        }
        assert "New conversation" in result_labels
    finally:
        controller.deleteLater()
        window.close()
        app.processEvents()


def test_help_surface_is_readable_and_documents_current_shortcuts() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = CommandPaletteController(window)
    try:
        assert controller.help_dialog.windowTitle() == "pATHENA Help"
        assert controller.help_text.isReadOnly()
        assert controller.help_text.accessibleName() == "pATHENA help content"
        assert "Read-only guide" in controller.help_text.accessibleDescription()
        help_text = controller._render_help_text()

        assert help_text.startswith("Workspaces\n")
        assert "Ctrl K       Commands" in help_text
        assert "Ctrl+Enter   Send message" in help_text
        assert "F1           Help" in help_text
        assert "Available commands" in help_text
        assert "Availability" in help_text
        assert "LOCAL-FIRST WORKSPACE" not in help_text
        assert "COMMAND PALETTE" not in help_text
    finally:
        controller.deleteLater()
        window.close()
        app.processEvents()
