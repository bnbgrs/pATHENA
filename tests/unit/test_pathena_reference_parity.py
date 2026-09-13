from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QListWidget, QPushButton

from athena.desktop.pathena_design_tokens import PALETTE, SHELL
from athena.desktop.pathena_reference_parity import install_reference_parity
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
        assert top_bar.height() == SHELL.top_bar_height
        assert icon_rail.width() == SHELL.icon_rail_width
        assert inspector.width() == SHELL.inspector_width + inspector.frameWidth()
        assert composer.minimumHeight() == 80
        assert composer.maximumHeight() == 92
        assert composer.maximumWidth() == 980
        assert window.prompt_input.minimumHeight() == 48
        assert window.send_button.minimumWidth() == 48
        assert window.send_button.maximumWidth() == 48
        assert window.send_button.minimumHeight() == 48
        assert window.send_button.maximumHeight() == 48
        if secondary is not None:
            assert secondary.width() == SHELL.secondary_nav_width
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


def test_reference_parity_uses_cobalt_action_accent_not_global_orange() -> None:
    assert PALETTE.accent == "#3B82F6"
    assert PALETTE.warning == "#E9A84D"
    assert PALETTE.accent != PALETTE.warning
