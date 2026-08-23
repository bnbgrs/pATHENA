from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_dense_list_scanability_4900 import (
    DenseListScanabilityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_selected_entity_identity_tracks_user_role() -> None:
    _app()
    window = QWidget()
    listing = QListWidget(window)
    item = QListWidgetItem("RUNNING  45.0%  Example query")
    item.setData(Qt.ItemDataRole.UserRole, "job-123")
    listing.addItem(item)

    controller = DenseListScanabilityController(window)
    controller.register(listing, "research job")
    listing.setCurrentItem(item)

    assert listing.property("pathenaSelectedEntityIdentity") == "job-123"
    assert listing.property("pathenaSelectedEntityPresent") is True
    assert "Example query" in str(listing.property("pathenaSelectedEntitySummary"))
    assert "Selected research job" in listing.statusTip()


def test_empty_selection_clears_identity_without_changing_rows() -> None:
    _app()
    window = QWidget()
    listing = QListWidget(window)
    listing.addItem(QListWidgetItem("QUEUED  0.0%  Example query"))

    controller = DenseListScanabilityController(window)
    controller.register(listing, "research job")
    listing.setCurrentRow(0)
    listing.clearSelection()
    listing.setCurrentItem(None)

    assert listing.count() == 1
    assert listing.property("pathenaSelectedEntityIdentity") == ""
    assert listing.property("pathenaSelectedEntityPresent") is False
    assert listing.statusTip() == "No research job selected."
