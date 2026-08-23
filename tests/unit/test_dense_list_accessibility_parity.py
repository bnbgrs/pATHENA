from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_dense_list_scanability_4900 import (
    apply_ui_refinements_4801_4900,
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


def _list(parent: QWidget, object_name: str, text: str, identity: str) -> QListWidget:
    widget = QListWidget(parent)
    widget.setObjectName(object_name)
    item = QListWidgetItem(text)
    item.setData(Qt.ItemDataRole.UserRole, identity)
    widget.addItem(item)
    widget.setCurrentItem(item)
    return widget


def test_knowledge_claim_and_decision_rows_expose_accessible_identity(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    layout = QVBoxLayout(window)
    knowledge = _list(
        window,
        "persistentKnowledgeList",
        "Capital of France · Paris",
        "knowledge-123",
    )
    claims = _list(
        window,
        "persistentClaimList",
        "Paris is the capital of France",
        "claim-456",
    )
    decisions = _list(
        window,
        "semanticReviewList",
        "Contradiction pending",
        "review-789",
    )
    for widget in (knowledge, claims, decisions):
        layout.addWidget(widget)

    apply_ui_refinements_4801_4900(window)

    for widget, identity in (
        (knowledge, "knowledge-123"),
        (claims, "claim-456"),
        (decisions, "review-789"),
    ):
        item = widget.currentItem()
        assert item is not None
        assert item.data(Qt.ItemDataRole.AccessibleTextRole) == item.text()
        description = str(item.data(Qt.ItemDataRole.AccessibleDescriptionRole))
        assert identity in description
        assert identity in widget.accessibleDescription()
        assert widget.property("pathenaDenseListAccessibility") is True


def test_accessibility_scope_does_not_claim_hidden_rows_are_shown(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    knowledge = _list(
        window,
        "persistentKnowledgeList",
        "Visible knowledge",
        "knowledge-visible",
    )
    hidden = QListWidgetItem("Filtered knowledge")
    hidden.setData(Qt.ItemDataRole.UserRole, "knowledge-hidden")
    knowledge.addItem(hidden)
    hidden.setHidden(True)

    apply_ui_refinements_4801_4900(window)

    description = knowledge.accessibleDescription()
    assert "2 total Knowledge items in the list model" in description
    assert "2 shown" not in description


def test_accessibility_parity_does_not_extend_existing_refinement_ids(
    qt_app: QApplication,
) -> None:
    window = QWidget()
    layout = QVBoxLayout(window)
    for object_name in (
        "researchJobList",
        "durableJobList",
        "sourceList",
        "backupSnapshotList",
        "persistentKnowledgeList",
        "persistentClaimList",
        "semanticReviewList",
    ):
        widget = QListWidget(window)
        widget.setObjectName(object_name)
        layout.addWidget(widget)

    applied = apply_ui_refinements_4801_4900(window)

    assert applied == tuple(range(4801, 4881))
    assert window.property("pathenaDenseListAccessibilityParityCount") == 6
