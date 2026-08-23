from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QListWidgetItem

from athena.desktop.pathena_result_scope_clarity import ResultScopeController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _item(label: str, identity: str) -> QListWidgetItem:
    item = QListWidgetItem(label)
    item.setData(Qt.ItemDataRole.UserRole, identity)
    return item


def test_scope_reports_empty_list_without_selection() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()

    ResultScopeController._sync_one(items, scope, "Sources")

    assert scope.text() == "Sources · 0 items · none selected"
    assert scope.property("pathenaResultTotal") == 0
    assert scope.property("pathenaResultVisible") == 0


def test_scope_reports_total_and_selected_identity() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()
    items.addItem(_item("one", "12345678-aaaa"))
    items.addItem(_item("two", "abcdef12-bbbb"))
    items.setCurrentRow(1)

    ResultScopeController._sync_one(items, scope, "Research jobs")

    assert scope.text() == "Research jobs · 2 shown · selected ABCDEF12"
    assert scope.property("pathenaSelectedIdentity") == "selected ABCDEF12"


def test_scope_distinguishes_filtered_visible_count_from_total() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()
    first = _item("one", "12345678-aaaa")
    second = _item("two", "abcdef12-bbbb")
    items.addItem(first)
    items.addItem(second)
    first.setHidden(True)
    items.setCurrentItem(second)

    ResultScopeController._sync_one(items, scope, "Knowledge")

    assert scope.text() == "Knowledge · 1 shown / 2 total · selected ABCDEF12"
    assert scope.property("pathenaResultTotal") == 2
    assert scope.property("pathenaResultVisible") == 1


def test_scope_keeps_non_identity_selection_truthful() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()
    item = QListWidgetItem("row without canonical id")
    items.addItem(item)
    items.setCurrentItem(item)

    ResultScopeController._sync_one(items, scope, "Backup snapshots")

    assert scope.text() == "Backup snapshots · 1 shown · selection active"
