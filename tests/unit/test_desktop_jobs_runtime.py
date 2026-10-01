from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from athena.desktop import jobs_cli
from athena.desktop.app import create_application
from athena.desktop.jobs_lifecycle import parse_current_progress
from athena.desktop.jobs_workspace import JobsWorkspace


@dataclass
class _StorageLifecycle:
    started: int = 0
    stopped: int = 0

    def start(self) -> None:
        self.started += 1

    def stop(self) -> None:
        self.stopped += 1


class _Jobs:
    def __init__(self, *, fail_list: bool = False) -> None:
        self.fail_list = fail_list

    def list(self, *, limit: int) -> tuple[()]:
        assert limit == 150
        if self.fail_list:
            raise RuntimeError("jobs list failed")
        return ()


class _HelperApp:
    def __init__(self, *, fail_list: bool = False) -> None:
        self.storage_bootstrap = _StorageLifecycle()
        self.jobs = _Jobs(fail_list=fail_list)

    def start(self, **_kwargs: object) -> None:
        raise AssertionError("desktop Jobs helper must not start the full Core lifecycle")

    def stop(self) -> None:
        raise AssertionError("desktop Jobs helper must not stop the full Core lifecycle")


def _qt_app() -> QApplication:
    return create_application(["pathena-jobs-runtime-test"])


def _workspace() -> JobsWorkspace:
    _qt_app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    return workspace


def test_jobs_cli_uses_storage_only_lifecycle(monkeypatch) -> None:
    app = _HelperApp()
    monkeypatch.setattr(jobs_cli, "AthenaApplication", lambda: app)

    result = jobs_cli.main(["list"])

    assert result == 0
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1


def test_jobs_cli_stops_storage_after_command_failure(monkeypatch, capsys) -> None:
    app = _HelperApp(fail_list=True)
    monkeypatch.setattr(jobs_cli, "AthenaApplication", lambda: app)

    result = jobs_cli.main(["list"])

    assert result == 2
    assert app.storage_bootstrap.started == 1
    assert app.storage_bootstrap.stopped == 1
    assert "JOBS_ERROR RuntimeError: jobs list failed" in capsys.readouterr().err


def test_compact_progress_summary_uses_persisted_values_without_fake_percentage() -> None:
    summary = jobs_cli._compact_progress_summary(
        '{"processed":347,"phase":"indexing","total":null}'
    )

    assert summary == '{"phase":"indexing","processed":347,"total":null}'
    assert "%" not in summary


def test_parse_current_progress_is_fail_closed_for_missing_checkpoint_progress() -> None:
    assert parse_current_progress("JOB abc\nCURRENT_PROGRESS -\nCHECKPOINTS 0\n") is None
    assert parse_current_progress("JOB abc\nCHECKPOINTS 0\n") is None


def test_parse_current_progress_reads_exact_cli_projection() -> None:
    assert (
        parse_current_progress(
            'JOB abc\nCURRENT_PROGRESS {"phase":"indexing","processed":347}\n'
        )
        == '{"phase":"indexing","processed":347}'
    )


def test_jobs_workspace_surfaces_durable_checkpoint_progress() -> None:
    workspace = _workspace()
    try:
        job_id = "11111111-1111-1111-1111-111111111111"
        workspace._selected_job_id = job_id
        workspace._selected_state = "running"
        workspace._operation = "show"
        workspace._operation_job_id = job_id
        workspace._buffer = (
            f"JOB {job_id}\n"
            "STATE running\n"
            'CURRENT_PROGRESS {"phase":"indexing","processed":347}\n'
        )

        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.progress.text() == (
            'PROGRESS · {"phase":"indexing","processed":347}'
        )
        assert workspace.progress.property("pathenaUiState") == "success"
    finally:
        workspace.close()


def test_jobs_workspace_preserves_operation_identity_until_crash_exit() -> None:
    workspace = _workspace()
    try:
        job_id = "22222222-2222-2222-2222-222222222222"
        workspace._selected_job_id = job_id
        workspace._selected_state = "running"
        workspace._operation = "cancel"
        workspace._operation_job_id = job_id

        workspace._process_error(QProcess.ProcessError.Crashed)

        assert workspace._operation == "cancel"
        assert workspace._operation_job_id == job_id
        assert "CANCEL for job 22222222 encountered Crashed" in workspace.status.text()

        workspace._process_finished(1, QProcess.ExitStatus.CrashExit)

        assert workspace._operation == ""
        assert workspace._operation_job_id is None
        assert workspace.status.text() == "CANCEL failed for job 22222222 (exit 1)."
    finally:
        workspace.close()


def test_jobs_workspace_failed_start_is_terminal_and_not_overwritten() -> None:
    workspace = _workspace()
    try:
        job_id = "33333333-3333-3333-3333-333333333333"
        workspace._selected_job_id = job_id
        workspace._selected_state = "running"
        workspace._operation = "show"
        workspace._operation_job_id = job_id

        workspace._process_error(QProcess.ProcessError.FailedToStart)
        reported = workspace.status.text()

        assert reported == "Job details for job 33333333 could not be started."
        assert workspace._operation == ""
        assert workspace._operation_job_id is None
        assert workspace.progress.text() == "PROGRESS · Unavailable."

        workspace._process_finished(1, QProcess.ExitStatus.CrashExit)

        assert workspace.status.text() == reported
    finally:
        workspace.close()
