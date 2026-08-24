from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

from athena.desktop.app import create_application
from athena.desktop.pathena_research_result_presentation import (
    _proposal_text,
    _sync,
    apply_research_result_presentation,
)
from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_workspace import ResearchWorkspace


def _app() -> QApplication:
    return create_application(["pathena-research-result-presentation-test"])


def test_proposal_copy_removes_cli_padding_without_losing_payload() -> None:
    assert _proposal_text(
        "01  KNOWLEDGE      PENDING     A durable evidence-backed proposal"
    ) == "Knowledge · Pending · A durable evidence-backed proposal"


def test_research_result_actions_are_progressively_disclosed() -> None:
    app = _app()
    workspace = ResearchWorkspace()
    extension = ResearchResultsExtension(workspace)
    extension.refresh_timer.stop()
    try:
        apply_research_result_presentation(extension)
        app.processEvents()

        panel = workspace.findChild(QLabel)
        headings = {label.text() for label in workspace.findChildren(QLabel)}
        assert panel is not None
        assert "Result & canonical memory" in headings
        assert extension.result_button.text() == "View result"
        assert extension.propose_button.text() == "Create proposals"
        assert extension.refresh_proposals_button.text() == "Review proposals"
        assert extension.accept_button.property("role") == "primary"

        assert extension.result_button.isHidden()
        assert extension.accept_button.isHidden()
        assert extension.reject_button.isHidden()

        extension.proposal_list.addItem(
            "01  KNOWLEDGE      PENDING     A durable evidence-backed proposal"
        )
        item = extension.proposal_list.item(0)
        item.setData(Qt.ItemDataRole.UserRole + 1, "pending")
        item.setData(Qt.ItemDataRole.UserRole + 2, "knowledge")
        extension.proposal_list.setCurrentRow(0)
        extension.accept_button.setEnabled(True)
        extension.accept_separate_button.setEnabled(True)
        extension.reject_button.setEnabled(True)
        _sync(extension)
        app.processEvents()

        assert item.text() == "Knowledge · Pending · A durable evidence-backed proposal"
        assert extension.accept_button.isHidden() is False
        assert extension.accept_separate_button.isHidden() is False
        assert extension.reject_button.isHidden() is False

        extension.accept_button.setEnabled(False)
        extension.accept_separate_button.setEnabled(False)
        _sync(extension)
        assert extension.accept_button.isHidden()
        assert extension.accept_separate_button.isHidden()
        assert extension.reject_button.isHidden() is False
    finally:
        extension.refresh_timer.stop()
        workspace.close()
        app.processEvents()
