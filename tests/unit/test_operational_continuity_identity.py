from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem

from athena.desktop.pathena_operational_continuity_3800 import (
    OperationalContinuityController,
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


def _item(label: str, identity: str) -> QListWidgetItem:
    item = QListWidgetItem(label)
    item.setData(Qt.ItemDataRole.UserRole, identity)
    return item


def test_restore_prefers_stable_identity_over_old_row(qt_app: QApplication) -> None:
    widget = QListWidget()
    widget.addItem(_item("new first", "b"))
    widget.addItem(_item("same object", "a"))

    OperationalContinuityController._restore_item_selection(
        widget,
        {"identity": "a", "row": 0},
    )

    assert widget.currentRow() == 1
    assert widget.currentItem().data(Qt.ItemDataRole.UserRole) == "a"


def test_missing_stable_identity_never_falls_back_to_old_row(
    qt_app: QApplication,
) -> None:
    widget = QListWidget()
    widget.addItem(_item("replacement", "b"))
    widget.setCurrentRow(-1)

    OperationalContinuityController._restore_item_selection(
        widget,
        {"identity": "a", "row": 0},
    )

    assert widget.currentRow() == -1


def test_row_fallback_remains_for_snapshots_without_identity(qt_app: QApplication) -> None:
    widget = QListWidget()
    widget.addItem(QListWidgetItem("row zero"))
    widget.addItem(QListWidgetItem("row one"))

    OperationalContinuityController._restore_item_selection(
        widget,
        {"identity": None, "row": 1},
    )

    assert widget.currentRow() == 1
