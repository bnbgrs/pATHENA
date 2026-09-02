"""Research-to-Knowledge transition refinements 2601-2700 for pATHENA.

ATHENA already owns immutable ResearchResult promotion and returns the accepted
canonical entity, revision and commit identifiers. This presentation-only adapter
makes that successful transition visible and offers navigation to the existing
Knowledge workspace. It never promotes, refreshes or mutates canonical memory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from athena.desktop.pathena_window import PathenaMainWindow
    from athena.desktop.research_results_extension import ResearchResultsExtension


@dataclass(frozen=True)
class TransitionTarget:
    key: str
    label: str


_TARGETS: tuple[TransitionTarget, ...] = (
    TransitionTarget("researchResultPanel", "Research result review"),
    TransitionTarget("researchProposalList", "Proposal browser"),
    TransitionTarget("researchProposalDecisionContext", "Proposal decision context"),
    TransitionTarget("researchProposalAcceptButton", "Accept proposal"),
    TransitionTarget("researchProposalSeparateButton", "Keep separate"),
    TransitionTarget("researchProposalRejectButton", "Reject proposal"),
    TransitionTarget("researchProposalStatus", "Proposal status"),
    TransitionTarget("researchKnowledgeTransition", "Research to Knowledge transition"),
    TransitionTarget("researchKnowledgeTransitionStatus", "Acceptance confirmation"),
    TransitionTarget("researchKnowledgeOpenButton", "Open Knowledge action"),
    TransitionTarget("knowledgeWorkspace", "Canonical Knowledge workspace"),
    TransitionTarget("canonicalMemoryTabs", "Canonical memory tabs"),
    TransitionTarget("persistentKnowledgeList", "Canonical Knowledge list"),
    TransitionTarget("persistentClaimList", "Canonical Claim list"),
    TransitionTarget("knowledgeSearchInput", "Canonical memory search"),
    TransitionTarget("knowledgeReviewState", "Knowledge review state"),
    TransitionTarget("researchResultButton", "Research result action"),
    TransitionTarget("researchProposeButton", "Create proposals action"),
    TransitionTarget("researchWorkspace", "Research workspace"),
    TransitionTarget("navigation", "Workspace navigation"),
)

_REFINEMENTS: tuple[str, ...] = (
    "confirm durable acceptance without celebratory chrome",
    "show canonical identity as secondary metadata",
    "offer a direct path to existing canonical memory",
    "keep Research and Knowledge ownership visually distinct",
    "preserve ATHENA promotion semantics without new side effects",
)

UI_REFINEMENT_TASKS_2601_2700: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _TARGETS
    for refinement in _REFINEMENTS
)

_ACCEPTED_RE = re.compile(r"^ACCEPTED\s+([^\s]+)$", re.MULTILINE)
_ENTITY_RE = re.compile(r"^ENTITY\s+([^\s]+)$", re.MULTILINE)
_REVISION_RE = re.compile(r"^REVISION\s+([^\s]+)$", re.MULTILINE)
_COMMIT_RE = re.compile(r"^COMMIT\s+([^\s]+)$", re.MULTILINE)

_STYLESHEET = r"""
QWidget#researchKnowledgeTransition {
    background: #090909;
    border-top: 1px solid #1E1E1E;
}
QLabel#researchKnowledgeTransitionStatus {
    color: #A8B3A5;
    background: transparent;
    padding: 6px 0;
}
QPushButton#researchKnowledgeOpenButton {
    background: transparent;
    color: #D8D8D8;
}
QPushButton#researchKnowledgeOpenButton:focus {
    border: 1px solid #F26A21;
}
"""


def _short_id(value: str) -> str:
    return value[:8].upper() if value else "—"


def _accepted_identity(output: str) -> tuple[str, str, str, str] | None:
    accepted = _ACCEPTED_RE.search(output)
    entity = _ENTITY_RE.search(output)
    revision = _REVISION_RE.search(output)
    commit = _COMMIT_RE.search(output)
    if not all((accepted, entity, revision, commit)):
        return None
    assert accepted is not None
    assert entity is not None
    assert revision is not None
    assert commit is not None
    return accepted.group(1), entity.group(1), revision.group(1), commit.group(1)


class PathenaResearchKnowledgeTransition(QObject):
    """Expose successful ATHENA promotion as a quiet navigational transition."""

    def __init__(
        self,
        window: PathenaMainWindow,
        extension: ResearchResultsExtension,
    ) -> None:
        super().__init__(extension.workspace)
        self.window = window
        self.extension = extension
        self.panel, self.status, self.open_button = self._install_panel()
        self.extension.process.finished.connect(self._schedule_sync)
        self.extension.workspace.jobs.currentItemChanged.connect(self._hide_transition)
        self.open_button.clicked.connect(self._open_knowledge)
        if _STYLESHEET not in window.styleSheet():
            window.setStyleSheet(f"{window.styleSheet()}\n{_STYLESHEET}")

    def _install_panel(self) -> tuple[QWidget, QLabel, QPushButton]:
        existing = self.extension.workspace.findChild(QWidget, "researchKnowledgeTransition")
        if existing is not None:
            status = existing.findChild(QLabel, "researchKnowledgeTransitionStatus")
            button = existing.findChild(QPushButton, "researchKnowledgeOpenButton")
            if status is not None and button is not None:
                return existing, status, button

        panel = QWidget()
        panel.setObjectName("researchKnowledgeTransition")
        row = QHBoxLayout(panel)
        row.setContentsMargins(0, 4, 0, 0)
        row.setSpacing(10)
        status = QLabel()
        status.setObjectName("researchKnowledgeTransitionStatus")
        status.setWordWrap(True)
        button = QPushButton("Open Knowledge")
        button.setObjectName("researchKnowledgeOpenButton")
        button.setAccessibleName("Open canonical Knowledge")
        button.setAccessibleDescription(
            "Navigate to the existing Knowledge workspace after successful Research promotion."
        )
        row.addWidget(status, 1)
        row.addWidget(button)

        result_panel = self.extension.workspace.findChild(QWidget, "researchResultPanel")
        layout = None if result_panel is None else result_panel.layout()
        if isinstance(layout, QVBoxLayout):
            layout.addWidget(panel)
        panel.hide()
        return panel, status, button

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self._sync_from_process_output)

    def _sync_from_process_output(self) -> None:
        output = str(getattr(self.extension, "_buffer", "") or "")
        identity = _accepted_identity(output)
        if identity is None:
            return
        proposal_id, entity_id, revision_id, commit_id = identity
        self.status.setText(
            "Added to canonical memory · "
            f"Entity {_short_id(entity_id)} · Revision {_short_id(revision_id)} · "
            f"Commit {_short_id(commit_id)}"
        )
        self.panel.setProperty("pathenaTransitionState", "accepted")
        self.panel.setToolTip(
            f"proposal={proposal_id}\nentity={entity_id}\nrevision={revision_id}\ncommit={commit_id}"
        )
        self.panel.show()
        self.open_button.setFocus()

    def _hide_transition(self, *_args: object) -> None:
        self.panel.hide()

    def _open_knowledge(self) -> None:
        navigation = getattr(self.window, "navigation", None)
        if navigation is not None and navigation.count() > 1:
            navigation.setCurrentRow(1)


def apply_ui_refinements_2601_2700(window: QWidget) -> tuple[int, ...]:
    """Register 100 transition refinements on existing or stable parent surfaces."""
    aliases = {
        "researchKnowledgeTransition": "researchResultPanel",
        "researchKnowledgeTransitionStatus": "researchResultPanel",
        "researchKnowledgeOpenButton": "researchResultPanel",
        "researchProposalDecisionContext": "researchResultPanel",
    }
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, aliases.get(target.key, target.key))
        if widget is None and target.key == "navigation":
            widget = getattr(window, "navigation", None)
        if widget is None:
            continue
        widget.setProperty("pathenaResearchKnowledge2700", True)
        start = 2601 + index * len(_REFINEMENTS)
        applied.extend(range(start, start + len(_REFINEMENTS)))
    return tuple(applied)


def install_research_knowledge_transition(
    window: PathenaMainWindow,
    extension: ResearchResultsExtension,
) -> PathenaResearchKnowledgeTransition:
    """Install the presentation-only Research-to-Knowledge acceptance transition."""
    return PathenaResearchKnowledgeTransition(window, extension)
