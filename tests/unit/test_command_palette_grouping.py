from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLineEdit, QListWidget, QMainWindow, QPushButton

from athena.desktop.command_palette import CommandPaletteController


class _PaletteWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.navigation = QListWidget(self)
        for label in ("Chat", "Knowledge", "Research", "Jobs", "Files", "System", "Settings"):
            self.navigation.addItem(label)
        self.new_chat_button = QPushButton(self)
        self.prompt_input = QLineEdit(self)
        self.ground_button = QPushButton(self)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_command_palette_groups_default_results_and_skips_headers() -> None:
    _app()
    window = _PaletteWindow()
    controller = CommandPaletteController(window)

    controller._refresh_results("")

    labels = [controller.results.item(row).text() for row in range(controller.results.count())]
    assert "Workspaces" in labels
    assert "Knowledge" in labels
    assert "Actions" in labels
    for header in ("Workspaces", "Knowledge", "Actions"):
        row = labels.index(header)
        assert controller.results.item(row).flags() == Qt.ItemFlag.NoItemFlags
        assert row not in controller._row_commands

    assert controller.results.currentRow() in controller._row_commands
    for _ in range(controller.results.count() * 2):
        controller._move_selection(1)
        assert controller.results.currentRow() in controller._row_commands


def test_command_palette_search_stays_flat_and_activation_keeps_real_route() -> None:
    _app()
    window = _PaletteWindow()
    controller = CommandPaletteController(window)

    controller._refresh_results("open research")

    labels = [controller.results.item(row).text() for row in range(controller.results.count())]
    assert labels[0] == "Open Research"
    assert "Open Research result & promotion" in labels
    assert tuple(controller._row_commands) == tuple(range(controller.results.count()))
    assert all(label not in {"Workspaces", "Knowledge", "Actions"} for label in labels)

    controller._activate_current()
    assert window.navigation.currentRow() == 2
