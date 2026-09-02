from __future__ import annotations

import math
import uuid

import pytest

from athena.source.analysis_models import (
    AnalysisStage,
    AnalysisWorkState,
    SourceAnalysisArtifact,
    SourceAnalysisRecord,
    SourceAnalysisState,
    SourceAnalysisWorkItem,
)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _analysis(**overrides: object) -> SourceAnalysisRecord:
    values: dict[str, object] = {
        "analysis_id": _uuid(),
        "job_id": _uuid(),
        "source_id": _uuid(),
        "representation_id": _uuid(),
        "question": "What does the source establish?",
        "state": SourceAnalysisState.RUNNING,
        "model_signature_id": _uuid(),
        "pipeline_version": "source-analysis/1",
        "effective_context_limit": 4096,
        "output_reserve": 1024,
        "safety_margin": 256,
        "token_estimator": "test-estimator",
        "max_hierarchy_depth": 4,
        "total_map_units": 10,
        "completed_map_units": 4,
        "failed_map_units": 1,
        "coverage": 0.5,
        "final_artifact_id": None,
        "created_at_us": 100,
        "updated_at_us": 101,
    }
    values.update(overrides)
    return SourceAnalysisRecord(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "effective_context_limit",
        "output_reserve",
        "safety_margin",
        "max_hierarchy_depth",
        "total_map_units",
        "completed_map_units",
        "failed_map_units",
        "created_at_us",
        "updated_at_us",
    ],
)
def test_analysis_rejects_bool_integer_fields(field: str) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        _analysis(**{field: True})


@pytest.mark.parametrize("coverage", [True, math.nan, math.inf, -0.01, 1.01])
def test_analysis_rejects_invalid_coverage(coverage: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _analysis(coverage=coverage)


def test_analysis_rejects_budget_without_input_capacity() -> None:
    with pytest.raises(ValueError, match="leaves no input capacity"):
        _analysis(effective_context_limit=1024, output_reserve=768, safety_margin=256)


def test_analysis_rejects_map_counts_above_total() -> None:
    with pytest.raises(ValueError, match="exceed total_map_units"):
        _analysis(total_map_units=2, completed_map_units=2, failed_map_units=1)


def test_analysis_rejects_reverse_timestamp_order() -> None:
    with pytest.raises(ValueError, match="precedes created_at_us"):
        _analysis(created_at_us=200, updated_at_us=199)


def test_work_item_rejects_empty_idempotency_key() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        SourceAnalysisWorkItem(
            work_item_id=_uuid(),
            analysis_id=_uuid(),
            stage=AnalysisStage.MAP,
            level=0,
            ordinal=0,
            state=AnalysisWorkState.PENDING,
            idempotency_key=b"",
            attempt_count=0,
            created_at_us=1,
            updated_at_us=1,
        )


def test_work_item_rejects_bool_attempt_count() -> None:
    with pytest.raises(TypeError, match="attempt_count must be an integer"):
        SourceAnalysisWorkItem(
            work_item_id=_uuid(),
            analysis_id=_uuid(),
            stage=AnalysisStage.MAP,
            level=0,
            ordinal=0,
            state=AnalysisWorkState.PENDING,
            idempotency_key=b"key",
            attempt_count=True,  # type: ignore[arg-type]
            created_at_us=1,
            updated_at_us=1,
        )


def test_artifact_requires_sha256_length() -> None:
    with pytest.raises(ValueError, match="32-byte SHA-256"):
        SourceAnalysisArtifact(
            artifact_id=_uuid(),
            analysis_id=_uuid(),
            work_item_id=_uuid(),
            artifact_kind=AnalysisStage.MAP,
            level=0,
            ordinal=0,
            content_json="{}",
            content_hash=b"short",
            processing_run_id=_uuid(),
            created_at_us=1,
        )
