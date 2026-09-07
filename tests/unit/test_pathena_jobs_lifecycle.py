from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.app import create_application
from athena.desktop.jobs_lifecycle import (
    JobLifecycleError,
    action_availability,
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
        assert "PAUSED" in workspace.status.text()
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
        assert "Raw command output:\nnot-a-receipt" in workspace.details.toPlainText()
        assert workspace._selected_state == "queued"
    finally:
        workspace.close()
        app.processEvents()
