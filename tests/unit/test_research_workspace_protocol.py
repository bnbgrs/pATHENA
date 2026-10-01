from __future__ import annotations

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
