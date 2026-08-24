from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_research_proposal_density import (
    ResearchProposalDensityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _proposal(
    proposal_id: str,
    state: str,
    proposal_type: str,
    evidence: str,
) -> QListWidgetItem:
    item = QListWidgetItem(f"{proposal_type} · {state} · payload")
    item.setData(Qt.ItemDataRole.UserRole, proposal_id)
    item.setData(Qt.ItemDataRole.UserRole + 1, state)
    item.setData(Qt.ItemDataRole.UserRole + 2, proposal_type)
    item.setToolTip(f"{proposal_id}\nevidence={evidence}\naccepted_entity=-")
    return item


def _surface() -> tuple[SimpleNamespace, QListWidget]:
    _app()
    workspace = QWidget()
    root = QVBoxLayout(workspace)
    panel = QWidget(workspace)
    layout = QVBoxLayout(panel)
    status = QLabel("Review proposals", panel)
    proposals = QListWidget(panel)
    layout.addWidget(status)
    layout.addWidget(proposals)
    root.addWidget(panel)
    extension = SimpleNamespace(
        workspace=workspace,
        proposal_status=status,
        proposal_list=proposals,
        process=QProcess(workspace),
    )
    return extension, proposals


def test_summary_counts_pending_and_resolved_without_reordering() -> None:
    extension, proposals = _surface()
    proposals.addItem(_proposal("11111111-a", "pending", "knowledge", "claim:1"))
    proposals.addItem(_proposal("22222222-b", "accepted", "claim", "source:2"))
    original = [proposals.item(index).text() for index in range(proposals.count())]

    controller = ResearchProposalDensityController(extension)  # type: ignore[arg-type]

    assert controller.summary.text().startswith("2 proposals · 1 pending · 1 resolved")
    assert [proposals.item(index).text() for index in range(proposals.count())] == original
    assert proposals.property("pathenaProposalOrderPreserved") is True


def test_selected_summary_includes_identity_state_and_evidence() -> None:
    extension, proposals = _surface()
    item = _proposal("abcdef12-3456", "pending", "knowledge_unit", "claim:7")
    proposals.addItem(item)
    proposals.setCurrentItem(item)

    controller = ResearchProposalDensityController(extension)  # type: ignore[arg-type]
    controller.sync()

    assert "knowledge unit / pending / ABCDEF12" in controller.summary.text()
    assert "evidence claim:7" in controller.summary.text()


def test_empty_summary_is_quiet_and_explicit() -> None:
    extension, _proposals = _surface()

    controller = ResearchProposalDensityController(extension)  # type: ignore[arg-type]

    assert controller.summary.text() == "No promotion proposals loaded"
    assert controller.summary.property("pathenaProposalTotal") == 0


def test_items_receive_accessible_state_text() -> None:
    extension, proposals = _surface()
    item = _proposal("abcdef12-3456", "rejected", "claim", "source:3")
    proposals.addItem(item)

    controller = ResearchProposalDensityController(extension)  # type: ignore[arg-type]
    controller.sync()

    accessible = item.data(Qt.ItemDataRole.AccessibleTextRole)
    assert isinstance(accessible, str)
    assert "claim proposal, rejected" in accessible
