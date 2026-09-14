from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QPushButton

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE
from athena.desktop.pathena_navigation_context_accessibility import (
    install_navigation_context_accessibility,
)
from athena.desktop.pathena_reference_shell import install_reference_shell
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _window_with_primary_navigation() -> PathenaMainWindow:
    window = PathenaMainWindow()
    install_navigation_context_accessibility(window)
    return window


def test_reference_shell_reuses_one_textual_primary_navigation() -> None:
    app = _app()
    window = _window_with_primary_navigation()
    opened: list[bool] = []
    shell = install_reference_shell(window, lambda: opened.append(True))
    app.processEvents()
    try:
        buttons = window.findChildren(QPushButton, "topNavButton")
        assert [button.text() for button in buttons] == [
            "CHAT",
            "KNOWLEDGE",
            "RESEARCH",
            "JOBS",
            "SOURCES",
        ]
        assert window.findChildren(QPushButton, "topPrimaryNavButton") == []

        buttons[1].click()
        assert window.navigation.currentRow() == 1
        assert window.pages.currentIndex() == 1
        assert window.page_title.text() == "Knowledge"
        assert buttons[1].isChecked()
        assert not buttons[0].isChecked()

        search = window.findChild(QPushButton, "topSearchButton")
        assert search is not None
        search.click()
        assert opened == [True]
    finally:
        shell.dispose()
        window.close()


def test_reference_shell_uses_reference_family_geometry() -> None:
    app = _app()
    window = _window_with_primary_navigation()
    shell = install_reference_shell(window, lambda: None)
    app.processEvents()
    try:
        top_bar = window.findChild(QFrame, "topBar")
        icon_rail = window.findChild(QFrame, "iconRail")
        composer = window.findChild(QFrame, "composer")
        inspector = window.findChild(QFrame, "inspector")

        assert top_bar is not None
        assert icon_rail is not None
        assert composer is not None
        assert inspector is not None
        # Qt includes the 1 px bottom divider in the styled frame's box metric.
        assert top_bar.minimumHeight() == SHELL.top_bar_height + 1
        assert top_bar.maximumHeight() == SHELL.top_bar_height + 1
        assert icon_rail.width() == SHELL.icon_rail_width
        assert inspector.width() >= SHELL.inspector_width
        assert composer.minimumHeight() == 80
        assert composer.maximumHeight() == 92
        assert composer.maximumWidth() == 980
        assert window.send_button.minimumWidth() == 44
        assert window.send_button.maximumWidth() == 44
    finally:
        shell.dispose()
        window.close()


def test_reference_shell_keeps_editorial_type_and_cobalt_actions() -> None:
    assert PALETTE.canvas == "#061421"
    assert PALETTE.accent == "#3B82F6"
    assert PALETTE.warning == "#E9A84D"
    assert "serif" in TYPE.display_family.lower()
    assert TYPE.title_px >= 40
