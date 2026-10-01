from __future__ import annotations

import sqlite3
import uuid
from types import SimpleNamespace

import pytest

from athena.research.comparison import (
    ResearchComparisonError,
    ResearchComparisonService,
)


def _database() -> SimpleNamespace:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE research_scopes (
            scope_id BLOB PRIMARY KEY,
            job_id BLOB NOT NULL,
            query_text TEXT NOT NULL,
            mode TEXT NOT NULL,
            domains_json TEXT NOT NULL,
            project_ids_json TEXT NOT NULL,
            source_types_json TEXT NOT NULL,
            time_start_us INTEGER NULL,
            time_end_us INTEGER NULL,
            coverage_target REAL NOT NULL,
            state TEXT NOT NULL,
            created_at_us INTEGER NOT NULL
        );
        CREATE TABLE research_results (
            result_id BLOB PRIMARY KEY,
            scope_id BLOB NOT NULL,
            created_at_us INTEGER NOT NULL,
            snapshot_commit_seq INTEGER NOT NULL,
            model_signature_id BLOB NULL,
            synthesis_pipeline_version TEXT NOT NULL
        );
        """
    )
    return SimpleNamespace(connection=connection)


def _blob(value: uuid.UUID) -> bytes:
    return value.bytes


def _insert_result(
    database: SimpleNamespace,
    *,
    result_id: uuid.UUID,
    scope_id: uuid.UUID,
    job_id: uuid.UUID,
    created_at_us: int,
    snapshot_commit_seq: int,
    query: str = "What changed?",
    mode: str = "local_exhaustive",
    domains: str = "[]",
    projects: str = "[]",
    source_types: str = "[]",
    coverage_target: float = 1.0,
    state: str = "completed",
    pipeline: str = "research-synthesis-v1",
    model_signature_id: uuid.UUID | None = None,
) -> None:
    database.connection.execute(
        """
        INSERT INTO research_scopes (
            scope_id, job_id, query_text, mode, domains_json, project_ids_json,
            source_types_json, time_start_us, time_end_us, coverage_target, state,
            created_at_us
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?)
        """,
        (
            _blob(scope_id),
            _blob(job_id),
            query,
            mode,
            domains,
            projects,
            source_types,
            coverage_target,
            state,
            created_at_us,
        ),
    )
    database.connection.execute(
        """
        INSERT INTO research_results (
            result_id, scope_id, created_at_us, snapshot_commit_seq,
            model_signature_id, synthesis_pipeline_version
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            _blob(result_id),
            _blob(scope_id),
            created_at_us,
            snapshot_commit_seq,
            None if model_signature_id is None else _blob(model_signature_id),
            pipeline,
        ),
    )
    database.connection.commit()


def _view(
    result_id: uuid.UUID,
    job_id: uuid.UUID,
    *,
    summary: str,
    findings: list[str],
    contradictions: list[str] | None = None,
    sources: list[uuid.UUID] | None = None,
    coverage_ratio: float = 1.0,
    uncertainty: str = "",
) -> dict[str, object]:
    source_ids = [str(item) for item in (sources or [])]
    return {
        "result_id": str(result_id),
        "job_id": str(job_id),
        "query": "What changed?",
        "scope_state": "completed",
        "coverage": {"coverage_ratio": coverage_ratio},
        "content": {
            "summary": summary,
            "findings": findings,
            "contradictions": contradictions or [],
            "uncertainty": uncertainty,
        },
        "evidence": {
            "findings": [
                {
                    "ordinal": index,
                    "text": text,
                    "source_ids": source_ids,
                    "source_anchor_ids": [],
                    "source_analysis_artifact_ids": [],
                }
                for index, text in enumerate(findings)
            ],
            "contradictions": [],
        },
    }


def test_previous_comparison_skips_newer_incomparable_run_and_diffs_persisted_truth() -> None:
    database = _database()
    baseline_result = uuid.UUID("11111111-1111-1111-1111-111111111111")
    baseline_scope = uuid.UUID("12111111-1111-1111-1111-111111111111")
    baseline_job = uuid.UUID("13111111-1111-1111-1111-111111111111")
    ignored_result = uuid.UUID("21111111-1111-1111-1111-111111111111")
    ignored_scope = uuid.UUID("22111111-1111-1111-1111-111111111111")
    ignored_job = uuid.UUID("23111111-1111-1111-1111-111111111111")
    current_result = uuid.UUID("31111111-1111-1111-1111-111111111111")
    current_scope = uuid.UUID("32111111-1111-1111-1111-111111111111")
    current_job = uuid.UUID("33111111-1111-1111-1111-111111111111")
    baseline_model = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    current_model = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    old_source = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    new_source = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")

    _insert_result(
        database,
        result_id=baseline_result,
        scope_id=baseline_scope,
        job_id=baseline_job,
        created_at_us=100,
        snapshot_commit_seq=10,
        model_signature_id=baseline_model,
    )
    _insert_result(
        database,
        result_id=ignored_result,
        scope_id=ignored_scope,
        job_id=ignored_job,
        created_at_us=150,
        snapshot_commit_seq=15,
        query="Different research question",
    )
    _insert_result(
        database,
        result_id=current_result,
        scope_id=current_scope,
        job_id=current_job,
        created_at_us=200,
        snapshot_commit_seq=20,
        model_signature_id=current_model,
    )

    views = {
        baseline_result: _view(
            baseline_result,
            baseline_job,
            summary="Old summary",
            findings=["Stable finding", "Removed finding"],
            contradictions=["Old contradiction"],
            sources=[old_source],
            coverage_ratio=0.5,
            uncertainty="Old uncertainty",
        ),
        current_result: _view(
            current_result,
            current_job,
            summary="Current summary",
            findings=["Stable finding", "Added finding"],
            contradictions=["New contradiction"],
            sources=[new_source],
            coverage_ratio=1.0,
            uncertainty="Current uncertainty",
        ),
    }
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=views.__getitem__,
    )

    delta = service.compare_previous(current_job)

    assert delta is not None
    assert delta.baseline_result_id == baseline_result
    assert delta.current_result_id == current_result
    assert delta.added_findings == ("Added finding",)
    assert delta.removed_findings == ("Removed finding",)
    assert delta.added_contradictions == ("New contradiction",)
    assert delta.removed_contradictions == ("Old contradiction",)
    assert delta.added_source_ids == (new_source,)
    assert delta.removed_source_ids == (old_source,)
    assert delta.summary_changed is True
    assert delta.uncertainty_changed is True
    assert delta.model_signature_changed is True
    assert delta.baseline_coverage_ratio == pytest.approx(0.5)
    assert delta.current_coverage_ratio == pytest.approx(1.0)

    payload = delta.as_dict()
    assert payload["comparison_mode"] == "exact_persisted_text_and_provenance"
    assert payload["available"] is True


def test_comparison_preserves_duplicate_counts_in_exact_text_delta() -> None:
    database = _database()
    baseline_result = uuid.UUID("41111111-1111-1111-1111-111111111111")
    baseline_scope = uuid.UUID("42111111-1111-1111-1111-111111111111")
    baseline_job = uuid.UUID("43111111-1111-1111-1111-111111111111")
    current_result = uuid.UUID("51111111-1111-1111-1111-111111111111")
    current_scope = uuid.UUID("52111111-1111-1111-1111-111111111111")
    current_job = uuid.UUID("53111111-1111-1111-1111-111111111111")
    _insert_result(
        database,
        result_id=baseline_result,
        scope_id=baseline_scope,
        job_id=baseline_job,
        created_at_us=100,
        snapshot_commit_seq=1,
    )
    _insert_result(
        database,
        result_id=current_result,
        scope_id=current_scope,
        job_id=current_job,
        created_at_us=200,
        snapshot_commit_seq=2,
    )
    views = {
        baseline_result: _view(
            baseline_result,
            baseline_job,
            summary="Summary",
            findings=["Repeated", "Repeated"],
        ),
        current_result: _view(
            current_result,
            current_job,
            summary="Summary",
            findings=["Repeated"],
        ),
    }
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=views.__getitem__,
    )

    delta = service.compare_previous(current_result)

    assert delta is not None
    assert delta.added_findings == ()
    assert delta.removed_findings == ("Repeated",)


def test_explicit_comparison_rejects_incomparable_scope_without_model_inference() -> None:
    database = _database()
    baseline_result = uuid.UUID("61111111-1111-1111-1111-111111111111")
    baseline_scope = uuid.UUID("62111111-1111-1111-1111-111111111111")
    baseline_job = uuid.UUID("63111111-1111-1111-1111-111111111111")
    current_result = uuid.UUID("71111111-1111-1111-1111-111111111111")
    current_scope = uuid.UUID("72111111-1111-1111-1111-111111111111")
    current_job = uuid.UUID("73111111-1111-1111-1111-111111111111")
    _insert_result(
        database,
        result_id=baseline_result,
        scope_id=baseline_scope,
        job_id=baseline_job,
        created_at_us=100,
        snapshot_commit_seq=1,
        domains='["example.com"]',
    )
    _insert_result(
        database,
        result_id=current_result,
        scope_id=current_scope,
        job_id=current_job,
        created_at_us=200,
        snapshot_commit_seq=2,
        domains='["other.example"]',
    )
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=lambda _identifier: {},
    )

    with pytest.raises(ResearchComparisonError, match="not comparable"):
        service.compare(
            current_result,
            baseline_identifier=baseline_result,
        )


def test_compare_previous_returns_none_when_no_earlier_comparable_result() -> None:
    database = _database()
    result_id = uuid.UUID("81111111-1111-1111-1111-111111111111")
    scope_id = uuid.UUID("82111111-1111-1111-1111-111111111111")
    job_id = uuid.UUID("83111111-1111-1111-1111-111111111111")
    _insert_result(
        database,
        result_id=result_id,
        scope_id=scope_id,
        job_id=job_id,
        created_at_us=100,
        snapshot_commit_seq=1,
    )
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=lambda _identifier: {},
    )

    assert service.compare_previous(job_id) is None


def test_comparison_requires_completed_current_result() -> None:
    database = _database()
    result_id = uuid.UUID("91111111-1111-1111-1111-111111111111")
    scope_id = uuid.UUID("92111111-1111-1111-1111-111111111111")
    job_id = uuid.UUID("93111111-1111-1111-1111-111111111111")
    _insert_result(
        database,
        result_id=result_id,
        scope_id=scope_id,
        job_id=job_id,
        created_at_us=100,
        snapshot_commit_seq=1,
        state="partial",
    )
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=lambda _identifier: {},
    )

    with pytest.raises(ResearchComparisonError, match="current result is not completed"):
        service.compare_previous(job_id)

def test_previous_run_order_uses_scope_start_not_late_result_finalization() -> None:
    database = _database()
    baseline_result = uuid.UUID("a1111111-1111-1111-1111-111111111111")
    baseline_scope = uuid.UUID("a2111111-1111-1111-1111-111111111111")
    baseline_job = uuid.UUID("a3111111-1111-1111-1111-111111111111")
    current_result = uuid.UUID("b1111111-1111-1111-1111-111111111111")
    current_scope = uuid.UUID("b2111111-1111-1111-1111-111111111111")
    current_job = uuid.UUID("b3111111-1111-1111-1111-111111111111")

    _insert_result(
        database,
        result_id=baseline_result,
        scope_id=baseline_scope,
        job_id=baseline_job,
        created_at_us=100,
        snapshot_commit_seq=10,
    )
    _insert_result(
        database,
        result_id=current_result,
        scope_id=current_scope,
        job_id=current_job,
        created_at_us=200,
        snapshot_commit_seq=20,
    )
    database.connection.execute(
        "UPDATE research_results SET created_at_us = 300 WHERE result_id = ?",
        (_blob(baseline_result),),
    )
    database.connection.execute(
        "UPDATE research_results SET created_at_us = 250 WHERE result_id = ?",
        (_blob(current_result),),
    )
    database.connection.commit()

    views = {
        baseline_result: _view(
            baseline_result,
            baseline_job,
            summary="Earlier scope",
            findings=["Before"],
        ),
        current_result: _view(
            current_result,
            current_job,
            summary="Later scope",
            findings=["After"],
        ),
    }
    service = ResearchComparisonService(
        database=database,  # type: ignore[arg-type]
        result_view=views.__getitem__,
    )

    delta = service.compare_previous(current_job)

    assert delta is not None
    assert delta.baseline_result_id == baseline_result
    assert delta.current_result_id == current_result

