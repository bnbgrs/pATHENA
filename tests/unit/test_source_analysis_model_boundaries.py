from __future__ import annotations

import uuid

import pytest

from athena.source.analysis_models import SourceAnalysisRecord, SourceAnalysisState


def _record(*, coverage: object = 1.0) -> SourceAnalysisRecord:
    return SourceAnalysisRecord(
        analysis_id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        representation_id=uuid.uuid4(),
        question="question",
        state=SourceAnalysisState.RUNNING,
        model_signature_id=uuid.uuid4(),
        pipeline_version="v1",
        effective_context_limit=4096,
        output_reserve=512,
        safety_margin=128,
        token_estimator="estimate-v1",
        max_hierarchy_depth=4,
        total_map_units=1,
        completed_map_units=0,
        failed_map_units=0,
        coverage=coverage,  # type: ignore[arg-type]
        final_artifact_id=None,
        created_at_us=1,
        updated_at_us=1,
    )


@pytest.mark.parametrize(
    "coverage",
    [True, False, float("nan"), float("inf"), float("-inf"), -0.1, 1.1, 10**400],
)
def test_source_analysis_record_rejects_invalid_coverage(coverage: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _record(coverage=coverage)


@pytest.mark.parametrize("coverage", [0, 0.0, 0.5, 1, 1.0])
def test_source_analysis_record_accepts_unit_interval_coverage(coverage: object) -> None:
    record = _record(coverage=coverage)

    assert 0.0 <= float(record.coverage) <= 1.0
