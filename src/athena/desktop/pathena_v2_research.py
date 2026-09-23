"""pATHENA v2 composition adapter for durable Research."""

from __future__ import annotations

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSplitter, QVBoxLayout, QWidget

from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_workspace import ResearchWorkspace


class PathenaV2ResearchController(QObject):
    """Recompose durable Research while preserving its real process and result contracts."""

    def __init__(
        self,
        workspace: ResearchWorkspace,
        results: ResearchResultsExtension,
    ) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.results = results
        self._recompose()

    def _recompose(self) -> None:
        workspace = self.workspace
        root = workspace.layout()
        if not isinstance(root, QVBoxLayout):
            raise RuntimeError("pATHENA v2 requires the real Research vertical layout.")

        splitter = workspace.jobs.parentWidget()
        if not isinstance(splitter, QSplitter):
            raise RuntimeError("pATHENA v2 requires the real Research master/detail splitter.")

        while root.count():
            item = root.takeAt(0)
            if item is None:
                continue
            nested = item.layout()
            if nested is not None:
                nested.setParent(None)

        for child in workspace.children():
            if isinstance(child, QWidget):
                child.hide()

        workspace.setObjectName("v2ResearchWorkspace")
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        query_bar = QFrame()
        query_bar.setObjectName("v2ResearchQueryBar")
        query_layout = QHBoxLayout(query_bar)
        query_layout.setContentsMargins(0, 0, 0, 0)
        query_layout.setSpacing(8)

        workspace.query_input.setParent(query_bar)
        workspace.query_input.setPlaceholderText("Research a question across local sources")
        workspace.query_input.show()
        query_layout.addWidget(workspace.query_input, 1)

        workspace.start_button.setParent(query_bar)
        workspace.start_button.setText("Start research")
        workspace.start_button.show()
        query_layout.addWidget(workspace.start_button)

        workspace.refresh_button.setParent(query_bar)
        workspace.refresh_button.setText("Refresh")
        workspace.refresh_button.show()
        query_layout.addWidget(workspace.refresh_button)

        workspace.cancel_button.setParent(query_bar)
        workspace.cancel_button.setText("Cancel")
        workspace.cancel_button.show()
        query_layout.addWidget(workspace.cancel_button)
        root.addWidget(query_bar)

        meta = QFrame()
        meta.setObjectName("v2ResearchMeta")
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(12, 8, 12, 8)
        meta_layout.setSpacing(12)

        workspace.status.setParent(meta)
        workspace.status.setObjectName("v2ResearchStatus")
        workspace.status.show()
        meta_layout.addWidget(workspace.status)

        self.results.job_filter.setParent(meta)
        self.results.job_filter.setPlaceholderText("Filter research runs")
        self.results.job_filter.show()
        meta_layout.addStretch(1)
        meta_layout.addWidget(self.results.job_filter)
        root.addWidget(meta)

        splitter.setParent(workspace)
        splitter.setObjectName("v2ResearchSplit")
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        workspace.jobs.setMinimumWidth(240)
        workspace.jobs.setMaximumWidth(430)
        workspace.jobs.show()
        splitter.show()
        root.addWidget(splitter, 1)

        # The result extension remains the source of truth for completed-result,
        # proposal and promotion controls; v2 only updates their human-facing copy.
        self.results.result_button.setText("Load result")
        self.results.propose_button.setText("Create proposals")
        self.results.refresh_proposals_button.setText("Proposals")
        self.results.accept_button.setText("Accept")
        self.results.accept_separate_button.setText("Keep separate")
        self.results.reject_button.setText("Reject")

        workspace.setProperty("pathenaV2Composed", True)


def install_v2_research_workspace(
    workspace: ResearchWorkspace,
    results: ResearchResultsExtension,
) -> PathenaV2ResearchController:
    """Install the v2 Research composition once."""
    existing = getattr(workspace, "_pathena_v2_controller", None)
    if isinstance(existing, PathenaV2ResearchController):
        return existing
    controller = PathenaV2ResearchController(workspace, results)
    workspace.__dict__["_pathena_v2_controller"] = controller
    return controller
