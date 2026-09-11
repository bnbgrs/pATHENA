from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

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
        expected = (
            "Workspace",
            "Library",
            "Research",
            "Jobs",
            "Sources",
            "System",
            "Settings",
        )
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


def test_top_navigation_reuses_existing_router_and_tracks_checked_state() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = NavigationContextAccessibility(window)
    window.show()
    app.processEvents()
    try:
        buttons = window.findChildren(QPushButton, "topNavButton")
        assert [button.text() for button in buttons] == [
            "Chat",
            "Knowledge",
            "Research",
            "Jobs",
            "Sources",
        ]

        for row, button in enumerate(buttons):
            button.click()
            app.processEvents()

            assert window.navigation.currentRow() == row
            assert window.pages.currentIndex() == row
            assert button.isChecked()
            assert button.accessibleDescription() == f"{button.text()}; current workspace"
            assert all(other.isChecked() is (other is button) for other in buttons)
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


def test_jobs_and_settings_use_truthful_contextual_inspector_overlays() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    controller = NavigationContextAccessibility(window)
    window.show()
    app.processEvents()
    try:
        panel = window.findChild(QFrame, "inspectorRouteContext")
        assert panel is not None
        context_id = panel.findChild(QLabel, "objectId")
        heading = panel.findChild(QLabel, "inspectorHeading")
        body = panel.findChild(QLabel, "inspectorBody")
        assert context_id is not None
        assert heading is not None
        assert body is not None

        window.navigation.setCurrentRow(3)
        app.processEvents()
        assert panel.isVisible()
        assert context_id.text() == "JOB / NONE"
        assert heading.text() == "No job selected"
        assert "EXECUTION" in body.text()
        assert "RESOURCES" in body.text()
        assert "Select a job" in body.text()

        window.navigation.setCurrentRow(6)
        app.processEvents()
        assert panel.isVisible()
        assert context_id.text() == "SETTINGS / LOCAL"
        assert heading.text() == "System status"
        assert "No synthetic health state" in body.text()
        assert window.status_text.text() in body.text()

        window.navigation.setCurrentRow(0)
        app.processEvents()
        assert panel.isHidden()
    finally:
        controller.deleteLater()
        window.close()
        app.processEvents()
