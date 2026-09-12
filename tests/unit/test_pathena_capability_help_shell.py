from __future__ import annotations

from PySide6.QtWidgets import QApplication, QFrame, QLabel

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_help import CapabilityHelpController
from athena.desktop.pathena_navigation_context_accessibility import (
    install_navigation_context_accessibility,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-capability-help-shell-test"])


def test_help_is_shell_hosted_without_extending_primary_page_stack() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    install_navigation_context_accessibility(window)
    palette = CommandPaletteController(window)
    controller = CapabilityHelpController(palette)
    window.show()
    app.processEvents()
    try:
        window.navigation.setCurrentRow(2)
        app.processEvents()
        primary_page_count = window.pages.count()
        original_inspector_id = window.inspector_object_id.text()
        route_overlay = window.findChild(QFrame, "inspectorRouteContext")
        assert primary_page_count == window.navigation.count() == 7
        assert window.pages.currentIndex() == 2
        assert route_overlay is not None
        assert route_overlay.isVisible()

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
        assert not route_overlay.isVisible()
        assert window.pages.count() == primary_page_count
        assert window.pages.currentIndex() == 2
        assert window.navigation.currentRow() == 2
        assert window.page_title.text() == "Help"
        assert window.property("pathenaHelpWorkspaceVisible") is True
        assert app.focusWidget() is controller.help_query
        assert controller.help_sections.count() > 1
        assert controller.help_capabilities.count() == len(controller.snapshot().capabilities)
        assert controller.help_query.placeholderText() == "Search help…"
        assert controller.help_capabilities.spacing() == 6
        assert window.inspector_object_id.text() == "HELP / LIVE"
        assert window.inspector_heading.text() == "Quick shortcuts"
        assert "Ctrl K" in window.inspector_provenance.text()
        assert "F1" in window.inspector_provenance.text()
        assert "generated from active capabilities" in window.inspector_provenance.text()
        assert "pATHENA capabilities" in palette.help_text.toPlainText()

        first_capability = controller.snapshot().capabilities[0]
        first_item = controller.help_capabilities.item(0)
        first_row = controller.help_capabilities.itemWidget(first_item)
        assert first_row is not None
        assert first_row.objectName() == "helpCapabilityRow"
        assert first_item.sizeHint().height() >= 76
        row_title = first_row.findChild(QLabel, "helpCapabilityTitle")
        row_summary = first_row.findChild(QLabel, "helpCapabilitySummary")
        row_state = first_row.findChild(QLabel, "helpCapabilityState")
        assert row_title is not None
        assert row_summary is not None
        assert row_state is not None
        assert row_title.text() == first_capability.label
        assert row_summary.text() == first_capability.summary
        assert row_state.text() == first_capability.availability.value.replace(
            "_", " "
        ).upper()
        assert first_row.property("pathenaCapabilityAvailability") == (
            first_capability.availability.value
        )

        controller.help_query.setText(first_capability.label)
        app.processEvents()
        visible_items = [
            controller.help_capabilities.item(index)
            for index in range(controller.help_capabilities.count())
            if not controller.help_capabilities.item(index).isHidden()
        ]
        assert visible_items
        assert all(
            first_capability.label.casefold() in item.text().casefold()
            for item in visible_items
        )

        palette.help_dialog.hide()
        app.processEvents()

        assert window.pages.count() == primary_page_count
        assert window.pages.currentIndex() == 2
        assert window.navigation.currentRow() == 2
        assert window.page_title.text() == "Research"
        assert window.property("pathenaHelpWorkspaceVisible") is False
        assert window.inspector_object_id.text() == original_inspector_id
        assert route_overlay.isVisible()
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
        assert controller.help_query.isVisible()
        assert controller.help_capabilities.isVisible()
        assert window.inspector_object_id.text() == "HELP / LIVE"
    finally:
        controller.deleteLater()
        palette.deleteLater()
        window.close()
        app.processEvents()
