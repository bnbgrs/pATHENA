"""V3 composition for durable Research."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSplitter, QVBoxLayout, QWidget
from shiboken6 import isValid

from athena.desktop.pathena_v3_components import V3EmptyState
from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_workspace import ResearchWorkspace


class PathenaV3ResearchController(QObject):
    """Compose Research as question -> run -> evidence/result."""

    def __init__(self, workspace: ResearchWorkspace, results: ResearchResultsExtension) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.results = results
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA V3 requires the real Research vertical layout.")

        splitter = workspace.jobs.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA V3 requires the real Research master/detail splitter.")

        while root.count():
            item = root.takeAt(0)
            if item is not None and item.layout() is not None:
                item.layout().setParent(None)
        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v3ResearchWorkspace")
        # V3 owns presentation at the application level. Drop presentation-only
        # local QSS installed by legacy experience controllers while preserving
        # their behavior, accessibility metadata, shortcuts and state wiring.
        workspace.setStyleSheet("")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        brief = QFrame()
        brief.setObjectName("v3ResearchBrief")
        brief_layout = QVBoxLayout(brief)
        brief_layout.setContentsMargins(16, 14, 16, 14)
        brief_layout.setSpacing(9)

        kicker = QLabel("RESEARCH BRIEF")
        kicker.setObjectName("v3Kicker")
        brief_layout.addWidget(kicker)

        query_row = QHBoxLayout()
        query_row.setContentsMargins(0, 0, 0, 0)
        query_row.setSpacing(8)
        workspace.query_input.setParent(brief)
        workspace.query_input.setPlaceholderText("What do you want to understand?")
        workspace.query_input.show()
        query_row.addWidget(workspace.query_input, 1)

        workspace.start_button.setParent(brief)
        workspace.start_button.setText("Research")
        workspace.start_button.show()
        query_row.addWidget(workspace.start_button)

        workspace.cancel_button.setParent(brief)
        workspace.cancel_button.setText("Cancel")
        workspace.cancel_button.show()
        query_row.addWidget(workspace.cancel_button)
        brief_layout.addLayout(query_row)

        state_row = QHBoxLayout()
        state_row.setContentsMargins(0, 0, 0, 0)
        state_row.setSpacing(10)
        workspace.status.setParent(brief)
        workspace.status.setObjectName("v3ResearchStatus")
        workspace.status.show()
        state_row.addWidget(workspace.status)
        state_row.addStretch(1)

        self.results.job_filter.setParent(brief)
        self.results.job_filter.setPlaceholderText("Filter runs")
        self.results.job_filter.setMaximumWidth(260)
        self.results.job_filter.show()
        state_row.addWidget(self.results.job_filter)

        workspace.refresh_button.setParent(brief)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        state_row.addWidget(workspace.refresh_button)
        brief_layout.addLayout(state_row)
        root.addWidget(brief)

        splitter.setParent(workspace)
        splitter.setObjectName("v3ResearchSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.jobs.setMinimumWidth(230)
        workspace.jobs.setMaximumWidth(390)
        workspace.jobs.show()
        splitter.show()
        root.addWidget(splitter, 1)

        self.empty_state = V3EmptyState(
            "Research",
            "Start with a question",
            "pATHENA keeps each research run, evidence trail and review decision together.",
        )
        self.empty_state.setAccessibleName("Research empty state")
        root.addWidget(self.empty_state, 1)
        model = workspace.jobs.model()
        model.rowsInserted.connect(self._sync_empty_state)
        model.rowsRemoved.connect(self._sync_empty_state)
        model.modelReset.connect(self._sync_empty_state)
        self._sync_empty_state()

        self.results.result_button.setText("Open result")
        self.results.propose_button.setText("Propose knowledge")
        self.results.refresh_proposals_button.setText("Review proposals")
        self.results.accept_button.setText("Accept")
        self.results.accept_separate_button.setText("Keep separate")
        self.results.reject_button.setText("Reject")
        workspace.setProperty("pathenaV3Composed", True)

    def _sync_empty_state(self, *_args: object) -> None:
        if not isValid(self.workspace) or not isValid(self.workspace.jobs):
            return
        is_empty = self.workspace.jobs.count() == 0
        self.empty_state.setVisible(is_empty)
        splitter = self.workspace.jobs.parentWidget()
        if isinstance(splitter, QSplitter):
            splitter.setVisible(not is_empty)


def install_v3_research_workspace(
    workspace: ResearchWorkspace,
    results: ResearchResultsExtension,
) -> PathenaV3ResearchController:
    existing = getattr(workspace, "_pathena_v3_controller", None)
    if isinstance(existing, PathenaV3ResearchController):
        return existing
    controller = PathenaV3ResearchController(workspace, results)
    workspace.__dict__["_pathena_v3_controller"] = controller
    return controller
