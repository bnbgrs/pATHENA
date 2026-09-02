from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_state_transition_integrity_4600 import (
    StateTransitionIntegrityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _selection_with_ids(*identities: str) -> QListWidget:
    selection = QListWidget()
    for identity in identities:
        item = QListWidgetItem(identity.upper())
        item.setData(Qt.ItemDataRole.UserRole, identity)
        selection.addItem(item)
    selection.setCurrentRow(0)
    return selection


def test_selection_change_clears_coverage_owned_terminal_state() -> None:
    _app()
    window = QWidget()
    selection = _selection_with_ids("first", "second")
    detail = QWidget(window)
    detail.setProperty("pathenaUiState", "error")
    detail.setProperty("pathenaCoverageOwnedState", "error")

    controller = StateTransitionIntegrityController(window)
    controller.register(selection, detail, "test entity")

    selection.setCurrentRow(1)

    assert detail.property("pathenaUiState") == "idle"
    assert detail.property("pathenaCoverageOwnedState") == ""
    assert detail.property("pathenaSelectionStateReset") is True
    assert detail.property("pathenaSelectionScopeIdentity") == "second"


def test_selection_change_does_not_clear_busy_work() -> None:
    _app()
    window = QWidget()
    selection = _selection_with_ids("first", "second")
    detail = QWidget(window)
    detail.setProperty("pathenaUiState", "error")
    detail.setProperty("pathenaCoverageOwnedState", "error")
    detail.setProperty("pathenaLongRunningWork", True)

    controller = StateTransitionIntegrityController(window)
    controller.register(selection, detail, "test entity")

    selection.setCurrentRow(1)

    assert detail.property("pathenaUiState") == "error"
    assert detail.property("pathenaCoverageOwnedState") == "error"
    assert detail.property("pathenaSelectionStateResetDeferred") is True


def test_selection_change_preserves_externally_owned_state() -> None:
    _app()
    window = QWidget()
    selection = _selection_with_ids("first", "second")
    detail = QWidget(window)
    detail.setProperty("pathenaUiState", "error")
    detail.setProperty("pathenaCoverageOwnedState", "")

    controller = StateTransitionIntegrityController(window)
    controller.register(selection, detail, "test entity")

    selection.setCurrentRow(1)

    assert detail.property("pathenaUiState") == "error"
    assert detail.property("pathenaCoverageOwnedState") == ""
    assert not bool(detail.property("pathenaSelectionStateReset"))
