from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL
from athena.desktop.pathena_reference_parity import install_reference_parity
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def test_reference_parity_installs_textual_top_workspace_navigation() -> None:
    app = _app()
    window = PathenaMainWindow()
    opened: list[bool] = []
    parity = install_reference_parity(window, lambda: opened.append(True))
    app.processEvents()
    try:
        buttons = window.findChildren(QPushButton, "topPrimaryNavButton")
        assert [button.text() for button in buttons] == [
            "CHAT",
            "KNOWLEDGE",
            "RESEARCH",
            "JOBS",
            "SOURCES",
        ]

        buttons[1].click()
        assert window.navigation.currentRow() == 1
        assert window.pages.currentIndex() == 1
        assert window.page_title.text() == "Knowledge"
        assert buttons[1].property("selected") is True
        assert buttons[0].property("selected") is False

        search = window.findChild(QPushButton, "topSearchButton")
        assert search is not None
        search.click()
        assert opened == [True]
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_applies_shared_reference_geometry() -> None:
    app = _app()
    previous_stylesheet = app.styleSheet()
    app.setStyleSheet(PATHENA_STYLESHEET)
    window = PathenaMainWindow()
    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        top_bar = window.findChild(QFrame, "topBar")
        icon_rail = window.findChild(QFrame, "iconRail")
        secondary = window.findChild(QListWidget, "settingsSecondaryNavigation")
        composer = window.findChild(QFrame, "composer")
        inspector = window.findChild(QFrame, "inspector")

        assert top_bar is not None
        assert icon_rail is not None
        assert composer is not None
        assert inspector is not None
        # Qt includes the styled 1 px frame in the effective fixed geometry.
        assert top_bar.minimumHeight() == SHELL.top_bar_height + top_bar.frameWidth()
        assert top_bar.maximumHeight() == SHELL.top_bar_height + top_bar.frameWidth()
        assert icon_rail.width() == SHELL.icon_rail_width
        assert inspector.width() == SHELL.inspector_width + inspector.frameWidth()
        assert composer.minimumHeight() == 80
        assert composer.maximumHeight() == 92
        assert composer.maximumWidth() == 980
        # An inherited line-edit style may lower the stored minimum constraint,
        # while the 80–92 px composer supplies the final rendered geometry.
        assert window.prompt_input.minimumHeight() >= 44
        assert window.prompt_input.maximumHeight() <= 56
        assert window.send_button.minimumWidth() == SHELL.composer_action_size
        assert window.send_button.maximumWidth() == SHELL.composer_action_size
        assert window.send_button.minimumHeight() == SHELL.composer_action_size
        assert window.send_button.maximumHeight() == SHELL.composer_action_size
        if secondary is not None:
            assert secondary.width() == SHELL.secondary_nav_width
    finally:
        parity.dispose()
        window.close()
        app.setStyleSheet(previous_stylesheet)


def test_reference_parity_marks_workspace_surfaces_for_qss_background_painting() -> None:
    app = _app()
    window = PathenaMainWindow()
    research_page = window.pages.widget(2)
    assert research_page is not None
    layout = research_page.layout()
    assert isinstance(layout, QVBoxLayout)
    surface = QWidget(research_page)
    surface.setObjectName("researchWorkspace")
    layout.addWidget(surface)

    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        assert surface.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        assert "QWidget#researchWorkspace" in window.styleSheet()
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_paints_canonical_memory_panes_with_canvas_token() -> None:
    app = _app()
    window = PathenaMainWindow()
    pane = QWidget(window)
    pane.setObjectName("canonicalMemoryListPane")
    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        assert pane.testAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        assert "QWidget#canonicalMemoryListPane" in window.styleSheet()
        assert f"background: {PALETTE.canvas};" in window.styleSheet()
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_forces_cobalt_focus_on_real_research_inputs() -> None:
    app = _app()
    window = PathenaMainWindow()
    research_page = window.pages.widget(2)
    assert research_page is not None
    layout = research_page.layout()
    assert isinstance(layout, QVBoxLayout)
    field = QLineEdit(research_page)
    field.setObjectName("researchJobFilter")
    layout.addWidget(field)

    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        stylesheet = field.styleSheet()
        assert PALETTE.accent in stylesheet
        assert PALETTE.surface in stylesheet
        assert "#F26A21" not in stylesheet
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_keeps_generic_inspector_contextual() -> None:
    app = _app()
    window = PathenaMainWindow()
    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        assert inspector.isHidden()

        window._set_context_available(True)
        assert not inspector.isHidden()

        window.navigation.setCurrentRow(2)
        assert inspector.isHidden()

        window.navigation.setCurrentRow(0)
        assert not inspector.isHidden()

        window._set_context_available(False)
        assert inspector.isHidden()
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_styles_pallas_jobs_system_and_settings_surfaces() -> None:
    app = _app()
    window = PathenaMainWindow()
    parity = install_reference_parity(window, lambda: None)
    app.processEvents()
    try:
        stylesheet = window.styleSheet()
        assert "QFrame#pallasShellWorkspaceHost" in stylesheet
        assert "QListWidget#durableJobList" in stylesheet
        assert "QListWidget#sourceList" in stylesheet
        assert "QFrame#systemStatusRow" in stylesheet
        assert "QListWidget#settingsSecondaryNavigation" in stylesheet
        assert "QDialog#commandPalette" in stylesheet
        assert "QWidget#helpWorkspace" in stylesheet
        assert "QDialog#comfyUiDialog" in stylesheet
        assert "QWidget#researchWorkspace QSplitter" in stylesheet
        assert "QTabWidget#canonicalMemoryTabs QTabBar" in stylesheet
    finally:
        parity.dispose()
        window.close()


def test_reference_parity_uses_cobalt_action_accent_not_global_orange() -> None:
    assert PALETTE.accent == "#3B82F6"
    assert PALETTE.warning == "#E9A84D"
    assert PALETTE.accent != PALETTE.warning
