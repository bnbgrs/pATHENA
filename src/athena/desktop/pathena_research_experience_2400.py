"""Research experience refinements 2301-2400 for pATHENA.

This presentation controller follows the existing durable Research path from question
through job inspection, immutable result review and explicit proposal decisions. It
adds no new domain action: every shortcut and progressive control delegates to an
existing ResearchWorkspace or ResearchResultsExtension method/button.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QAbstractItemView, QPlainTextEdit, QSplitter, QWidget

if TYPE_CHECKING:
    from athena.desktop.research_results_extension import ResearchResultsExtension
    from athena.desktop.research_workspace import ResearchWorkspace


@dataclass(frozen=True)
class ResearchTarget:
    key: str
    label: str


_RESEARCH_TARGETS: tuple[ResearchTarget, ...] = (
    ResearchTarget("researchWorkspace", "Research workspace"),
    ResearchTarget("researchQuestionInput", "Research question"),
    ResearchTarget("researchStartButton", "Start research"),
    ResearchTarget("researchRefreshButton", "Refresh research runs"),
    ResearchTarget("researchCancelButton", "Cancel selected research"),
    ResearchTarget("researchStatus", "Research status"),
    ResearchTarget("researchJobFilter", "Research run filter"),
    ResearchTarget("researchJobList", "Research run browser"),
    ResearchTarget("researchPrimarySplitter", "Research browse/detail splitter"),
    ResearchTarget("researchDetails", "Research scope and result detail"),
    ResearchTarget("researchResultPanel", "Research result review"),
    ResearchTarget("researchResultButton", "View immutable result"),
    ResearchTarget("researchProposeButton", "Create knowledge proposals"),
    ResearchTarget("researchProposalRefreshButton", "Review knowledge proposals"),
    ResearchTarget("researchProposalStatus", "Proposal review status"),
    ResearchTarget("researchProposalList", "Proposal browser"),
    ResearchTarget("researchProposalRejectButton", "Reject proposal"),
    ResearchTarget("researchProposalSeparateButton", "Keep proposal separate"),
    ResearchTarget("researchProposalAcceptButton", "Accept proposal"),
    ResearchTarget("researchDecisionFlow", "Proposal decision flow"),
)

_RESEARCH_REFINEMENTS: tuple[str, ...] = (
    "give the existing control a stable accessible identity",
    "describe the real action or information in plain language",
    "make keyboard focus and traversal predictable",
    "reduce visual machinery while preserving state visibility",
    "surface the next valid action only when the backing state allows it",
)

UI_REFINEMENT_TASKS_2301_2400: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _RESEARCH_TARGETS
    for refinement in _RESEARCH_REFINEMENTS
)

_RESEARCH_STYLESHEET = r"""
QWidget[pathenaResearchRole="status"] {
    color: #969696;
    background: transparent;
}
QWidget[pathenaResearchRole="detail"] {
    background: #070707;
    border: none;
    color: #D8D8D8;
}
QWidget[pathenaResearchRole="browser"] {
    background: #090909;
    border: 1px solid #1E1E1E;
}
QWidget[pathenaResearchRole="action"] {
    background: transparent;
}
QWidget[pathenaResearchRole="decision"]:focus,
QWidget[pathenaResearchRole="action"]:focus {
    border: 1px solid #F26A21;
}
"""


def _set_identity(
    widget: QWidget,
    *,
    object_name: str,
    accessible_name: str,
    description: str,
    role: str,
) -> None:
    widget.setObjectName(object_name)
    widget.setAccessibleName(accessible_name)
    widget.setAccessibleDescription(description)
    widget.setProperty("pathenaResearchRole", role)


class PathenaResearchExperience(QObject):
    """Polish the existing Research interaction path without changing its semantics."""

    def __init__(
        self,
        workspace: ResearchWorkspace,
        extension: ResearchResultsExtension,
    ) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.extension = extension
        self._shortcuts: list[QShortcut] = []
        self._identify_existing_surfaces()
        self._configure_readability()
        self._configure_keyboard_flow()
        self._configure_progressive_actions()
        self._connect_state_sync()
        self.sync()

    def _identify_existing_surfaces(self) -> None:
        _set_identity(
            self.workspace,
            object_name="researchWorkspace",
            accessible_name="Research workspace",
            description="Create and inspect durable local research runs.",
            role="surface",
        )
        _set_identity(
            self.workspace.query_input,
            object_name="researchQuestionInput",
            accessible_name="Research question",
            description="Question to research across the current local Source snapshot.",
            role="action",
        )
        _set_identity(
            self.workspace.start_button,
            object_name="researchStartButton",
            accessible_name="Start research",
            description="Queue the entered question as a durable research job.",
            role="action",
        )
        _set_identity(
            self.workspace.refresh_button,
            object_name="researchRefreshButton",
            accessible_name="Refresh research runs",
            description="Reload durable research jobs from the canonical job store.",
            role="action",
        )
        _set_identity(
            self.workspace.cancel_button,
            object_name="researchCancelButton",
            accessible_name="Cancel selected research run",
            description="Persist a cancellation request for the selected non-terminal run.",
            role="decision",
        )
        _set_identity(
            self.workspace.status,
            object_name="researchStatus",
            accessible_name="Research status",
            description="Current state of the local Research command.",
            role="status",
        )
        _set_identity(
            self.extension.job_filter,
            object_name="researchJobFilter",
            accessible_name="Filter research runs",
            description="Filter the visible durable research run list.",
            role="action",
        )
        _set_identity(
            self.workspace.jobs,
            object_name="researchJobList",
            accessible_name="Research runs",
            description="Durable research runs with state, coverage and query.",
            role="browser",
        )
        _set_identity(
            self.workspace.details,
            object_name="researchDetails",
            accessible_name="Research details and result",
            description=(
                "Scope, coverage, work items, immutable result and evidence for the "
                "selected run."
            ),
            role="detail",
        )

        result_panel = self.workspace.findChild(QWidget, "researchResultPanel")
        if result_panel is not None:
            _set_identity(
                result_panel,
                object_name="researchResultPanel",
                accessible_name="Research result review",
                description=(
                    "Inspect an immutable result and review evidence-backed knowledge "
                    "proposals."
                ),
                role="surface",
            )
            splitter = result_panel.parentWidget()
            if isinstance(splitter, QSplitter):
                splitter.setObjectName("researchPrimarySplitter")
                splitter.setAccessibleName("Research run and result splitter")
                splitter.setAccessibleDescription(
                    "Resize the research run browser and result detail areas."
                )
                splitter.setProperty("pathenaResearchRole", "surface")

        control_specs = (
            (
                self.extension.result_button,
                "researchResultButton",
                "View result",
                "Load the immutable result and evidence for the selected completed run.",
                "action",
            ),
            (
                self.extension.propose_button,
                "researchProposeButton",
                "Create proposals",
                "Create deterministic knowledge proposals from the selected completed result.",
                "action",
            ),
            (
                self.extension.refresh_proposals_button,
                "researchProposalRefreshButton",
                "Review proposals",
                "Load frozen proposals for the selected completed research run.",
                "action",
            ),
            (
                self.extension.accept_button,
                "researchProposalAcceptButton",
                "Accept proposal",
                "Accept the selected evidence-backed proposal into canonical memory.",
                "decision",
            ),
            (
                self.extension.accept_separate_button,
                "researchProposalSeparateButton",
                "Keep proposal separate",
                "Accept the proposal while keeping a surfaced near-duplicate separate.",
                "decision",
            ),
            (
                self.extension.reject_button,
                "researchProposalRejectButton",
                "Reject proposal",
                "Reject the selected proposal without adding it to canonical memory.",
                "decision",
            ),
        )
        for button, name, accessible, description, role in control_specs:
            _set_identity(
                button,
                object_name=name,
                accessible_name=accessible,
                description=description,
                role=role,
            )

        _set_identity(
            self.extension.proposal_status,
            object_name="researchProposalStatus",
            accessible_name="Proposal review status",
            description="Explains the current immutable result and proposal-review state.",
            role="status",
        )
        _set_identity(
            self.extension.proposal_list,
            object_name="researchProposalList",
            accessible_name="Research knowledge proposals",
            description=(
                "Evidence-backed proposals generated from the selected immutable "
                "research result."
            ),
            role="browser",
        )
        self.workspace.setProperty("pathenaResearchDecisionFlow", True)

    def _configure_readability(self) -> None:
        self.workspace.status.setWordWrap(True)
        self.extension.proposal_status.setWordWrap(True)
        self.workspace.details.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.workspace.details.document().setDocumentMargin(14.0)
        self.workspace.jobs.setAlternatingRowColors(False)
        self.workspace.jobs.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.extension.proposal_list.setAlternatingRowColors(False)
        self.extension.proposal_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.extension.proposal_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.extension.proposal_list.setMinimumHeight(96)
        self.extension.proposal_list.setMaximumHeight(168)
        self.workspace.query_input.setClearButtonEnabled(True)
        self.workspace.query_input.setToolTip(
            "Enter a question · Enter or Ctrl+Enter to queue"
        )
        self.extension.job_filter.setToolTip("Filter runs · Ctrl+F")

        if _RESEARCH_STYLESHEET not in self.workspace.styleSheet():
            self.workspace.setStyleSheet(
                f"{self.workspace.styleSheet()}\n{_RESEARCH_STYLESHEET}"
            )

    def _configure_keyboard_flow(self) -> None:
        for widget in (
            self.workspace.query_input,
            self.workspace.start_button,
            self.workspace.refresh_button,
            self.workspace.cancel_button,
            self.extension.job_filter,
            self.workspace.jobs,
            self.extension.result_button,
            self.extension.propose_button,
            self.extension.refresh_proposals_button,
            self.extension.proposal_list,
            self.extension.reject_button,
            self.extension.accept_separate_button,
            self.extension.accept_button,
        ):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        focus_order: tuple[QWidget, ...] = (
            self.workspace.query_input,
            self.workspace.start_button,
            self.extension.job_filter,
            self.workspace.jobs,
            self.extension.result_button,
            self.extension.propose_button,
            self.extension.refresh_proposals_button,
            self.extension.proposal_list,
            self.extension.reject_button,
            self.extension.accept_separate_button,
            self.extension.accept_button,
            self.workspace.refresh_button,
            self.workspace.cancel_button,
        )
        for first, second in zip(focus_order, focus_order[1:], strict=True):
            QWidget.setTabOrder(first, second)

        self._add_shortcut("Ctrl+Enter", self._start_if_available)
        self._add_shortcut("Ctrl+F", self.extension.job_filter.setFocus)
        self._add_shortcut("F5", self._refresh_if_available)

    def _add_shortcut(self, keys: str, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(QKeySequence(keys), self.workspace)
        shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        shortcut.activated.connect(callback)
        self._shortcuts.append(shortcut)

    def _start_if_available(self) -> None:
        if (
            self.workspace.start_button.isEnabled()
            and self.workspace.query_input.text().strip()
        ):
            self.workspace.start_button.click()

    def _refresh_if_available(self) -> None:
        if self.workspace.refresh_button.isEnabled():
            self.workspace.refresh_button.click()

    def _configure_progressive_actions(self) -> None:
        self.workspace.cancel_button.setVisible(self.workspace.cancel_button.isEnabled())
        for button in (
            self.extension.result_button,
            self.extension.propose_button,
            self.extension.refresh_proposals_button,
            self.extension.reject_button,
            self.extension.accept_separate_button,
            self.extension.accept_button,
        ):
            button.setVisible(button.isEnabled())

    def _connect_state_sync(self) -> None:
        self.workspace.jobs.currentItemChanged.connect(self.sync)
        self.extension.proposal_list.currentItemChanged.connect(self.sync)
        self.workspace._process.finished.connect(self.sync)
        self.extension.process.finished.connect(self.sync)
        self.workspace.query_input.textChanged.connect(self.sync)

    def sync(self, *_args: object) -> None:
        has_job = self.workspace.jobs.currentItem() is not None
        has_proposals = self.extension.proposal_list.count() > 0
        has_selected_proposal = self.extension.proposal_list.currentItem() is not None

        self.workspace.cancel_button.setVisible(self.workspace.cancel_button.isEnabled())
        self.extension.proposal_list.setVisible(has_proposals)
        self.extension.proposal_status.setVisible(has_job)

        for button in (
            self.extension.result_button,
            self.extension.propose_button,
            self.extension.refresh_proposals_button,
        ):
            button.setVisible(button.isEnabled())

        for button in (
            self.extension.reject_button,
            self.extension.accept_separate_button,
            self.extension.accept_button,
        ):
            button.setVisible(has_selected_proposal and button.isEnabled())

        if not has_job:
            self.workspace.details.setPlaceholderText(
                "Select a research run to inspect scope, coverage, evidence and result."
            )
        self.extension.proposal_list.setMaximumHeight(168 if has_proposals else 0)


def apply_ui_refinements_2301_2400(window: QWidget) -> tuple[int, ...]:
    """Register the 100 Research experience refinements on installed real surfaces."""
    applied: list[int] = []
    for index, target in enumerate(_RESEARCH_TARGETS):
        if target.key == "researchDecisionFlow":
            found = window.findChild(QWidget, "researchWorkspace")
        else:
            found = window.findChild(QWidget, target.key)
        if found is None:
            continue
        found.setProperty("pathenaResearch2400", True)
        start = 2301 + index * len(_RESEARCH_REFINEMENTS)
        applied.extend(range(start, start + len(_RESEARCH_REFINEMENTS)))
    return tuple(applied)


def install_research_experience(
    workspace: ResearchWorkspace,
    extension: ResearchResultsExtension,
) -> PathenaResearchExperience:
    """Install accessible, progressive presentation for the existing Research flow."""
    return PathenaResearchExperience(workspace, extension)
