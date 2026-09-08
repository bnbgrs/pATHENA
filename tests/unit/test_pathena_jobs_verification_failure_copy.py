from __future__ import annotations

import pytest
from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.jobs_workspace import JobsWorkspace


def _app() -> QApplication:
    return create_application(["pathena-jobs-verification-failure-copy-test"])


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


def test_jobs_verification_failure_keeps_diagnostic_payload_but_hides_command_jargon(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, workspace = _workspace(monkeypatch)
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    diagnostic_payload = "UNEXPECTED RECEIPT PAYLOAD --debug-token=alpha"
    try:
        workspace._operation = "pause"
        workspace._operation_job_id = "12345678-job"
        workspace._selected_job_id = "12345678-job"
        workspace._buffer = diagnostic_payload

        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        details = workspace.details.toPlainText()
        assert details.startswith("JOB ACTION COULD NOT BE VERIFIED\n")
        assert "Diagnostic details:\n" in details
        assert diagnostic_payload in details
        lowered = details.casefold()
        assert "job action response unavailable" not in lowered
        assert "raw command output" not in lowered
    finally:
        workspace.close()
        app.processEvents()
