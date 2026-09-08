from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.app import create_application
from athena.desktop.jobs_workspace import JobsWorkspace


def _app() -> QApplication:
    return create_application(["pathena-jobs-status-copy-test"])


def _workspace(monkeypatch: pytest.MonkeyPatch) -> tuple[QApplication, JobsWorkspace]:
    original_refresh = JobsWorkspace.refresh
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    monkeypatch.setattr(JobsWorkspace, "refresh", original_refresh)
    app.processEvents()
    return app, workspace


def test_jobs_progress_copy_uses_product_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, workspace = _workspace(monkeypatch)
    starts: list[tuple[str, list[str], str, str | None]] = []

    def record_start(
        operation: str,
        arguments: list[str],
        label: str,
        *,
        job_id: str | None = None,
    ) -> None:
        starts.append((operation, arguments, label, job_id))

    monkeypatch.setattr(workspace, "_start", record_start)
    monkeypatch.setattr(workspace, "_busy", lambda: False)
    try:
        JobsWorkspace.refresh(workspace)
        assert starts[-1][2] == "Refreshing jobs"

        workspace._selected_job_id = "12345678-job"
        workspace.cancel_selected()
        assert starts[-1][2] == "Requesting cancellation"

        item = QListWidgetItem("WAITING")
        item.setData(Qt.ItemDataRole.UserRole, "12345678-job")
        item.setData(Qt.ItemDataRole.UserRole + 1, "waiting")
        workspace._selection_changed(item, None)
        assert starts[-1][2] == "Loading job details"

        visible_copy = " ".join(entry[2] for entry in starts).casefold()
        assert "durable" not in visible_copy
        assert "persisting" not in visible_copy
    finally:
        workspace.close()
        app.processEvents()


def test_jobs_refresh_and_show_success_copy_is_human_facing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, workspace = _workspace(monkeypatch)
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    try:
        workspace._operation = "list"
        workspace._operation_job_id = None
        workspace._buffer = ""
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == "Jobs refreshed: 0 shown."

        workspace._operation = "show"
        workspace._operation_job_id = "12345678-job"
        workspace._selected_job_id = "12345678-job"
        workspace._buffer = ""
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == "Job 12345678 details loaded."

        lowered = workspace.status.text().casefold()
        assert "durable" not in lowered
        assert "persist" not in lowered
    finally:
        workspace.close()
        app.processEvents()


def test_jobs_nonzero_exit_status_uses_product_language(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, workspace = _workspace(monkeypatch)
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    try:
        workspace._operation = "list"
        workspace._operation_job_id = None
        workspace._selected_job_id = None
        workspace._buffer = "list failed"
        workspace._process_finished(17, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == "Jobs could not be refreshed (exit 17)."

        workspace._operation = "show"
        workspace._operation_job_id = "12345678-job"
        workspace._selected_job_id = "12345678-job"
        workspace._buffer = "show failed"
        workspace._process_finished(18, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == (
            "Job 12345678 details could not be loaded (exit 18)."
        )

        workspace._operation = "cancel"
        workspace._operation_job_id = "12345678-job"
        workspace._selected_job_id = "12345678-job"
        workspace._buffer = "cancel failed"
        workspace._process_finished(19, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == "CANCEL failed for job 12345678 (exit 19)."

        workspace._operation = "pause"
        workspace._operation_job_id = "12345678-job"
        workspace._selected_job_id = "87654321-job"
        workspace._buffer = "pause failed"
        workspace._process_finished(20, QProcess.ExitStatus.NormalExit)
        assert workspace.status.text() == (
            "PAUSE failed for job 12345678 in the background (exit 20)."
        )

        assert "command" not in workspace.status.text().casefold()
    finally:
        workspace.close()
        app.processEvents()
