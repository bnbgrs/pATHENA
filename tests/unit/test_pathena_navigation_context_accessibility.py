from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.pathena_navigation_context_accessibility import (
    NavigationContextAccessibility,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-navigation-context-test"])


def test_navigation_context_tracks_existing_workspace_selection() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = NavigationContextAccessibility(window)
    try:
        expected = ("Chat", "Knowledge", "Research", "Jobs", "Files", "System", "Settings")
        assert window.navigation.accessibleName() == "Workspaces"

        for row, label in enumerate(expected):
            window.navigation.setCurrentRow(row)
            app.processEvents()

            assert window.pages.currentIndex() == row
            assert window.page_title.text() == label
            assert window.page_title.accessibleDescription() == f"Current workspace: {label}."
            assert window.navigation.property("pathenaCurrentWorkspace") == label
            item = window.navigation.item(row)
            assert item.data(Qt.ItemDataRole.AccessibleTextRole) == label
            assert item.data(Qt.ItemDataRole.AccessibleDescriptionRole) == (
                f"{label}; current workspace"
            )
            assert window.pages.widget(row).property("pathenaCurrentWorkspace") is True
    finally:
        controller.deleteLater()
        window.close()
        app.processEvents()


def test_navigation_context_does_not_move_existing_focus() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = NavigationContextAccessibility(window)
    window.show()
    app.processEvents()
    try:
        window.prompt_input.setEnabled(True)
        window.prompt_input.setFocus()
        app.processEvents()
        assert app.focusWidget() is window.prompt_input

        window.navigation.setCurrentRow(1)
        app.processEvents()

        assert window.pages.currentIndex() == 1
        assert app.focusWidget() is window.prompt_input
    finally:
        controller.deleteLater()
        window.close()
        app.processEvents()
