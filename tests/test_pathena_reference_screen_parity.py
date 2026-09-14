from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QListWidget, QPushButton, QWidget

from athena.desktop.pathena_reference_screen_parity import (
    COMPOSER_PLACEHOLDER,
    PAGE_LABELS,
    REFERENCE_FAMILY,
    TOP_NAV_LABELS,
    install_reference_screen_parity,
)


class _ReferenceWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.navigation = QListWidget(self)
        for label in ("Workspace", "Library", "Research", "Jobs", "Sources", "System", "Settings"):
            self.navigation.addItem(label)
        self.navigation.setCurrentRow(0)

        self.page_title = QLabel("Workspace", self)
        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Ask, explore, or work with your knowledge…")
        self.send_button = QPushButton("→", self)

        self.reference_top_nav_buttons: list[QPushButton] = []
        for index, label in enumerate(("WORKSPACE", "LIBRARY", "RESEARCH", "JOBS", "SOURCES")):
            button = QPushButton(label, self)
            button.setCheckable(True)
            button.setProperty("pageIndex", index)
            self.reference_top_nav_buttons.append(button)

        self.local_status = QLabel("LOCAL / PRIVATE", self)
        self.local_status.setObjectName("localPrivateStatus")


def _application() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_reference_contract_matches_selected_eleven_screen_family() -> None:
    assert REFERENCE_FAMILY == "11-screen-2026-08-24"
    assert PAGE_LABELS == (
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    )
    assert TOP_NAV_LABELS == {
        0: "CHAT",
        1: "KNOWLEDGE",
        2: "RESEARCH",
        3: "JOBS",
        4: "SOURCES",
    }
    assert COMPOSER_PLACEHOLDER == "Ask, explore, or build…"


def test_parity_adapter_normalizes_live_shell_copy_and_navigation() -> None:
    app = _application()
    window = _ReferenceWindow()
    parity = install_reference_screen_parity(window)

    assert window.property("referenceFamily") == REFERENCE_FAMILY
    assert [button.text() for button in window.reference_top_nav_buttons] == [
        "CHAT",
        "KNOWLEDGE",
        "RESEARCH",
        "JOBS",
        "SOURCES",
    ]
    assert window.prompt_input.placeholderText() == COMPOSER_PLACEHOLDER
    assert window.prompt_input.accessibleName() == "Ask pATHENA"
    assert window.send_button.text() == "↑"
    assert window.local_status.text() == "Local · Private"
    assert window.page_title.text() == "Chat"

    window.navigation.setCurrentRow(1)
    app.processEvents()
    assert window.page_title.text() == "Knowledge"
    assert window.reference_top_nav_buttons[1].isChecked()
    assert not window.reference_top_nav_buttons[0].isChecked()

    window.navigation.setCurrentRow(5)
    app.processEvents()
    assert window.page_title.text() == "System"
    assert not any(button.isChecked() for button in window.reference_top_nav_buttons)

    parity.deleteLater()
    window.deleteLater()
    app.processEvents()
