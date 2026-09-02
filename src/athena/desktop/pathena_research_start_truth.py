"""Truthful START RESEARCH availability for the native Research workspace."""

from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from athena.desktop.research_workspace import ResearchWorkspace


class ResearchStartTruth(QObject):
    """Keep START RESEARCH aligned with the existing non-empty query contract."""

    def __init__(self, workspace: ResearchWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        workspace.query_input.textChanged.connect(self.sync)
        workspace._process.finished.connect(self._schedule_sync)
        workspace._process.errorOccurred.connect(self._schedule_sync)
        self.sync()

    def _schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self, *_args: object) -> None:
        workspace = self.workspace
        query = workspace.query_input.text().strip()
        available = bool(query) and not workspace._busy()
        workspace.start_button.setEnabled(available)
        workspace.start_button.setProperty("pathenaResearchStartAvailable", available)
        workspace.start_button.setProperty("pathenaResearchQueryPresent", bool(query))

        if workspace._busy():
            reason = "Research command is already running; wait for it to finish."
        elif not query:
            reason = "Enter a research question before starting exhaustive local research."
        else:
            reason = "Queue exhaustive local research for the current question."
        workspace.start_button.setToolTip(reason)
        workspace.start_button.setAccessibleDescription(reason)
        workspace.query_input.setProperty("pathenaResearchStartReason", reason)


def install_research_start_truth(workspace: ResearchWorkspace) -> ResearchStartTruth:
    """Install non-empty-query availability for the existing Research start action."""
    return ResearchStartTruth(workspace)
