from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_selection_loading_5400 import SelectionLoadingController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_detail_busy_state_is_mirrored_without_changing_selection() -> None:
    _app()
    window = QWidget()
    listing = QListWidget(window)
    item = QListWidgetItem("RUNNING  Example")
    item.setData(Qt.ItemDataRole.UserRole, "entity-1")
    listing.addItem(item)
    listing.setCurrentItem(item)
    detail = QWidget(window)
    detail.setProperty("pathenaUiState", "busy")

    controller = SelectionLoadingController(window)
    controller.register(listing, detail, "research job")

    assert listing.currentItem() is item
    assert detail.property("pathenaUiState") == "busy"
    assert listing.property("pathenaDetailLoading") is True
    assert listing.property("pathenaSelectedDetailIdentity") == "entity-1"


def test_completion_keeps_selection_anchor_and_clears_loading_marker() -> None:
    _app()
    window = QWidget()
    listing = QListWidget(window)
    item = QListWidgetItem("COMPLETED  Example")
    item.setData(Qt.ItemDataRole.UserRole, "entity-1")
    listing.addItem(item)
    listing.setCurrentItem(item)
    detail = QWidget(window)
    detail.setProperty("pathenaUiState", "busy")

    controller = SelectionLoadingController(window)
    controller.register(listing, detail, "research job")
    detail.setProperty("pathenaUiState", "success")
    controller.sync()

    assert listing.currentItem() is item
    assert detail.property("pathenaUiState") == "success"
    assert listing.property("pathenaDetailLoading") is False
    assert listing.property("pathenaSelectionAnchored") is True
