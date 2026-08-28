from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_result_scope_clarity import ResultScopeController


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def _item(text: str, identity: str) -> QListWidgetItem:
    item = QListWidgetItem(text)
    item.setData(Qt.ItemDataRole.UserRole, identity)
    return item


def test_filtered_result_scope_is_mirrored_to_list_accessibility(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    results = QListWidget(window)
    scope = QLabel(window)
    visible = _item("Visible", "12345678-visible")
    hidden = _item("Hidden", "87654321-hidden")
    results.addItem(visible)
    results.addItem(hidden)
    hidden.setHidden(True)
    results.setCurrentItem(visible)

    ResultScopeController._sync_one(results, scope, "Research jobs")

    expected = "Research jobs · 1 shown / 2 total · selected 12345678"
    assert scope.text() == expected
    assert results.accessibleDescription() == expected
    assert results.property("pathenaResultScopeText") == expected
    assert results.property("pathenaResultTotal") == 2
    assert results.property("pathenaResultVisible") == 1


def test_filtered_selected_item_is_announced_as_filtered(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    results = QListWidget(window)
    scope = QLabel(window)
    visible = _item("Visible", "12345678-visible")
    hidden = _item("Hidden", "87654321-hidden")
    results.addItem(visible)
    results.addItem(hidden)
    hidden.setHidden(True)
    results.setCurrentItem(hidden)

    ResultScopeController._sync_one(results, scope, "Knowledge")

    expected = "Knowledge · 1 shown / 2 total · selected 87654321 (filtered)"
    assert results.accessibleDescription() == expected
    assert results.property("pathenaSelectedIdentity") == "selected 87654321 (filtered)"
