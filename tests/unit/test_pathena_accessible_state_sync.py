from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_accessible_state_sync_5600 import (
    AccessibleStateSyncController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_semantic_state_updates_accessible_copy() -> None:
    app = _app()
    window = QWidget()
    status = QLabel("Refreshing research", window)
    status.setProperty("pathenaUiState", "busy")

    controller = AccessibleStateSyncController(window)
    controller.register(status, "Research status")

    assert status.accessibleName() == "Research status — working"
    assert "Research status is working." in status.accessibleDescription()
    first_count = status.property("pathenaAccessibleSyncCount")

    status.setProperty("pathenaUiState", "error")
    app.processEvents()
    controller.sync()

    assert status.accessibleName() == "Research status — needs attention"
    assert "needs attention" in status.accessibleDescription()
    assert int(status.property("pathenaAccessibleSyncCount")) > int(first_count)


def test_list_selection_identity_is_synchronized() -> None:
    app = _app()
    window = QWidget()
    listing = QListWidget(window)
    first = QListWidgetItem("First visible row")
    first.setData(Qt.ItemDataRole.UserRole, "job-001")
    second = QListWidgetItem("Second visible row")
    second.setData(Qt.ItemDataRole.UserRole, "job-002")
    listing.addItem(first)
    listing.addItem(second)
    listing.setProperty("pathenaUiState", "success")

    controller = AccessibleStateSyncController(window)
    controller.register(listing, "Research jobs")
    listing.setCurrentItem(first)
    app.processEvents()
    controller.sync()

    assert listing.property("pathenaAccessibleSelectionIdentity") == "job-001"
    assert "selected job-001" in listing.accessibleName()

    listing.setCurrentItem(second)
    app.processEvents()
    controller.sync()

    assert listing.property("pathenaAccessibleSelectionIdentity") == "job-002"
    assert "Selected item: job-002." in listing.accessibleDescription()


def test_unchanged_signature_does_not_increment_sync_count() -> None:
    _app()
    window = QWidget()
    status = QLabel("Ready", window)

    controller = AccessibleStateSyncController(window)
    controller.register(status, "System runtime")
    count = status.property("pathenaAccessibleSyncCount")

    controller.sync()
    controller.sync()

    assert status.property("pathenaAccessibleSyncCount") == count
