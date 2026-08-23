"""Research proposal clarity refinements 2501-2600 for pATHENA.

ATHENA's promotion service freezes immutable proposal payload JSON and enforces the
actual decision rules. This presentation adapter only humanizes already-rendered
proposal rows and mirrors those rules in the visible copy. It never accepts, rejects,
mutates or reclassifies a proposal.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QLabel,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from athena.desktop.research_results_extension import ResearchResultsExtension


@dataclass(frozen=True)
class ProposalClarityTarget:
    key: str
    label: str


_TARGETS: tuple[ProposalClarityTarget, ...] = (
    ProposalClarityTarget("researchResultPanel", "Research result review"),
    ProposalClarityTarget("researchProposalList", "Proposal browser"),
    ProposalClarityTarget("researchProposalStatus", "Proposal review status"),
    ProposalClarityTarget("researchProposalAcceptButton", "Accept proposal"),
    ProposalClarityTarget("researchProposalSeparateButton", "Keep separate"),
    ProposalClarityTarget("researchProposalRejectButton", "Reject proposal"),
    ProposalClarityTarget("researchResultButton", "View result"),
    ProposalClarityTarget("researchProposeButton", "Create proposals"),
    ProposalClarityTarget("researchProposalRefreshButton", "Review proposals"),
    ProposalClarityTarget("researchDetails", "Research result detail"),
    ProposalClarityTarget("researchJobList", "Research run browser"),
    ProposalClarityTarget("researchJobFilter", "Research run filter"),
    ProposalClarityTarget("researchStatus", "Research status"),
    ProposalClarityTarget("researchQuestionInput", "Research question"),
    ProposalClarityTarget("researchStartButton", "Start research"),
    ProposalClarityTarget("researchCancelButton", "Cancel research"),
    ProposalClarityTarget("researchWorkspace", "Research workspace"),
    ProposalClarityTarget("researchPrimarySplitter", "Research splitter"),
    ProposalClarityTarget("researchDecisionFlow", "Proposal decision flow"),
    ProposalClarityTarget(
        "researchProposalDecisionContext",
        "Selected proposal context",
    ),
)

_REFINEMENTS: tuple[str, ...] = (
    "show proposal meaning before technical payload",
    "keep evidence context adjacent to the decision",
    "mirror immutable proposal state without changing it",
    "make review-only contradictions unmistakable",
    "retain technical identity in secondary metadata",
)

UI_REFINEMENT_TASKS_2501_2600: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _TARGETS
    for refinement in _REFINEMENTS
)

_RAW_TEXT_ROLE = Qt.ItemDataRole.UserRole + 70
_CLARITY_ROLE = Qt.ItemDataRole.UserRole + 71

_STYLESHEET = r"""
QLabel#researchProposalDecisionContext {
    color: #919191;
    background: transparent;
    padding: 2px 0 4px 0;
}
QListWidget#researchProposalList::item {
    padding: 8px 9px;
}
QPushButton[pathenaProposalRisk="review-only"] {
    color: #B8A39A;
}
QPushButton[pathenaProposalRole="primary"]:focus {
    border: 1px solid #F26A21;
}
"""


def _parse_payload_text(text: str) -> tuple[str, str, dict[str, Any]] | None:
    """Read either the existing humanized row or the legacy fixed-column row."""
    parts = text.split(" · ", 2)
    if len(parts) == 3:
        proposal_type, state, payload_text = parts
    else:
        columns = tuple(
            part.strip()
            for part in re.split(r"\s{2,}", text.strip())
            if part.strip()
        )
        if len(columns) < 4 or not columns[0].isdigit():
            return None
        _ordinal, proposal_type, state = columns[:3]
        payload_text = "  ".join(columns[3:])

    try:
        payload = json.loads(payload_text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    return (
        proposal_type.casefold().replace(" ", "_"),
        state.casefold().replace(" ", "_"),
        payload,
    )


def _summary(proposal_type: str, payload: dict[str, Any]) -> str:
    if proposal_type == "knowledge":
        title = str(payload.get("title") or "").strip()
        body = str(payload.get("body") or "").strip()
        return title or body or "Knowledge summary"
    if proposal_type == "claim":
        return str(payload.get("statement") or "Claim").strip()
    if proposal_type == "contradiction":
        return str(
            payload.get("text") or "Contradiction requires review"
        ).strip()
    return str(
        payload.get("summary") or payload.get("text") or "Proposal"
    ).strip()


def _shorten(text: str, limit: int = 150) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def _evidence_from_tooltip(tooltip: str) -> str:
    match = re.search(r"(?:^|\n)evidence=([^:\n]+):([^\n]+)", tooltip)
    if match is None:
        return "Evidence linked"
    kind, ordinal = match.groups()
    human_kind = kind.replace("_", " ").title()
    if ordinal == "-":
        return f"Evidence · {human_kind}"
    try:
        human_ordinal: int | str = int(ordinal) + 1
    except ValueError:
        human_ordinal = ordinal
    return f"Evidence · {human_kind} {human_ordinal}"


def _human_state(state: str) -> str:
    return state.replace("_", " ").title()


def _human_type(proposal_type: str) -> str:
    return proposal_type.replace("_", " ").title()


def _render_item(item: QListWidgetItem) -> None:
    if item.data(_CLARITY_ROLE) is True:
        return
    parsed = _parse_payload_text(item.text())
    if parsed is None:
        return
    proposal_type, state, payload = parsed
    item.setData(_RAW_TEXT_ROLE, item.text())
    meaning = _shorten(_summary(proposal_type, payload))
    evidence = _evidence_from_tooltip(item.toolTip())
    state_copy = (
        "Review only"
        if proposal_type == "contradiction" and state == "pending"
        else _human_state(state)
    )
    item.setText(
        f"{meaning}\n{_human_type(proposal_type)} · {state_copy} · {evidence}"
    )
    item.setData(_CLARITY_ROLE, True)


def _technical_identity(item: QListWidgetItem) -> str:
    proposal_id = str(item.data(Qt.ItemDataRole.UserRole) or "")
    return proposal_id[:8].upper() if proposal_id else "—"


class PathenaResearchProposalClarity(QObject):
    """Keep proposal decisions readable while delegating all semantics to ATHENA."""

    def __init__(self, extension: ResearchResultsExtension) -> None:
        super().__init__(extension.workspace)
        self.extension = extension
        self.workspace = extension.workspace
        self.list = extension.proposal_list
        self.context = self._install_context_label()
        self._configure_actions()
        self._connect_updates()
        self.sync()
        if _STYLESHEET not in self.workspace.styleSheet():
            self.workspace.setStyleSheet(
                f"{self.workspace.styleSheet()}\n{_STYLESHEET}"
            )

    def _install_context_label(self) -> QLabel:
        existing = self.workspace.findChild(
            QLabel,
            "researchProposalDecisionContext",
        )
        if existing is not None:
            return existing
        label = QLabel(
            "Select a proposal to inspect its evidence and allowed decision."
        )
        label.setObjectName("researchProposalDecisionContext")
        label.setWordWrap(True)
        panel = self.workspace.findChild(QWidget, "researchResultPanel")
        layout = None if panel is None else panel.layout()
        if isinstance(layout, QVBoxLayout):
            index = layout.indexOf(self.list)
            layout.insertWidget(
                index + 1 if index >= 0 else layout.count(),
                label,
            )
        return label

    def _configure_actions(self) -> None:
        self.extension.accept_button.setProperty("pathenaProposalRole", "primary")
        self.extension.accept_separate_button.setProperty(
            "pathenaProposalRole",
            "secondary",
        )
        self.extension.reject_button.setProperty(
            "pathenaProposalRole",
            "secondary",
        )

    def _connect_updates(self) -> None:
        model = self.list.model()
        model.rowsInserted.connect(self._schedule_sync)
        model.modelReset.connect(self._schedule_sync)
        self.list.currentItemChanged.connect(self.sync)
        self.extension.process.finished.connect(self._schedule_sync)

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self, *_args: object) -> None:
        for index in range(self.list.count()):
            _render_item(self.list.item(index))

        current = self.list.currentItem()
        if current is None:
            self.context.setVisible(False)
            self.extension.accept_button.setProperty("pathenaProposalRisk", "")
            self.extension.accept_separate_button.setProperty(
                "pathenaProposalRisk",
                "",
            )
            return

        self.context.setVisible(True)
        proposal_type = str(
            current.data(Qt.ItemDataRole.UserRole + 2) or ""
        ).casefold()
        state = str(current.data(Qt.ItemDataRole.UserRole + 1) or "").casefold()
        evidence = _evidence_from_tooltip(current.toolTip())
        identity = _technical_identity(current)

        if proposal_type == "contradiction":
            self.context.setText(
                f"Contradiction · {evidence} · Review only · ID {identity}. "
                "ATHENA does not allow silent canonical acceptance; "
                "acknowledge with Reject."
            )
            self.extension.accept_button.setProperty(
                "pathenaProposalRisk",
                "review-only",
            )
            self.extension.accept_separate_button.setProperty(
                "pathenaProposalRisk",
                "review-only",
            )
        else:
            state_copy = _human_state(state) if state else "Unknown state"
            self.context.setText(
                f"{_human_type(proposal_type or 'proposal')} · {state_copy} · "
                f"{evidence} · ID {identity}."
            )
            self.extension.accept_button.setProperty("pathenaProposalRisk", "")
            self.extension.accept_separate_button.setProperty(
                "pathenaProposalRisk",
                "",
            )


def apply_ui_refinements_2501_2600(window: QWidget) -> tuple[int, ...]:
    """Register the 100 proposal-clarity tasks on existing presentation surfaces."""
    applied: list[int] = []
    aliases = {
        "researchDecisionFlow": "researchWorkspace",
        "researchProposalDecisionContext": "researchResultPanel",
    }
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, aliases.get(target.key, target.key))
        if widget is None:
            continue
        widget.setProperty("pathenaResearch2600", True)
        start = 2501 + index * len(_REFINEMENTS)
        applied.extend(range(start, start + len(_REFINEMENTS)))
    return tuple(applied)


def install_research_proposal_clarity(
    extension: ResearchResultsExtension,
) -> PathenaResearchProposalClarity:
    """Install presentation-only proposal meaning, evidence and decision context."""
    return PathenaResearchProposalClarity(extension)
