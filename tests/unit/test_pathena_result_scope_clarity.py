from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_result_scope_clarity import (
    KnowledgeTabbedScopeController,
    ResultScopeController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _item(label: str, identity: str) -> QListWidgetItem:
    item = QListWidgetItem(label)
    item.setData(Qt.ItemDataRole.UserRole, identity)
    return item


def _knowledge_surface() -> tuple[QWidget, QLabel, QTabWidget]:
    _app()
    workspace = QWidget()
    QVBoxLayout(workspace)
    workspace.browser_tabs = QTabWidget(workspace)  # type: ignore[attr-defined]
    workspace.search_input = QLineEdit(workspace)  # type: ignore[attr-defined]
    workspace.search_input.setObjectName("knowledgeSearchInput")  # type: ignore[attr-defined]
    workspace.knowledge_list = QListWidget(workspace)  # type: ignore[attr-defined]
    workspace.claim_list = QListWidget(workspace)  # type: ignore[attr-defined]
    workspace.review_list = QListWidget(workspace)  # type: ignore[attr-defined]
    for label in ("Knowledge", "Claims", "Decisions", "Session review"):
        workspace.browser_tabs.addTab(QWidget(), label)  # type: ignore[attr-defined]
    scope = QLabel(workspace)
    return workspace, scope, workspace.browser_tabs  # type: ignore[attr-defined]


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


def test_hidden_selection_is_explicitly_marked_filtered() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()
    item = _item("hidden", "abcdef12-bbbb")
    items.addItem(item)
    items.setCurrentItem(item)
    item.setHidden(True)

    ResultScopeController._sync_one(items, scope, "Claims")

    assert scope.text() == "Claims · 0 shown / 1 total · selected ABCDEF12 (filtered)"


def test_scope_keeps_non_identity_selection_truthful() -> None:
    _app()
    items = QListWidget()
    scope = QLabel()
    item = QListWidgetItem("row without canonical id")
    items.addItem(item)
    items.setCurrentItem(item)

    ResultScopeController._sync_one(items, scope, "Backup snapshots")

    assert scope.text() == "Backup snapshots · 1 shown · selection active"


def test_filter_signal_resynchronizes_hidden_research_rows() -> None:
    app = _app()
    owner = QWidget()
    items = QListWidget(owner)
    scope = QLabel(owner)
    filter_input = QLineEdit(owner)
    filter_input.setObjectName("researchJobFilter")
    first = _item("alpha", "12345678-aaaa")
    second = _item("beta", "abcdef12-bbbb")
    items.addItem(first)
    items.addItem(second)
    items.setCurrentItem(second)
    filter_input.textChanged.connect(lambda text: first.setHidden(bool(text)))
    controller = ResultScopeController(owner)
    controller.register(items, scope, "Research jobs", filter_input)

    filter_input.setText("beta")
    app.processEvents()

    assert scope.text() == "Research jobs · 1 shown / 2 total · selected ABCDEF12"
    assert scope.property("pathenaResultScopeFilterBound") == "researchJobFilter"


def test_knowledge_scope_tracks_claims_and_decisions_tabs() -> None:
    workspace, scope, tabs = _knowledge_surface()
    claim = _item("claim", "11111111-aaaa")
    decision = _item("decision", "22222222-bbbb")
    workspace.claim_list.addItem(claim)  # type: ignore[attr-defined]
    workspace.review_list.addItem(decision)  # type: ignore[attr-defined]
    workspace.claim_list.setCurrentItem(claim)  # type: ignore[attr-defined]
    workspace.review_list.setCurrentItem(decision)  # type: ignore[attr-defined]
    controller = KnowledgeTabbedScopeController(workspace, scope)

    tabs.setCurrentIndex(1)
    controller.sync()
    assert scope.text() == "Claims · 1 shown · selected 11111111"

    tabs.setCurrentIndex(2)
    controller.sync()
    assert scope.text() == "Decisions · 1 shown · selected 22222222"


def test_session_review_scope_does_not_invent_a_count() -> None:
    workspace, scope, tabs = _knowledge_surface()
    controller = KnowledgeTabbedScopeController(workspace, scope)

    tabs.setCurrentIndex(3)
    controller.sync()

    assert scope.text() == "Session review · scope is shown inside the review panel"
    assert scope.property("pathenaResultScopeMode") == "session-review"
    assert scope.property("pathenaResultTotal") is None
