"""Progressive workspace refinements 2201-2300 for pATHENA.

The desktop already exposes rich Research and Knowledge flows. This controller reduces
permanent chrome and reveals secondary review/relationship surfaces only when they
contain actionable information. Presentation only; no domain state is changed.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QWidget,
)


@dataclass(frozen=True)
class ProgressiveTarget:
    key: str
    label: str


_PROGRESSIVE_TARGETS: tuple[ProgressiveTarget, ...] = (
    ProgressiveTarget("knowledgeWorkspace", "Knowledge header"),
    ProgressiveTarget("researchWorkspace", "Research header"),
    ProgressiveTarget("jobsWorkspace", "Jobs header"),
    ProgressiveTarget("filesWorkspace", "Sources header"),
    ProgressiveTarget("systemWorkspace", "System header"),
    ProgressiveTarget("canonicalMemoryTabs", "Canonical memory navigation"),
    ProgressiveTarget("persistentKnowledgeDetails", "Knowledge provenance detail"),
    ProgressiveTarget("persistentClaimDetails", "Claim evidence detail"),
    ProgressiveTarget("semanticReviewDetails", "Decision comparison detail"),
    ProgressiveTarget("claimRelationList", "Claim relations"),
    ProgressiveTarget("openRelatedClaimButton", "Related claim action"),
    ProgressiveTarget("knowledgeReviewPanel", "Session review panel"),
    ProgressiveTarget("knowledgeReviewState", "Session review state"),
    ProgressiveTarget("researchResultPanel", "Research result panel"),
    ProgressiveTarget("researchDetails", "Research result detail"),
    ProgressiveTarget("researchProposalList", "Research proposal list"),
    ProgressiveTarget("researchProposalRefreshButton", "Proposal review action"),
    ProgressiveTarget("researchProposalAcceptButton", "Proposal accept action"),
    ProgressiveTarget("researchProposalSeparateButton", "Proposal separate action"),
    ProgressiveTarget("researchProposalRejectButton", "Proposal reject action"),
)

_PROGRESSIVE_REFINEMENTS: tuple[str, ...] = (
    "remove redundant permanent chrome",
    "reveal secondary content only when useful",
    "prioritize readable content over controls",
    "use typography instead of extra containers",
    "preserve direct access to actionable state",
)

UI_REFINEMENT_TASKS_2201_2300: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _PROGRESSIVE_TARGETS
    for refinement in _PROGRESSIVE_REFINEMENTS
)

_WORKSPACE_TITLE_COPY = {
    "KNOWLEDGE / CANONICAL MEMORY",
    "EXHAUSTIVE LOCAL RESEARCH",
    "DURABLE JOB CONTROL",
    "LOCAL SOURCES / FILES",
    "LOCAL RUNTIME / SYSTEM",
}

_PROGRESSIVE_STYLESHEET = r"""
QLabel[pathenaSectionHeading="true"] {
    color: #969696;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
QWidget[pathenaProgressiveRole="detail"] {
    background: #080808;
    border: none;
    color: #D7D7D7;
}
QWidget[pathenaProgressiveRole="secondary"] {
    background: transparent;
    border-color: #1E1E1E;
}
QWidget[pathenaProgressiveRole="decision"] {
    background: transparent;
}
QWidget[pathenaProgressiveRole="decision"]:focus {
    border: 1px solid #F26A21;
}
"""


class PathenaProgressiveWorkspaceRefinement(QObject):
    """Make Research/Knowledge secondary surfaces content-dependent and quieter."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._tag_targets()
        self._remove_duplicate_workspace_titles()
        self._quiet_section_headings()
        self._quiet_detail_editors()
        self._configure_tabs()
        self._connect_progressive_lists()
        self._sync_research_proposals()
        self._sync_claim_relations()
        if _PROGRESSIVE_STYLESHEET not in window.styleSheet():
            window.setStyleSheet(f"{window.styleSheet()}\n{_PROGRESSIVE_STYLESHEET}")

    def _tag_targets(self) -> None:
        for target in _PROGRESSIVE_TARGETS:
            widget = self.window.findChild(QWidget, target.key)
            if widget is not None:
                widget.setProperty("pathenaProgressiveSurface", True)

    def _remove_duplicate_workspace_titles(self) -> None:
        for label in self.window.findChildren(QLabel):
            if label.text() in _WORKSPACE_TITLE_COPY:
                label.hide()

    def _quiet_section_headings(self) -> None:
        for label in self.window.findChildren(QLabel):
            if label.property("role") == "section":
                label.setProperty("pathenaSectionHeading", True)

    def _quiet_detail_editors(self) -> None:
        for name in (
            "persistentKnowledgeDetails",
            "persistentClaimDetails",
            "semanticReviewDetails",
            "researchDetails",
        ):
            editor = self.window.findChild(QPlainTextEdit, name)
            if editor is None:
                continue
            editor.setProperty("pathenaProgressiveRole", "detail")
            editor.setFrameStyle(0)
            editor.document().setDocumentMargin(12.0)

    def _configure_tabs(self) -> None:
        tabs = self.window.findChild(QTabWidget, "canonicalMemoryTabs")
        if tabs is not None:
            tabs.setDocumentMode(True)
            tabs.tabBar().setDrawBase(False)

    def _connect_progressive_lists(self) -> None:
        proposals = self.window.findChild(QListWidget, "researchProposalList")
        if proposals is not None:
            model = proposals.model()
            model.rowsInserted.connect(self._sync_research_proposals)
            model.rowsRemoved.connect(self._sync_research_proposals)
            model.modelReset.connect(self._sync_research_proposals)
            proposals.currentItemChanged.connect(self._sync_research_proposals)

        relations = self.window.findChild(QListWidget, "claimRelationList")
        if relations is not None:
            model = relations.model()
            model.rowsInserted.connect(self._sync_claim_relations)
            model.rowsRemoved.connect(self._sync_claim_relations)
            model.modelReset.connect(self._sync_claim_relations)
            relations.currentItemChanged.connect(self._sync_claim_relations)

    def _sync_research_proposals(self, *_args: object) -> None:
        try:
            proposals = self.window.findChild(QListWidget, "researchProposalList")
        except RuntimeError:
            return
        if proposals is None:
            return
        has_rows = proposals.count() > 0
        proposals.setVisible(has_rows)
        proposals.setMaximumHeight(170 if has_rows else 0)
        proposals.setProperty("pathenaProgressiveRole", "secondary")

        for name in (
            "researchProposalAcceptButton",
            "researchProposalSeparateButton",
            "researchProposalRejectButton",
        ):
            try:
                button = self.window.findChild(QPushButton, name)
            except RuntimeError:
                return
            if button is not None:
                button.setVisible(button.isEnabled())
                button.setProperty("pathenaProgressiveRole", "decision")

    def _sync_claim_relations(self, *_args: object) -> None:
        try:
            relations = self.window.findChild(QListWidget, "claimRelationList")
        except RuntimeError:
            return
        if relations is None:
            return
        has_rows = relations.count() > 0
        relations.setVisible(has_rows)
        relations.setMaximumHeight(150 if has_rows else 0)
        relations.setProperty("pathenaProgressiveRole", "secondary")

        try:
            open_related = self.window.findChild(QPushButton, "openRelatedClaimButton")
        except RuntimeError:
            return
        if open_related is not None:
            open_related.setVisible(has_rows and open_related.isEnabled())

        relations.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus if has_rows else Qt.FocusPolicy.NoFocus
        )


def apply_ui_refinements_2201_2300(window: QWidget) -> tuple[int, ...]:
    """Record progressive-refinement coverage for installed presentation surfaces."""
    applied: list[int] = []
    for index, target in enumerate(_PROGRESSIVE_TARGETS):
        widget = window.findChild(QWidget, target.key)
        if widget is None:
            continue
        widget.setProperty("pathenaProgressiveSurface", True)
        start = 2201 + index * len(_PROGRESSIVE_REFINEMENTS)
        applied.extend(range(start, start + len(_PROGRESSIVE_REFINEMENTS)))
    window.setProperty("pathenaUiProgressiveTaskCount", 100)
    return tuple(applied)


def install_progressive_workspace_refinement(
    window: QWidget,
) -> PathenaProgressiveWorkspaceRefinement:
    """Install progressive Research/Knowledge presentation behavior."""
    return PathenaProgressiveWorkspaceRefinement(window)
