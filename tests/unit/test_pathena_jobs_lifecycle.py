from __future__ import annotations

import pytest
from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.app import create_application
from athena.desktop.jobs_lifecycle import (
    JobLifecycleError,
    action_availability,
    parse_job_list,
    parse_transition_receipt,
)
from athena.desktop.jobs_workspace import JobsWorkspace

JOB_ID = "11111111-1111-1111-1111-111111111111"


def _app() -> QApplication:
    return create_application(["pathena-jobs-lifecycle-test"])


@pytest.mark.parametrize(
    ("state", "enabled"),
    (
        ("queued", {"pause", "cancel"}),
        ("waiting", {"pause", "wake", "cancel"}),
        ("paused", {"resume", "cancel"}),
        ("running", {"cancel"}),
        ("cancel_requested", set()),
        ("completed", set()),
    ),
)
def test_action_availability_matches_durable_service_states(
    state: str,
    enabled: set[str],
) -> None:
    availability = action_availability(state)

    assert {
        action
        for action in ("pause", "resume", "wake", "cancel")
        if getattr(availability, action)
    } == enabled
    for action in ("pause", "resume", "wake", "cancel"):
        reason = availability.reason(action)
        assert "persisted state" not in reason
        assert "lifecycle mutation" not in reason
        assert "lifecycle action" not in reason
        if state == "cancel_requested":
            assert "Cancellation has already been requested" in reason
            assert "cancel_requested" not in reason
        else:
            assert state in reason


def test_action_availability_empty_selection_uses_product_language() -> None:
    availability = action_availability(None)

    for action in ("pause", "resume", "wake", "cancel"):
        reason = availability.reason(action)
        assert reason == "Select a job first."
        assert "durable" not in reason.casefold()


def test_unknown_job_state_fails_closed_for_every_visible_action() -> None:
    availability = action_availability("future_state")

    assert not availability.pause
    assert not availability.resume
    assert not availability.wake
    assert not availability.cancel
    for action in ("pause", "resume", "wake", "cancel"):
        reason = availability.reason(action)
        assert reason == "This job has an unrecognized state; actions are unavailable."
        assert "future_state" not in reason


def test_action_button_help_is_exposed_to_accessibility(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    try:
        workspace._selected_state = "waiting"
        workspace._sync_action_buttons()

        for button in (
            workspace.pause_button,
            workspace.resume_button,
            workspace.wake_button,
            workspace.cancel_button,
        ):
            assert button.toolTip()
            assert button.accessibleDescription() == button.toolTip()
    finally:
        workspace.close()
        app.processEvents()


def test_transition_receipt_is_bound_to_exact_job_and_operation() -> None:
    receipt = parse_transition_receipt(
        f"JOB_PAUSE {JOB_ID} paused\n",
        expected_operation="pause",
        expected_job_id=JOB_ID,
    )
    assert receipt.state == "paused"

    with pytest.raises(JobLifecycleError, match="another job"):
        parse_transition_receipt(
            "JOB_PAUSE 22222222-2222-2222-2222-222222222222 paused",
            expected_operation="pause",
            expected_job_id=JOB_ID,
        )


@pytest.mark.parametrize(
    ("output", "operation", "expected_fragment"),
    (
        ("not-a-receipt", "pause", "could not be verified"),
        (f"JOB_PAUSE {JOB_ID} future_state", "pause", "unrecognized state"),
        (f"JOB_PAUSE {JOB_ID} paused", "future", "not supported"),
    ),
)
def test_transition_receipt_errors_use_human_product_language(
    output: str,
    operation: str,
    expected_fragment: str,
) -> None:
    with pytest.raises(JobLifecycleError) as exc_info:
        parse_transition_receipt(
            output,
            expected_operation=operation,
            expected_job_id=JOB_ID,
        )

    message = str(exc_info.value)
    assert expected_fragment in message
    assert "durable" not in message.casefold()
    assert "lifecycle" not in message.casefold()
    assert "receipt" not in message.casefold()


def test_successful_transition_updates_selected_persisted_state_and_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    item = QListWidgetItem("QUEUED")
    item.setData(Qt.ItemDataRole.UserRole, JOB_ID)
    item.setData(Qt.ItemDataRole.UserRole + 1, "queued")
    workspace.jobs.blockSignals(True)
    workspace.jobs.addItem(item)
    workspace.jobs.setCurrentItem(item)
    workspace.jobs.blockSignals(False)
    workspace._selected_job_id = JOB_ID
    workspace._selected_state = "queued"
    workspace._operation = "pause"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = f"JOB_PAUSE {JOB_ID} paused\n"
    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace._selected_state == "paused"
        assert workspace.resume_button.isEnabled()
        assert not workspace.pause_button.isEnabled()
        assert workspace.status.text() == "PAUSE completed for job 11111111 · PAUSED."
        assert "transition" not in workspace.status.text().casefold()
        assert "persisted" not in workspace.status.text().casefold()
    finally:
        workspace.close()
        app.processEvents()


def test_unverified_receipt_fails_closed_and_preserves_raw_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    workspace._buffer = "not-a-receipt"
    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.status.property("pathenaUiState") == "error"
        details = workspace.details.toPlainText()
        assert "Diagnostic details:\nnot-a-receipt" in details
        assert "raw command output" not in details.casefold()
        assert workspace._selected_state == "queued"
    finally:
        workspace.close()
        app.processEvents()

def _job_list_line(
    *,
    job_id: str = JOB_ID,
    state: str = "queued",
    priority: int = 4,
    job_type: str = "research.run",
    stage: str = "discovery",
    retries: int = 2,
    updated_at_us: int = 123456,
    summary: str = "query=test",
) -> str:
    return "\t".join(
        (
            job_id,
            state,
            str(priority),
            job_type,
            stage,
            str(retries),
            str(updated_at_us),
            summary,
        )
    )


def test_job_list_parser_validates_complete_response_before_projection() -> None:
    rows = parse_job_list(_job_list_line())

    assert len(rows) == 1
    row = rows[0]
    assert row.job_id == JOB_ID
    assert row.state == "queued"
    assert row.priority == 4
    assert row.job_type == "research.run"
    assert row.stage == "discovery"
    assert row.retries == 2
    assert row.updated_at_us == 123456
    assert row.summary == "query=test"

    with pytest.raises(JobLifecycleError, match="line 2"):
        parse_job_list(_job_list_line() + "\nBROKEN")

    with pytest.raises(JobLifecycleError, match="unrecognized state"):
        parse_job_list(_job_list_line(state="future_state"))


def test_invalid_list_response_preserves_previous_selection_and_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)

    item = QListWidgetItem("QUEUED")
    item.setData(Qt.ItemDataRole.UserRole, JOB_ID)
    item.setData(Qt.ItemDataRole.UserRole + 1, "queued")
    workspace.jobs.blockSignals(True)
    workspace.jobs.addItem(item)
    workspace.jobs.setCurrentItem(item)
    workspace.jobs.blockSignals(False)
    workspace._selected_job_id = JOB_ID
    workspace._selected_state = "queued"
    workspace.details.setPlainText("Existing selected job details")
    workspace._operation = "list"
    workspace._operation_job_id = None
    workspace._buffer = _job_list_line() + "\nBROKEN"

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.jobs.count() == 1
        assert workspace.jobs.item(0).data(Qt.ItemDataRole.UserRole) == JOB_ID
        assert workspace._selected_job_id == JOB_ID
        assert workspace.details.toPlainText() == "Existing selected job details"
        assert workspace.status.property("pathenaUiState") == "error"
        assert "invalid" in workspace.status.text().casefold()
        assert "line 2" in workspace.status.toolTip()
        assert "line 2" in workspace.status.accessibleDescription()
    finally:
        workspace.close()
        app.processEvents()


def test_success_clears_stale_job_status_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    workspace._selected_job_id = JOB_ID
    workspace._selected_state = "queued"

    try:
        workspace._operation = "cancel"
        workspace._operation_job_id = JOB_ID
        workspace._buffer = "not-a-receipt"
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.status.toolTip()
        assert workspace.status.property("pathenaUiState") == "error"

        workspace._operation = "show"
        workspace._operation_job_id = JOB_ID
        workspace._buffer = f"JOB {JOB_ID}\nSTATE queued\n"
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.status.text() == "Job 11111111 details loaded."
        assert workspace.status.toolTip() == ""
        assert workspace.status.accessibleDescription() == workspace.status.text()
        assert workspace.status.property("pathenaUiState") == "success"
    finally:
        workspace.close()
        app.processEvents()


def test_process_error_is_not_overwritten_by_following_finished_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(JobsWorkspace, "refresh", lambda _self: None)
    app = _app()
    workspace = JobsWorkspace()
    workspace._refresh_timer.stop()
    workspace._scheduler_status_timer.stop()
    app.processEvents()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    workspace._selected_job_id = JOB_ID
    workspace._selected_state = "queued"
    workspace._operation = "pause"
    workspace._operation_job_id = JOB_ID

    try:
        workspace._process_error(QProcess.ProcessError.Crashed)
        error_text = workspace.status.text()

        assert error_text == "PAUSE for job 11111111 failed: Crashed"
        assert workspace.status.property("pathenaUiState") == "error"
        assert workspace._process_error_reported is True

        workspace._process_finished(1, QProcess.ExitStatus.CrashExit)

        assert workspace.status.text() == error_text
        assert workspace.status.property("pathenaUiState") == "error"
        assert workspace._process_error_reported is False
    finally:
        workspace.close()
        app.processEvents()

