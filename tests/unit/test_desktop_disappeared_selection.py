from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
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


def test_source_refresh_does_not_replace_disappeared_selection(qt_app: QApplication) -> None:
    workspace = FilesWorkspace()
    workspace._refresh_timer.stop()
    missing = "11111111-1111-1111-1111-111111111111"
    replacement = "22222222-2222-2222-2222-222222222222"
    workspace._selected_source_id = missing
    workspace._selected_readiness = "ready"
    workspace._selected_processable = True

    workspace._render_source_list(
        f"{replacement}\tready\tcompleted\tcaptured\tnew.txt\ttext/plain\t12\tyes\t1\t1"
    )

    assert workspace.sources.currentRow() == -1
    assert workspace._selected_source_id is None
    assert workspace.sources.property("pathenaSelectionDisappeared") == missing
    assert "11111111" in workspace.details.toPlainText()


def test_job_refresh_does_not_replace_disappeared_selection(qt_app: QApplication) -> None:
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    missing = "33333333-3333-3333-3333-333333333333"
    replacement = "44444444-4444-4444-4444-444444444444"
    workspace._selected_job_id = missing
    workspace._selected_state = "waiting"

    workspace._render_job_list(
        f"{replacement}\twaiting\t1\tresearch\tqueued\t0\t123\tReplacement job"
    )

    assert workspace.jobs.currentRow() == -1
    assert workspace._selected_job_id is None
    assert workspace.jobs.property("pathenaSelectionDisappeared") == missing
    assert "33333333" in workspace.details.toPlainText()


def test_research_refresh_does_not_replace_disappeared_selection(qt_app: QApplication) -> None:
    workspace = ResearchWorkspace()
    missing = "55555555-5555-5555-5555-555555555555"
    replacement = "66666666-6666-6666-6666-666666666666"
    workspace._selected_job_id = missing

    workspace._render_job_list(
        f"{replacement}\twaiting\tqueued\t0.25\tReplacement research run"
    )

    assert workspace.jobs.currentRow() == -1
    assert workspace._selected_job_id is None
    assert workspace.jobs.property("pathenaSelectionDisappeared") == missing
    assert "55555555" in workspace.details.toPlainText()


def test_backup_refresh_does_not_replace_disappeared_selection(qt_app: QApplication) -> None:
    workspace = BackupWorkspace()
    missing = "77777777-7777-7777-7777-777777777777"
    replacement = "88888888-8888-8888-8888-888888888888"
    workspace._selected_snapshot_id = missing

    workspace._render_snapshots(
        f"{replacement} state=complete verify=verified commit=abc123 objects=4 path=/tmp/backup"
    )

    assert workspace.snapshots.currentRow() == -1
    assert workspace._selected_snapshot_id is None
    assert workspace.snapshots.property("pathenaSelectionDisappeared") == missing
    assert "77777777" in workspace.details.toPlainText()


def test_initial_refresh_still_selects_first_available_rows(qt_app: QApplication) -> None:
    sources = FilesWorkspace()
    sources._refresh_timer.stop()
    sources._render_source_list(
        "99999999-9999-9999-9999-999999999999\tready\tcompleted\tcaptured\tfirst.txt\t"
        "text/plain\t12\tyes\t1\t1"
    )
    assert sources.sources.currentRow() == 0

    backups = BackupWorkspace()
    backups._render_snapshots(
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa state=complete verify=verified "
        "commit=abc123 objects=1 path=/tmp/backup"
    )
    assert backups.snapshots.currentRow() == 0
