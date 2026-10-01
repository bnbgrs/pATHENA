from __future__ import annotations

import json

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QListWidgetItem

from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_review import (
    ResearchReviewError,
    parse_research_delta_review,
    parse_research_result_review,
    render_research_delta_review,
    render_research_result_review,
)
from athena.desktop.research_workspace import ResearchWorkspace


def _payload() -> str:
    return json.dumps(
        {
            "result_id": "11111111-1111-1111-1111-111111111111",
            "job_id": "22222222-2222-2222-2222-222222222222",
            "query": "How should local memory evolve?",
            "scope_state": "completed",
            "snapshot_commit_seq": 42,
            "coverage": {
                "candidate_total": 3,
                "processed_count": 3,
                "successful_count": 2,
                "coverage_ratio": 1.0,
            },
            "content": {
                "summary": "Memory should remain useful and explainable.",
                "uncertainty": "One source disagrees about retention.",
            },
            "evidence": {
                "findings": [
                    {
                        "ordinal": 0,
                        "text": "Retain with purpose.",
                        "source_ids": ["aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"],
                        "source_anchor_ids": ["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"],
                        "source_analysis_artifact_ids": [
                            "cccccccc-cccc-cccc-cccc-cccccccccccc"
                        ],
                    }
                ],
                "contradictions": [
                    {
                        "ordinal": 0,
                        "text": "Retention limits differ.",
                        "source_ids": ["dddddddd-dddd-dddd-dddd-dddddddddddd"],
                        "source_anchor_ids": [],
                        "source_analysis_artifact_ids": [
                            "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
                        ],
                    }
                ],
            },
        }
    )


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _extension() -> tuple[ResearchWorkspace, ResearchResultsExtension]:
    _app()
    workspace = ResearchWorkspace()
    extension = ResearchResultsExtension(workspace)
    extension.refresh_timer.stop()
    item = QListWidgetItem("COMPLETED 100.0%  How should local memory evolve?")
    item.setData(
        Qt.ItemDataRole.UserRole,
        "22222222-2222-2222-2222-222222222222",
    )
    item.setData(Qt.ItemDataRole.UserRole + 1, "completed")
    workspace.jobs.blockSignals(True)
    workspace.jobs.addItem(item)
    workspace.jobs.setCurrentItem(item)
    workspace.jobs.blockSignals(False)
    workspace._selected_job_id = str(item.data(Qt.ItemDataRole.UserRole))
    workspace._selected_job_state = "completed"
    return workspace, extension


def test_persisted_result_becomes_immutable_review_with_provenance() -> None:
    review = parse_research_result_review(_payload())

    assert review.query == "How should local memory evolve?"
    assert review.evidence[0].kind == "contradiction"
    assert review.evidence[1].kind == "finding"
    assert review.evidence[1].source_ids == (
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    )

    rendered = render_research_result_review(review)
    assert "Memory should remain useful and explainable." in rendered
    assert "100.0% covered · 3/3 sources processed · 2 successful" in rendered
    assert "CONTRADICTION 1\nRetention limits differ." in rendered
    assert "Sources · AAAAAAAA" in rendered
    assert "Result 11111111 · Run 22222222 · Snapshot commit 42" in rendered


@pytest.mark.parametrize(
    ("change", "message"),
    (
        ({"query": ""}, "query is missing"),
        ({"coverage": {"coverage_ratio": 1.2}}, "outside 0..1"),
        ({"evidence": {"findings": "not-a-list"}}, "findings is invalid"),
    ),
)
def test_invalid_result_fails_closed_without_synthetic_review(
    change: dict[str, object], message: str
) -> None:
    payload = json.loads(_payload())
    payload.update(change)

    with pytest.raises(ResearchReviewError, match=message):
        parse_research_result_review(json.dumps(payload))


def test_empty_persisted_evidence_is_reported_honestly() -> None:
    payload = json.loads(_payload())
    payload["evidence"] = {"findings": [], "contradictions": []}
    review = parse_research_result_review(json.dumps(payload))

    assert "No finding-level provenance was persisted" in render_research_result_review(
        review
    )


def test_completed_result_is_rendered_only_for_its_selected_persisted_run() -> None:
    workspace, extension = _extension()
    try:
        extension._operation = "result"
        extension._operation_job_id = workspace._selected_job_id
        extension._buffer = _payload()
        extension._finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.details.toPlainText().startswith("RESEARCH RESULT\n")
        assert workspace.details.property("pathenaResearchResultId") == (
            "11111111-1111-1111-1111-111111111111"
        )
        assert workspace.details.property("pathenaResearchResultReviewState") == "ready"
        assert "Raw command output" not in workspace.details.toPlainText()
    finally:
        extension.refresh_timer.stop()
        workspace.close()


def test_unreadable_result_preserves_raw_output_and_recovers_controls() -> None:
    workspace, extension = _extension()
    try:
        extension._operation = "result"
        extension._operation_job_id = workspace._selected_job_id
        extension._buffer = "not-json"
        extension._finished(0, QProcess.ExitStatus.NormalExit)

        assert "RESULT REVIEW UNAVAILABLE" in workspace.details.toPlainText()
        assert "Raw command output:\nnot-json" in workspace.details.toPlainText()
        assert "unreadable result" in extension.proposal_status.text()
        assert workspace.details.property("pathenaResearchResultReviewState") == "error"
        assert extension.result_button.isEnabled()
    finally:
        extension.refresh_timer.stop()
        workspace.close()


def test_background_result_never_overwrites_newer_run_selection() -> None:
    workspace, extension = _extension()
    try:
        workspace.details.setPlainText("Current run remains visible")
        extension._operation = "result"
        extension._operation_job_id = "33333333-3333-3333-3333-333333333333"
        extension._buffer = _payload()
        extension._finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.details.toPlainText() == "Current run remains visible"
        assert "finished result in the background" in extension.proposal_status.text()
    finally:
        extension.refresh_timer.stop()
        workspace.close()

def _delta_payload(*, available: bool = True) -> str:
    if not available:
        return json.dumps(
            {
                "available": False,
                "reason": "No earlier comparable completed ResearchResult exists.",
            }
        )
    return json.dumps(
        {
            "available": True,
            "comparison_mode": "exact_persisted_text_and_provenance",
            "query": "How should local memory evolve?",
            "baseline": {
                "result_id": "11111111-1111-1111-1111-111111111111",
                "job_id": "21111111-1111-1111-1111-111111111111",
                "snapshot_commit_seq": 40,
                "model_signature_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "coverage_ratio": 0.5,
                "summary": "Old summary",
                "uncertainty": "Old uncertainty",
            },
            "current": {
                "result_id": "33333333-3333-3333-3333-333333333333",
                "job_id": "22222222-2222-2222-2222-222222222222",
                "snapshot_commit_seq": 42,
                "model_signature_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "coverage_ratio": 1.0,
                "summary": "New summary",
                "uncertainty": "New uncertainty",
            },
            "changes": {
                "summary_changed": True,
                "uncertainty_changed": True,
                "model_signature_changed": True,
                "added_findings": ["Added finding"],
                "removed_findings": ["Removed finding"],
                "added_contradictions": ["Added contradiction"],
                "removed_contradictions": [],
                "added_source_ids": ["dddddddd-dddd-dddd-dddd-dddddddddddd"],
                "removed_source_ids": ["cccccccc-cccc-cccc-cccc-cccccccccccc"],
            },
        }
    )


def test_research_delta_review_reports_exact_persisted_changes_and_method() -> None:
    review = parse_research_delta_review(_delta_payload())

    assert review.available is True
    assert review.added_findings == ("Added finding",)
    assert review.removed_source_ids == (
        "cccccccc-cccc-cccc-cccc-cccccccccccc",
    )
    rendered = render_research_delta_review(review)
    assert "RESEARCH CHANGES" in rendered
    assert "50.0% → 100.0% (+50.0 percentage points)" in rendered
    assert "+ Added finding" in rendered
    assert "- Removed finding" in rendered
    assert "no model decides semantic equivalence" in rendered
    assert "Model signature changed between runs" in rendered


def test_research_delta_unavailable_state_is_explicit_not_faked() -> None:
    review = parse_research_delta_review(_delta_payload(available=False))

    assert review.available is False
    assert render_research_delta_review(review) == (
        "RESEARCH CHANGES\n\n"
        "No earlier comparable completed ResearchResult exists."
    )


def test_completed_run_comparison_renders_only_for_owned_selection() -> None:
    workspace, extension = _extension()
    try:
        extension._operation = "compare"
        extension._operation_job_id = workspace._selected_job_id
        extension._buffer = _delta_payload()
        extension._finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.details.toPlainText().startswith("RESEARCH CHANGES\n")
        assert workspace.details.property("pathenaResearchComparisonState") == "ready"
        assert workspace.details.property("pathenaResearchBaselineResultId") == (
            "11111111-1111-1111-1111-111111111111"
        )
        assert workspace.details.property("pathenaResearchResultId") == (
            "33333333-3333-3333-3333-333333333333"
        )
    finally:
        extension.refresh_timer.stop()
        workspace.close()


def test_missing_prior_comparison_has_honest_unavailable_ui_state() -> None:
    workspace, extension = _extension()
    try:
        extension._operation = "compare"
        extension._operation_job_id = workspace._selected_job_id
        extension._buffer = _delta_payload(available=False)
        extension._finished(0, QProcess.ExitStatus.NormalExit)

        assert workspace.details.property("pathenaResearchComparisonState") == "unavailable"
        assert "No earlier comparable" in workspace.details.toPlainText()
        assert extension.compare_button.isEnabled()
    finally:
        extension.refresh_timer.stop()
        workspace.close()

