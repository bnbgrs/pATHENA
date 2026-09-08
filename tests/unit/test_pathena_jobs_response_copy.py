from __future__ import annotations

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.jobs_workspace import JobsWorkspace

JOB_ID = "11111111-1111-1111-1111-111111111111"


def _app() -> QApplication:
    return create_application(["pathena-jobs-response-copy-test"])


def test_unverified_job_action_uses_product_response_copy(monkeypatch) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    workspace._selected_job_id = JOB_ID
    workspace._selected_state = "queued"
    workspace._operation = "cancel"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = "not-a-response"
    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.status.property("pathenaUiState") == "error"
        assert workspace.status.text() == (
            "CANCEL response for job 11111111 could not be verified."
        )
        details = workspace.details.toPlainText()
        assert details.startswith("JOB ACTION COULD NOT BE VERIFIED\n")
        assert "Diagnostic details:\nnot-a-response" in details
        assert "Raw command output" not in details
        assert "receipt" not in workspace.status.text().casefold()
        assert "receipt" not in details.casefold()
        assert workspace._selected_state == "queued"
    finally:
        workspace.close()
        app.processEvents()
