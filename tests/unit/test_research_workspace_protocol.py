from __future__ import annotations

import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.research_workspace import ResearchWorkspace
from athena.desktop.research_workspace_protocol import (
    ResearchWorkspaceProtocolError,
    parse_research_cancel_receipt,
    parse_research_comparison_receipt,
    parse_research_enqueue_receipt,
    parse_research_job_list,
)

JOB_ID = "11111111-1111-1111-1111-111111111111"
OTHER_JOB_ID = "22222222-2222-2222-2222-222222222222"


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _list_line(
    *,
    job_id: str = JOB_ID,
    state: str = "running",
    stage: str = "discovery",
    coverage: str = "0.375",
    query: str = "What changed?",
) -> str:
    return "\t".join((job_id, state, stage, coverage, query))




def _comparison_output(
    *,
    current_job_id: str = JOB_ID,
    available: bool = True,
) -> str:
    if not available:
        payload = {
            "available": False,
            "comparison_mode": "exact_persisted_text_and_provenance",
            "current_job_id": current_job_id,
        }
    else:
        payload = {
            "available": True,
            "comparison_mode": "exact_persisted_text_and_provenance",
            "query": "What changed?",
            "baseline": {
                "result_id": "31111111-1111-1111-1111-111111111111",
                "job_id": OTHER_JOB_ID,
                "snapshot_commit_seq": 10,
                "model_signature_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "coverage_ratio": 0.5,
                "summary": "Old summary",
                "uncertainty": "Old uncertainty",
            },
            "current": {
                "result_id": "41111111-1111-1111-1111-111111111111",
                "job_id": current_job_id,
                "snapshot_commit_seq": 20,
                "model_signature_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "coverage_ratio": 1.0,
                "summary": "Current summary",
                "uncertainty": "Current uncertainty",
            },
            "changes": {
                "summary_changed": True,
                "uncertainty_changed": True,
                "model_signature_changed": True,
                "added_findings": ["Added finding"],
                "removed_findings": ["Removed finding"],
                "added_contradictions": ["New contradiction"],
                "removed_contradictions": ["Old contradiction"],
                "added_source_ids": [
                    "cccccccc-cccc-cccc-cccc-cccccccccccc"
                ],
                "removed_source_ids": [
                    "dddddddd-dddd-dddd-dddd-dddddddddddd"
                ],
            },
        }
    return "RESEARCH_COMPARE " + json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"

def _workspace(monkeypatch: pytest.MonkeyPatch) -> ResearchWorkspace:
    monkeypatch.setattr(ResearchWorkspace, "refresh", lambda _self: None)
    workspace = ResearchWorkspace()
    monkeypatch.setattr(workspace, "_drain_output", lambda: None)
    return workspace


def _install_selected_job(
    workspace: ResearchWorkspace,
    *,
    job_id: str = JOB_ID,
    state: str = "queued",
) -> QListWidgetItem:
    item = QListWidgetItem(state.upper())
    item.setData(Qt.ItemDataRole.UserRole, job_id)
    item.setData(Qt.ItemDataRole.UserRole + 1, state)
    item.setData(Qt.ItemDataRole.UserRole + 2, "discovery")
    workspace.jobs.blockSignals(True)
    workspace.jobs.addItem(item)
    workspace.jobs.setCurrentItem(item)
    workspace.jobs.blockSignals(False)
    workspace._selected_job_id = job_id
    workspace._selected_job_state = state
    return item


def test_research_list_parser_validates_complete_response() -> None:
    rows = parse_research_job_list(
        _list_line() + "\n" + _list_line(
            job_id=OTHER_JOB_ID,
            state="completed",
            stage="complete",
            coverage="-",
            query="Second query",
        )
    )

    assert len(rows) == 2
    assert rows[0].job_id == JOB_ID
    assert rows[0].coverage == pytest.approx(0.375)
    assert rows[1].state == "completed"
    assert rows[1].coverage is None

    with pytest.raises(ResearchWorkspaceProtocolError, match="line 2"):
        parse_research_job_list(_list_line() + "\nBROKEN")

    with pytest.raises(ResearchWorkspaceProtocolError, match="invalid coverage"):
        parse_research_job_list(_list_line(coverage="nan"))

    with pytest.raises(ResearchWorkspaceProtocolError, match="invalid coverage"):
        parse_research_job_list(_list_line(coverage="1.001"))

    with pytest.raises(ResearchWorkspaceProtocolError, match="unrecognized state"):
        parse_research_job_list(_list_line(state="future_state"))


def test_enqueue_receipt_requires_one_valid_job_identity() -> None:
    output = f"JOB_QUEUED {JOB_ID}\nQUERY What changed?\n"
    assert parse_research_enqueue_receipt(output) == JOB_ID

    with pytest.raises(ResearchWorkspaceProtocolError, match="could not be verified"):
        parse_research_enqueue_receipt("QUERY What changed?\n")

    with pytest.raises(ResearchWorkspaceProtocolError, match="could not be verified"):
        parse_research_enqueue_receipt(
            f"JOB_QUEUED {JOB_ID}\nJOB_QUEUED {OTHER_JOB_ID}\n"
        )

    with pytest.raises(ResearchWorkspaceProtocolError, match="invalid queued job ID"):
        parse_research_enqueue_receipt("JOB_QUEUED not-a-uuid\n")


@pytest.mark.parametrize("state", ["cancelled", "cancel_requested"])
def test_cancel_receipt_binds_exact_job_and_service_state(state: str) -> None:
    receipt = parse_research_cancel_receipt(
        f"JOB_CANCEL {JOB_ID} {state}\n",
        expected_job_id=JOB_ID,
    )

    assert receipt.job_id == JOB_ID
    assert receipt.state == state

    with pytest.raises(ResearchWorkspaceProtocolError, match="another run"):
        parse_research_cancel_receipt(
            f"JOB_CANCEL {OTHER_JOB_ID} {state}\n",
            expected_job_id=JOB_ID,
        )

    with pytest.raises(ResearchWorkspaceProtocolError, match="unexpected state"):
        parse_research_cancel_receipt(
            f"JOB_CANCEL {JOB_ID} queued\n",
            expected_job_id=JOB_ID,
        )


def test_cancelled_receipt_replaces_old_fake_cancel_requested_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    item = _install_selected_job(workspace, state="queued")
    workspace._operation = "cancel"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = f"JOB_CANCEL {JOB_ID} cancelled\n"

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace._selected_job_state == "cancelled"
        assert item.data(Qt.ItemDataRole.UserRole + 1) == "cancelled"
        assert not workspace.cancel_button.isEnabled()
        assert "CANCELLED" in workspace.status.text()
        assert workspace.status.property("pathenaUiState") == "success"
        assert workspace.status.toolTip() == ""
    finally:
        workspace.close()
        app.processEvents()


def test_mismatched_cancel_receipt_fails_closed_without_mutating_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    item = _install_selected_job(workspace, state="running")
    workspace._operation = "cancel"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = f"JOB_CANCEL {OTHER_JOB_ID} cancel_requested\n"

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace._selected_job_state == "running"
        assert item.data(Qt.ItemDataRole.UserRole + 1) == "running"
        assert workspace.status.property("pathenaUiState") == "error"
        assert "could not be verified" in workspace.status.text().casefold()
        assert "another run" in workspace.status.toolTip()
    finally:
        workspace.close()
        app.processEvents()


def test_exit_zero_enqueue_without_receipt_preserves_user_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    workspace.query_input.setText("Keep this question")
    workspace._operation = "enqueue"
    workspace._buffer = "QUERY Keep this question\n"

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.query_input.text() == "Keep this question"
        assert workspace._selected_job_id is None
        assert workspace.status.property("pathenaUiState") == "error"
        assert "could not be verified" in workspace.status.text().casefold()
    finally:
        workspace.close()
        app.processEvents()


def test_invalid_exit_zero_list_preserves_existing_projection_and_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    item = _install_selected_job(workspace, state="running")
    workspace.details.setPlainText("Existing selected Research details")
    workspace._operation = "list"
    workspace._buffer = _list_line() + "\nBROKEN"

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.jobs.count() == 1
        assert workspace.jobs.item(0) is item
        assert workspace._selected_job_id == JOB_ID
        assert workspace.details.toPlainText() == "Existing selected Research details"
        assert workspace.status.property("pathenaUiState") == "error"
        assert "line 2" in workspace.status.toolTip()
        assert "line 2" in workspace.status.accessibleDescription()
    finally:
        workspace.close()
        app.processEvents()


def test_selection_change_while_show_runs_preserves_background_ownership(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    first = _install_selected_job(workspace, job_id=JOB_ID, state="running")
    second = QListWidgetItem("WAITING")
    second.setData(Qt.ItemDataRole.UserRole, OTHER_JOB_ID)
    second.setData(Qt.ItemDataRole.UserRole + 1, "waiting")
    second.setToolTip(f"{OTHER_JOB_ID}\nstate=waiting\nstage=discovery")
    workspace.jobs.addItem(second)
    workspace._operation = "show"
    workspace._operation_job_id = JOB_ID
    monkeypatch.setattr(workspace, "_busy", lambda: True)

    try:
        workspace._selection_changed(second, first)

        assert workspace._selected_job_id == OTHER_JOB_ID
        assert workspace._selected_job_state == "waiting"
        assert workspace.details.property("pathenaBackgroundOperationOwner") == JOB_ID
        details = workspace.details.toPlainText()
        assert "BACKGROUND" in details
        assert JOB_ID[:8].upper() in details
        assert OTHER_JOB_ID[:8].upper() in details
        assert "background output will not be written into this pane" in details
    finally:
        workspace.close()
        app.processEvents()


def test_process_error_is_not_overwritten_by_finished_signal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    _install_selected_job(workspace, state="running")
    workspace._operation = "show"
    workspace._operation_job_id = JOB_ID

    try:
        workspace._process_error(QProcess.ProcessError.Crashed)
        error_text = workspace.status.text()

        assert error_text == "Research command for run 11111111 failed: Crashed"
        assert workspace.status.property("pathenaUiState") == "error"
        assert workspace._process_error_reported is True

        workspace._process_finished(1, QProcess.ExitStatus.CrashExit)

        assert workspace.status.text() == error_text
        assert workspace.status.property("pathenaUiState") == "error"
        assert workspace._process_error_reported is False
    finally:
        workspace.close()
        app.processEvents()

def test_background_show_completion_loads_current_research_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    old_item = _install_selected_job(workspace, job_id=JOB_ID, state="running")
    new_item = QListWidgetItem("WAITING")
    new_item.setData(Qt.ItemDataRole.UserRole, OTHER_JOB_ID)
    new_item.setData(Qt.ItemDataRole.UserRole + 1, "waiting")
    workspace.jobs.blockSignals(True)
    workspace.jobs.addItem(new_item)
    workspace.jobs.setCurrentItem(new_item)
    workspace.jobs.blockSignals(False)
    workspace._selected_job_id = OTHER_JOB_ID
    workspace._selected_job_state = "waiting"
    workspace._operation = "show"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = f"JOB {JOB_ID}\nSTATE running\n"
    workspace.details.setProperty("pathenaBackgroundOperationOwner", JOB_ID)
    calls: list[tuple[str, list[str], str | None]] = []

    def _record_start(
        operation: str,
        arguments: list[str],
        _label: str,
        *,
        job_id: str | None = None,
    ) -> None:
        calls.append((operation, arguments, job_id))

    monkeypatch.setattr(workspace, "_start", _record_start)
    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)
        app.processEvents()

        assert workspace.jobs.currentItem() is new_item
        assert calls == [("show", ["show", OTHER_JOB_ID], OTHER_JOB_ID)]
        assert workspace.details.property("pathenaBackgroundOperationOwner") == ""
        assert old_item.data(Qt.ItemDataRole.UserRole) == JOB_ID
    finally:
        workspace.close()
        app.processEvents()


def test_comparison_receipt_binds_exact_run_and_persisted_delta() -> None:
    receipt = parse_research_comparison_receipt(
        _comparison_output(),
        expected_job_id=JOB_ID,
    )

    assert receipt.available is True
    assert receipt.current_job_id == JOB_ID
    assert receipt.baseline_job_id == OTHER_JOB_ID
    assert receipt.baseline_snapshot_commit_seq == 10
    assert receipt.current_snapshot_commit_seq == 20
    assert receipt.baseline_coverage == pytest.approx(0.5)
    assert receipt.current_coverage == pytest.approx(1.0)
    assert receipt.baseline_summary == "Old summary"
    assert receipt.current_summary == "Current summary"
    assert receipt.added_findings == ("Added finding",)
    assert receipt.removed_findings == ("Removed finding",)
    assert receipt.added_source_ids == (
        "cccccccc-cccc-cccc-cccc-cccccccccccc",
    )

    with pytest.raises(
        ResearchWorkspaceProtocolError,
        match="another run",
    ):
        parse_research_comparison_receipt(
            _comparison_output(current_job_id=OTHER_JOB_ID),
            expected_job_id=JOB_ID,
        )


def test_comparison_receipt_represents_no_previous_match_without_fake_delta() -> None:
    receipt = parse_research_comparison_receipt(
        _comparison_output(available=False),
        expected_job_id=JOB_ID,
    )

    assert receipt.available is False
    assert receipt.current_job_id == JOB_ID
    assert receipt.baseline_job_id is None
    assert receipt.added_findings == ()
    assert receipt.removed_findings == ()
    assert receipt.baseline_summary == ""


def test_comparison_action_requires_completed_selected_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    item = _install_selected_job(workspace, state="running")

    try:
        workspace._sync_compare_button()
        assert workspace.compare_button.isEnabled() is False
        assert "cannot be compared" in workspace.compare_button.toolTip()

        item.setData(Qt.ItemDataRole.UserRole + 1, "completed")
        workspace._selected_job_state = "completed"
        workspace._sync_compare_button()

        assert workspace.compare_button.isEnabled() is True
        assert (
            workspace.compare_button.property(
                "pathenaResearchComparisonAvailable"
            )
            is True
        )
    finally:
        workspace.close()
        app.processEvents()


def test_verified_comparison_renders_exact_persisted_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    _install_selected_job(workspace, state="completed")
    workspace._operation = "compare"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = _comparison_output()

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        details = workspace.details.toPlainText()
        assert "EXACT PERSISTED TEXT + PROVENANCE" in details
        assert f"RUNS {OTHER_JOB_ID} → {JOB_ID}" in details
        assert "COVERAGE 50.0% → 100.0%" in details
        assert "BASELINE SUMMARY Old summary" in details
        assert "CURRENT SUMMARY Current summary" in details
        assert "ADDED FINDINGS 1" in details
        assert "+ Added finding" in details
        assert "REMOVED FINDINGS 1" in details
        assert "+ Removed finding" in details
        assert workspace.details.property("pathenaUiState") == "success"
        assert "compared with previous" in workspace.status.text().casefold()
    finally:
        workspace.close()
        app.processEvents()


def test_no_previous_comparable_run_renders_explicit_empty_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app()
    workspace = _workspace(monkeypatch)
    _install_selected_job(workspace, state="completed")
    workspace._operation = "compare"
    workspace._operation_job_id = JOB_ID
    workspace._buffer = _comparison_output(available=False)

    try:
        workspace._process_finished(0, QProcess.ExitStatus.NormalExit)

        assert "NO EARLIER COMPARABLE RUN" in workspace.details.toPlainText()
        assert workspace.details.property("pathenaUiState") == "empty"
        assert "no earlier comparable run" in workspace.status.text().casefold()
    finally:
        workspace.close()
        app.processEvents()
