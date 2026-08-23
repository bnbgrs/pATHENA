from __future__ import annotations

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QListWidgetItem, QPlainTextEdit, QWidget

from athena.desktop.app import create_application
from athena.desktop.pathena_selection_disappearance_handoff import (
    SelectionDisappearanceHandoff,
    _SelectionTarget,
)


def _app() -> QApplication:
    return create_application(["pathena-selection-reselection-test"])


class _ResearchWorkspaceStub(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.jobs = QListWidget(self)
        self._selected_job_id: str | None = None
        self._process = QProcess(self)


class _ResearchResultsStub:
    def __init__(self) -> None:
        self.workspace = _ResearchWorkspaceStub()
        self.proposal_status = QLabel(self.workspace)
        self.proposal_list = QListWidget(self.workspace)
        self._selected_proposal_id: str | None = None

    def _sync_proposal_actions(self) -> None:
        return


def test_direct_reselection_clears_vanished_selection_announcement() -> None:
    app = _app()
    results = _ResearchResultsStub()
    details = QPlainTextEdit(results.workspace)
    target = _SelectionTarget(results.workspace.jobs, details)
    controller = SelectionDisappearanceHandoff((target,), results)  # type: ignore[arg-type]
    try:
        results.workspace.jobs.setProperty("pathenaSelectionDisappeared", "old-job-id")
        details.setProperty("pathenaSelectionDisappeared", "old-job-id")
        details.setPlainText("The previously selected research run disappeared.")
        controller._sync_target(target)
        assert results.workspace.jobs.property("pathenaSelectionHandoffAnnouncement")

        item = QListWidgetItem("CURRENT RUN")
        item.setData(Qt.ItemDataRole.UserRole, "new-job-id")
        results.workspace.jobs.addItem(item)
        results.workspace.jobs.setCurrentItem(item)
        app.processEvents()

        assert results.workspace.jobs.property("pathenaSelectionDisappeared") == ""
        assert details.property("pathenaSelectionDisappeared") == ""
        assert results.workspace.jobs.property("pathenaSelectionHandoffAnnouncement") == ""
    finally:
        controller.deleteLater()
        results.workspace.deleteLater()
        app.processEvents()


def test_research_reselection_clears_dependent_proposal_handoff_marker() -> None:
    app = _app()
    results = _ResearchResultsStub()
    details = QPlainTextEdit(results.workspace)
    target = _SelectionTarget(results.workspace.jobs, details)
    controller = SelectionDisappearanceHandoff((target,), results)  # type: ignore[arg-type]
    try:
        results.workspace.jobs.setProperty("pathenaSelectionDisappeared", "old-job-id")
        details.setProperty("pathenaSelectionDisappeared", "old-job-id")
        results.proposal_status.setProperty("pathenaSelectionDisappeared", "old-job-id")

        item = QListWidgetItem("NEW RUN")
        item.setData(Qt.ItemDataRole.UserRole, "new-job-id")
        results.workspace.jobs.addItem(item)
        results.workspace.jobs.setCurrentItem(item)
        app.processEvents()

        assert results.proposal_status.property("pathenaSelectionDisappeared") == ""
    finally:
        controller.deleteLater()
        results.workspace.deleteLater()
        app.processEvents()
