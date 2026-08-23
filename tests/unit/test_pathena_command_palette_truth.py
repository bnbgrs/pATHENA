from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget

from athena.desktop.pathena_command_palette_truth_6500 import CommandPaletteTruthController


@dataclass
class _FakeCommand:
    label: str


class _FakePalette(QObject):
    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.dialog = QDialog(window)
        self.dialog.setLayout(QVBoxLayout())
        self.query = QLineEdit(self.dialog)
        self.results = QListWidget(self.dialog)
        self.dialog.layout().addWidget(self.query)
        self.dialog.layout().addWidget(self.results)
        self._filtered_commands = [_FakeCommand("New conversation")]
        self.results.addItem("New conversation")
        self.calls: list[int] = []

    def _run_row(self, row: int) -> None:
        self.calls.append(row)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface(enabled: bool) -> tuple[QWidget, _FakePalette, CommandPaletteTruthController]:
    _app()
    window = QWidget()
    button = QPushButton("New", window)
    button.setEnabled(enabled)
    button.setProperty("pathenaEnablementReason", "A chat operation is still running.")
    button.setProperty(
        "pathenaEnablementRestoreCondition",
        "Wait for the current chat operation to finish.",
    )
    window.new_chat_button = button
    palette = _FakePalette(window)
    controller = CommandPaletteTruthController(palette)  # type: ignore[arg-type]
    return window, palette, controller


def test_disabled_target_exposes_existing_enablement_rationale() -> None:
    _window, _palette, controller = _surface(enabled=False)

    available, explanation = controller._availability("New conversation")

    assert available is False
    assert "chat operation is still running" in explanation
    assert "Wait for the current chat operation" in explanation


def test_disabled_palette_command_is_not_invoked() -> None:
    _window, palette, controller = _surface(enabled=False)

    controller._run_row(0)

    assert palette.calls == []
    assert controller.status.isVisible() is False or "Unavailable" in controller.status.text()


def test_enabled_palette_command_delegates_to_original_action() -> None:
    _window, palette, controller = _surface(enabled=True)

    controller._run_row(0)

    assert palette.calls == [0]


def test_refresh_marks_unavailable_command_without_removing_it() -> None:
    _window, palette, controller = _surface(enabled=False)

    controller.refresh()

    item = palette.results.item(0)
    assert item is not None
    assert item.text() == "New conversation · unavailable"
    assert palette.results.count() == 1
