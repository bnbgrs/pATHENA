from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_accessible_state_sync_5600 import (
    AccessibleStateSyncController,
)


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def _selected_list() -> QListWidget:
    widget = QListWidget()
    item = QListWidgetItem("Selected row")
    item.setData(Qt.ItemDataRole.UserRole, "12345678-selected")
    widget.addItem(item)
    widget.setCurrentItem(item)
    return widget


def test_result_scope_survives_semantic_state_change(qt_app: QApplication) -> None:
    window = QWidget()
    widget = _selected_list()
    widget.setParent(window)
    controller = AccessibleStateSyncController(window)
    controller.register(widget, "Research jobs")
    widget.setProperty(
        "pathenaResultScopeText",
        "Research jobs · 1 shown / 2 total · selected 12345678",
    )
    widget.setProperty("pathenaUiState", "busy")

    controller._sync_one(widget)

    description = widget.accessibleDescription()
    assert "Research jobs · 1 shown / 2 total · selected 12345678" in description
    assert "State: working." in description


def test_backup_scope_has_priority_when_state_sync_runs(qt_app: QApplication) -> None:
    window = QWidget()
    widget = _selected_list()
    widget.setParent(window)
    controller = AccessibleStateSyncController(window)
    controller.register(widget, "Backup snapshots")
    widget.setProperty(
        "pathenaResultScopeText",
        "Backup snapshots · 2 shown · selected 12345678",
    )
    widget.setProperty(
        "pathenaBackupListScope",
        "2 backup snapshots listed. Selected 12345678: state complete, "
        "verification verified deep, restore available.",
    )
    widget.setProperty("pathenaUiState", "success")

    controller._sync_one(widget)

    description = widget.accessibleDescription()
    assert description.startswith("2 backup snapshots listed.")
    assert "restore available" in description
    assert "State: complete." in description


def test_result_scope_retains_existing_cancellation_phase(qt_app: QApplication) -> None:
    window = QWidget()
    widget = _selected_list()
    widget.setParent(window)
    controller = AccessibleStateSyncController(window)
    controller.register(widget, "Durable jobs")
    widget.setProperty(
        "pathenaResultScopeText",
        "Durable jobs · 1 shown · selected 12345678",
    )
    widget.setProperty("pathenaCancellationPhase", "requested")
    widget.setProperty("pathenaCancellationSelectedState", "cancel_requested")
    widget.setProperty("pathenaUiState", "idle")

    controller._sync_one(widget)

    description = widget.accessibleDescription()
    assert "Durable jobs · 1 shown · selected 12345678" in description
    assert "State: ready." in description
    assert "Cancellation: phase requested" in description
    assert "selected job state cancel_requested" in description


def test_vanished_selection_remains_authoritative_after_scope_and_state_sync(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    widget = _selected_list()
    widget.setParent(window)
    controller = AccessibleStateSyncController(window)
    controller.register(widget, "Sources")
    widget.clear()
    widget.setProperty(
        "pathenaResultScopeText",
        "Sources · 0 shown / 1 total · none selected",
    )
    widget.setProperty("pathenaSelectionDisappeared", "abcdef12-vanished")
    widget.setProperty("pathenaUiState", "idle")

    controller._sync_one(widget)

    description = widget.accessibleDescription()
    assert description.startswith(
        "Previously selected item ABCDEF12 is no longer listed after refresh."
    )
    assert "Sources · 0 shown / 1 total · none selected" in description
    assert "State: ready." in description
    assert widget.property("pathenaAccessibleSelectionDisappeared") == (
        "abcdef12-vanished"
    )
