from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFrame, QVBoxLayout

from athena.desktop.pathena_design_tokens import SHELL
from athena.desktop.pathena_secondary_navigation import (
    install_settings_secondary_navigation,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _window_with_runtime_panel() -> tuple[PathenaMainWindow, QFrame]:
    window = PathenaMainWindow()
    settings_page = window.pages.widget(6)
    assert settings_page is not None
    layout = settings_page.layout()
    assert isinstance(layout, QVBoxLayout)
    runtime_panel = QFrame()
    runtime_panel.setObjectName("settingsRuntimePanel")
    layout.insertWidget(4, runtime_panel)
    return window, runtime_panel


def test_settings_secondary_navigation_wraps_only_real_sections() -> None:
    _app()
    window, runtime_panel = _window_with_runtime_panel()
    try:
        controller = install_settings_secondary_navigation(window)

        assert controller.section_names == ("Model & inference", "Local runtime")
        assert controller.navigation.width() == SHELL.secondary_nav_width
        assert 210 <= controller.navigation.width() <= 280
        assert controller.navigation.currentRow() == 0
        assert controller.navigation.accessibleName() == "Settings sections"
        assert controller.content.isAncestorOf(window.context_spin)
        assert controller.content.isAncestorOf(runtime_panel)
        assert controller.navigation.item(0).data(Qt.ItemDataRole.UserRole) == "model"
        assert controller.navigation.item(1).data(Qt.ItemDataRole.UserRole) == "runtime"
    finally:
        window.close()


def test_settings_secondary_navigation_exposes_accessible_section_semantics() -> None:
    _app()
    window, _runtime_panel = _window_with_runtime_panel()
    try:
        controller = install_settings_secondary_navigation(window)

        model_item = controller.navigation.item(0)
        runtime_item = controller.navigation.item(1)
        assert model_item.data(Qt.ItemDataRole.AccessibleTextRole) == "Model & inference"
        assert model_item.data(Qt.ItemDataRole.AccessibleDescriptionRole) == (
            "Open Model & inference settings"
        )
        assert model_item.toolTip() == "Open Model & inference settings"
        assert runtime_item.data(Qt.ItemDataRole.AccessibleTextRole) == "Local runtime"
        assert runtime_item.data(Qt.ItemDataRole.AccessibleDescriptionRole) == (
            "Open Local runtime settings"
        )
        assert runtime_item.toolTip() == "Open Local runtime settings"
    finally:
        window.close()


def test_settings_secondary_navigation_does_not_invent_unavailable_sections() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        controller = install_settings_secondary_navigation(window)

        assert controller.section_names == ("Model & inference",)
        assert controller.navigation.count() == 1
        assert controller.navigation.item(0).data(Qt.ItemDataRole.UserRole) == "model"
        assert controller.navigation.findItems(
            "Local runtime", Qt.MatchFlag.MatchExactly
        ) == []
    finally:
        window.close()


def test_settings_secondary_navigation_keyboard_selection_is_deterministic() -> None:
    app = _app()
    window, _runtime_panel = _window_with_runtime_panel()
    try:
        controller = install_settings_secondary_navigation(window)
        window.navigation.setCurrentRow(6)
        window.show()
        controller.navigation.setFocus()
        app.processEvents()

        assert controller.navigation.hasFocus()
        QTest.keyClick(controller.navigation, Qt.Key.Key_Down)
        app.processEvents()

        assert controller.navigation.currentRow() == 1
        assert controller.navigation.accessibleDescription() == (
            "Selected section: Local runtime"
        )
        assert window.pages.currentIndex() == 6
    finally:
        window.close()


def test_settings_secondary_navigation_install_is_idempotent() -> None:
    _app()
    window, _runtime_panel = _window_with_runtime_panel()
    try:
        first = install_settings_secondary_navigation(window)
        second = install_settings_secondary_navigation(window)

        assert second is first
        settings_page = window.pages.widget(6)
        assert settings_page is not None
        assert len(settings_page.findChildren(QFrame, "settingsSecondaryContainer")) == 1
        assert first.parent() is window
    finally:
        window.close()
