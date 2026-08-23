"""Presentation-only adapter for ResearchResult review and promotion."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QListWidgetItem, QPushButton, QWidget

if TYPE_CHECKING:
    from athena.desktop.research_results_extension import ResearchResultsExtension

_PRESENTED_ROLE = Qt.ItemDataRole.UserRole + 64


def _proposal_text(text: str) -> str | None:
    columns = tuple(
        part.strip()
        for part in re.split(r"\s{2,}", text.strip())
        if part.strip()
    )
    if len(columns) < 4 or not columns[0].isdigit():
        return None
    _ordinal, proposal_type, state = columns[:3]
    payload = "  ".join(columns[3:])
    return (
        f"{proposal_type.replace('_', ' ').title()} · "
        f"{state.replace('_', ' ').title()} · {payload}"
    )


def _present_item(item: QListWidgetItem) -> None:
    if item.data(_PRESENTED_ROLE) is True:
        return
    text = _proposal_text(item.text())
    if text is None:
        return
    item.setText(text)
    item.setData(_PRESENTED_ROLE, True)


def _sync(extension: ResearchResultsExtension) -> None:
    for index in range(extension.proposal_list.count()):
        _present_item(extension.proposal_list.item(index))

    for button in (
        extension.result_button,
        extension.propose_button,
        extension.refresh_proposals_button,
        extension.accept_button,
        extension.accept_separate_button,
        extension.reject_button,
    ):
        button.setVisible(button.isEnabled())

    status = extension.proposal_status.text()
    replacements = {
        "Select a completed Research run to inspect its result.": (
            "Select a completed research run to inspect its result."
        ),
        "Load proposals for the selected completed Research run.": (
            "Review knowledge proposals from the selected completed run."
        ),
        "Immutable ResearchResult and evidence loaded.": (
            "Research result and evidence loaded."
        ),
        "Research proposal accepted into canonical memory.": (
            "Proposal added to canonical memory."
        ),
        "Research proposal rejected/acknowledged.": "Proposal rejected.",
    }
    replacement = replacements.get(status)
    if replacement is not None:
        extension.proposal_status.setText(replacement)


def apply_research_result_presentation(extension: ResearchResultsExtension) -> None:
    """Make the real Research result flow quiet and state-dependent."""
    panel = extension.workspace.findChild(QWidget, "researchResultPanel")
    if panel is not None:
        for label in panel.findChildren(QLabel):
            if label.text() == "RESULT / PROMOTION":
                label.setText("Result & canonical memory")
                break

    extension.result_button.setText("View result")
    extension.result_button.setObjectName("researchResultButton")
    extension.propose_button.setText("Create proposals")
    extension.propose_button.setObjectName("researchProposeButton")
    extension.refresh_proposals_button.setText("Review proposals")
    extension.refresh_proposals_button.setObjectName("researchProposalRefreshButton")

    extension.accept_button.setText("Accept")
    extension.accept_button.setObjectName("researchProposalAcceptButton")
    extension.accept_button.setProperty("role", "primary")
    extension.accept_separate_button.setText("Keep separate")
    extension.accept_separate_button.setObjectName("researchProposalSeparateButton")
    extension.reject_button.setText("Reject")
    extension.reject_button.setObjectName("researchProposalRejectButton")

    extension.proposal_list.setMinimumHeight(120)
    extension.proposal_list.setToolTip(
        "Evidence-backed proposals; technical identity and evidence remain in each tooltip"
    )

    def schedule_sync(*_args: object) -> None:
        QTimer.singleShot(0, lambda: _sync(extension))

    extension.process.finished.connect(schedule_sync)
    extension.proposal_list.currentItemChanged.connect(schedule_sync)
    extension.workspace.jobs.currentItemChanged.connect(schedule_sync)
    _sync(extension)
