from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_dense_list_scanability_4900 import (
    DenseListScanabilityController,
    apply_ui_refinements_4801_4900,
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


def test_research_proposals_receive_accessibility_parity_from_shared_layer() -> None:
    app = _app()
    window = QWidget()
    listing = QListWidget(window)
    listing.setObjectName("researchProposalList")
    proposal = QListWidgetItem("01  CLAIM          PENDING     Evidence-backed statement")
    proposal.setData(Qt.ItemDataRole.UserRole, "proposal-123")
    proposal.setData(Qt.ItemDataRole.UserRole + 1, "pending")
    proposal.setData(Qt.ItemDataRole.UserRole + 2, "claim")
    listing.addItem(proposal)
    listing.setCurrentItem(proposal)

    apply_ui_refinements_4801_4900(window)
    app.processEvents()

    assert listing.property("pathenaDenseListAccessibility") is True
    assert proposal.data(Qt.ItemDataRole.AccessibleTextRole) == proposal.text()
    description = str(proposal.data(Qt.ItemDataRole.AccessibleDescriptionRole))
    assert "Research proposal row" in description
    assert "proposal-123" in description
    assert "Selected identity: proposal-123" in listing.accessibleDescription()
