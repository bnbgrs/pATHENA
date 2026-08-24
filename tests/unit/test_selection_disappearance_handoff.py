from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.pathena_selection_disappearance_handoff import (
    install_selection_disappearance_handoff,
)
from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_workspace import ResearchWorkspace
from athena.desktop.system_backup import BackupWorkspace


@pytest.fixture(scope="module")
def qt_app() -> Iterator[QApplication]:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        yield existing
        return
    app = QApplication([])
    yield app
    app.quit()


def _workspaces() -> tuple[
    FilesWorkspace,
    JobsWorkspace,
    ResearchWorkspace,
    BackupWorkspace,
    ResearchResultsExtension,
]:
    files = FilesWorkspace()
    files._refresh_timer.stop()
    jobs = JobsWorkspace()
    jobs._refresh_timer.stop()
    jobs._scheduler_status_timer.stop()
    research = ResearchWorkspace()
    backup = BackupWorkspace()
    results = ResearchResultsExtension(research)
    results.refresh_timer.stop()
    return files, jobs, research, backup, results


def test_disappeared_selection_explanation_reaches_list_accessibility(
    qt_app: QApplication,
) -> None:
    files, jobs, research, backup, results = _workspaces()
    handoff = install_selection_disappearance_handoff(
        files,
        jobs,
        research,
        backup,
        results,
    )
    message = (
        "SELECTION CHANGED · Source 11111111 is no longer listed after refresh. "
        "Select another Source to inspect its current state."
    )
    files.details.setPlainText(message)
    files.sources.setProperty(
        "pathenaSelectionDisappeared",
        "11111111-1111-1111-1111-111111111111",
    )
    qt_app.processEvents()

    assert files.sources.accessibleDescription() == message
    assert files.sources.property("pathenaSelectionHandoffAnnouncement") == message
    handoff.deleteLater()


def test_research_disappearance_clears_stale_proposals(qt_app: QApplication) -> None:
    files, jobs, research, backup, results = _workspaces()
    handoff = install_selection_disappearance_handoff(
        files,
        jobs,
        research,
        backup,
        results,
    )
    proposal = QListWidgetItem("stale proposal")
    results.proposal_list.addItem(proposal)
    results.proposal_list.setCurrentItem(proposal)
    results._selected_proposal_id = "proposal-1"
    research._selected_job_id = None
    research.jobs.setProperty(
        "pathenaSelectionDisappeared",
        "22222222-2222-2222-2222-222222222222",
    )

    handoff._sync_research_results()

    assert results.proposal_list.count() == 0
    assert results._selected_proposal_id is None
    assert "22222222" in results.proposal_status.text()
    assert "No ResearchResult proposal is selected" in results.proposal_status.text()
    handoff.deleteLater()
