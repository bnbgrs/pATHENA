from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_command_palette_truth_6500 import (
    CommandPaletteTruthController,
)


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.resize(1200, 800)
        self.navigation = QListWidget(self)
        self.pages = QStackedWidget(self)
        for index in range(7):
            self.navigation.addItem(f"Workspace {index}")
            self.pages.addWidget(QWidget(self.pages))
        self.new_chat_button = QPushButton("New", self)
        self.prompt_input = QLineEdit(self)
        self.ground_button = QPushButton("Ground", self)


def _palette(qapp: QApplication) -> tuple[_Window, CommandPaletteController, CommandPaletteTruthController]:
    window = _Window()
    window.show()
    palette = CommandPaletteController(window)  # type: ignore[arg-type]
    truth = CommandPaletteTruthController(palette)
    qapp.processEvents()
    return window, palette, truth


def _filter(
    qapp: QApplication,
    palette: CommandPaletteController,
    text: str,
) -> None:
    palette.open()
    palette.query.setText(text)
    qapp.processEvents()
    qapp.processEvents()


def test_available_command_executes_from_keyboard_and_closes_palette(
    qapp: QApplication,
) -> None:
    window, palette, truth = _palette(qapp)
    clicks: list[bool] = []
    window.new_chat_button.clicked.connect(lambda: clicks.append(True))
    try:
        _filter(qapp, palette, "new conversation")

        assert palette.results.count() == 1
        assert palette.results.item(0).text() == "New conversation"
        assert palette.dialog.property("pathenaUiState") == "ready"
        assert truth.status.isVisible() is False

        QTest.keyClick(palette.query, Qt.Key.Key_Return)
        qapp.processEvents()

        assert clicks == [True]
        assert palette.dialog.isVisible() is False
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_context_required_command_explains_blocker_and_does_not_execute(
    qapp: QApplication,
) -> None:
    window, palette, truth = _palette(qapp)
    clicks: list[bool] = []
    window.ground_button.clicked.connect(lambda: clicks.append(True))
    window.ground_button.setEnabled(False)
    window.ground_button.setProperty(
        "pathenaEnablementReason", "Select a grounded chat context first."
    )
    window.ground_button.setProperty(
        "pathenaEnablementRestoreCondition", "Choose available source evidence."
    )
    try:
        _filter(qapp, palette, "use sources")

        assert palette.results.count() == 1
        item = palette.results.item(0)
        assert item is not None
        assert item.text() == "Use sources for next response · context required"
        assert item.data(256) is False
        assert palette.dialog.property("pathenaUiState") == "blocked"
        assert truth.status.isVisible() is True
        assert truth.status.text() == (
            "Context required · Select a grounded chat context first. "
            "Choose available source evidence."
        )

        QTest.keyClick(palette.query, Qt.Key.Key_Return)
        qapp.processEvents()

        assert clicks == []
        assert palette.dialog.isVisible() is True
        assert palette.dialog.property("pathenaUiState") == "blocked"
        assert palette.query.hasFocus() is True

        QTest.keyClick(palette.query, Qt.Key.Key_Escape)
        qapp.processEvents()
        assert palette.dialog.isVisible() is False
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_empty_filter_has_explicit_honest_state(qapp: QApplication) -> None:
    window, palette, truth = _palette(qapp)
    try:
        _filter(qapp, palette, "definitely-not-a-command")

        assert palette.results.count() == 0
        assert palette.dialog.property("pathenaUiState") == "empty"
        assert palette.results.property("pathenaUiState") == "empty"
        assert truth.status.isVisible() is True
        assert truth.status.text() == "No matching commands · refine the search."
        assert truth.status.accessibleName() == "No matching commands"

        QTest.keyClick(palette.query, Qt.Key.Key_Return)
        qapp.processEvents()
        assert palette.dialog.isVisible() is True

        QTest.keyClick(palette.query, Qt.Key.Key_Escape)
        qapp.processEvents()
        assert palette.dialog.isVisible() is False
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_up_down_navigation_wraps_deterministically(qapp: QApplication) -> None:
    window, palette, _truth = _palette(qapp)
    try:
        _filter(qapp, palette, "open")
        assert palette.results.count() > 2
        assert palette.results.currentRow() == 0

        QTest.keyClick(palette.query, Qt.Key.Key_Down)
        qapp.processEvents()
        assert palette.results.currentRow() == 1

        QTest.keyClick(palette.query, Qt.Key.Key_Up)
        qapp.processEvents()
        assert palette.results.currentRow() == 0

        QTest.keyClick(palette.query, Qt.Key.Key_Up)
        qapp.processEvents()
        assert palette.results.currentRow() == palette.results.count() - 1
    finally:
        window.deleteLater()
        qapp.processEvents()
