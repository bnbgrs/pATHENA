from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLineEdit,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_command_palette_truth_6500 import (
    CommandPaletteTruthController,
)


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
        self.help_text = QPlainTextEdit(self.dialog)
        self.dialog.layout().addWidget(self.query)
        self.dialog.layout().addWidget(self.results)
        self._filtered_commands = [_FakeCommand("New conversation")]
        self._commands = tuple(self._filtered_commands)
        self.results.addItem("New conversation")
        self.calls: list[int] = []

    def _run_row(self, row: int) -> None:
        self.calls.append(row)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface(
    enabled: bool,
) -> tuple[QWidget, _FakePalette, CommandPaletteTruthController]:
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
    assert (
        controller.status.isVisible() is False
        or "Context required" in controller.status.text()
    )


def test_enabled_palette_command_delegates_to_original_action() -> None:
    _window, palette, controller = _surface(enabled=True)

    controller._run_row(0)

    assert palette.calls == [0]


def test_refresh_marks_unavailable_command_without_removing_it() -> None:
    _window, palette, controller = _surface(enabled=False)

    controller.refresh()

    item = palette.results.item(0)
    assert item is not None
    assert item.text() == "New conversation · context required"
    assert palette.results.count() == 1


def test_command_rows_expose_availability_and_current_scope_to_accessibility() -> None:
    _window, palette, controller = _surface(enabled=False)
    palette.results.setCurrentRow(0)

    controller.refresh()

    item = palette.results.item(0)
    assert item is not None
    assert item.data(Qt.ItemDataRole.AccessibleTextRole) == (
        "New conversation · context required"
    )
    description = str(item.data(Qt.ItemDataRole.AccessibleDescriptionRole))
    assert "Command context required" in description
    assert "chat operation is still running" in description
    assert palette.results.accessibleName() == "Command results"
    assert "1 command shown" in palette.results.accessibleDescription()
    assert "Current command: New conversation, context required" in (
        palette.results.accessibleDescription()
    )


def test_palette_rows_expose_shared_capability_catalog_contract() -> None:
    _window, palette, controller = _surface(enabled=False)

    controller.refresh()

    item = palette.results.item(0)
    assert item is not None
    assert item.data(257) == "context required"
    assert item.data(258) == "2026.08.25.1"
    assert palette.dialog.property("pathenaCapabilityCatalogVersion") == "2026.08.25.1"
    assert palette.dialog.property("pathenaCapabilityCatalogDrift") is True


def test_undocumented_live_command_fails_closed_and_cannot_execute() -> None:
    _window, palette, controller = _surface(enabled=True)
    palette._commands = (_FakeCommand("Undocumented live command"),)
    palette._filtered_commands = list(palette._commands)
    palette.results.clear()
    palette.results.addItem("Undocumented live command")

    controller.refresh()
    controller._run_row(0)

    item = palette.results.item(0)
    assert item is not None
    assert item.text() == "Undocumented live command · unavailable"
    assert "catalogue metadata is missing" in item.toolTip()
    assert palette.calls == []


def test_command_search_and_help_have_stable_assistive_semantics() -> None:
    _window, palette, _controller = _surface(enabled=True)

    assert palette.query.accessibleName() == "Command search"
    assert "existing pATHENA commands" in palette.query.accessibleDescription()
    assert palette.help_text.accessibleName() == "Help and capabilities"
    assert "Read-only guide" in palette.help_text.accessibleDescription()
