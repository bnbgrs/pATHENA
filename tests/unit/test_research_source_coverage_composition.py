from __future__ import annotations

import uuid

import pytest

from athena.research.errors import ResearchStateError
from athena.research.models import (
    ResearchCandidateEligibility,
    ResearchCandidateRecord,
    ResearchWorkItemRecord,
    ResearchWorkState,
)
from athena.research.source_coverage_composition import (
    SOURCE_COVERAGE_RESULT_KEY,
    research_result_content_with_source_coverage,
    source_coverage_result_payloads_from_records,
    source_coverages_from_records,
)


def _candidate(
    *,
    source_id: uuid.UUID,
    ordinal: int,
    eligibility: ResearchCandidateEligibility = ResearchCandidateEligibility.ELIGIBLE,
) -> ResearchCandidateRecord:
    candidate_id = uuid.uuid4()
    return ResearchCandidateRecord(
        candidate_id=candidate_id,
        candidate_set_id=uuid.uuid4(),
        source_id=source_id,
        ordinal=ordinal,
        content_sha256=bytes([ordinal + 1]) * 32,
        eligibility=eligibility,
        duplicate_of_candidate_id=(
            uuid.uuid4()
            if eligibility is ResearchCandidateEligibility.EXCLUDED_DUPLICATE
            else None
        ),
        created_at_us=1,
    )


def _work(candidate: ResearchCandidateRecord, state: ResearchWorkState) -> ResearchWorkItemRecord:
    return ResearchWorkItemRecord(
        work_item_id=uuid.uuid4(),
        scope_id=uuid.uuid4(),
        candidate_id=candidate.candidate_id,
        state=state,
        idempotency_key=b"k" * 32,
        source_processing_job_id=None,
        source_analysis_job_id=None,
        attempt_count=1,
        created_at_us=1,
        updated_at_us=1,
    )


def test_source_coverages_derive_real_terminal_states_without_hiding_failures() -> None:
    source_id = uuid.uuid4()
    successful = _candidate(source_id=source_id, ordinal=0)
    irrelevant = _candidate(source_id=source_id, ordinal=1)
    failed = _candidate(source_id=source_id, ordinal=2)
    unavailable = _candidate(source_id=source_id, ordinal=3)
    pending = _candidate(source_id=source_id, ordinal=4)
    duplicate = _candidate(
        source_id=source_id,
        ordinal=5,
        eligibility=ResearchCandidateEligibility.EXCLUDED_DUPLICATE,
    )

    (coverage,) = source_coverages_from_records(
        [successful, irrelevant, failed, unavailable, pending, duplicate],
        [
            _work(successful, ResearchWorkState.SUCCESSFUL),
            _work(irrelevant, ResearchWorkState.IRRELEVANT),
            _work(failed, ResearchWorkState.FAILED),
            _work(unavailable, ResearchWorkState.UNAVAILABLE),
        ],
    )

    assert coverage.source_id == source_id
    assert coverage.unit_total == 6
    assert coverage.excluded_count == 1
    assert coverage.eligible_count == 5
    assert coverage.processed_count == 4
    assert coverage.successful_count == 1
    assert coverage.irrelevant_count == 1
    assert coverage.failed_count == 1
    assert coverage.unavailable_count == 1
    assert coverage.coverage_ratio == pytest.approx(2 / 5)
    assert coverage.fully_covered is False


def test_source_coverages_are_stably_ordered_by_real_source_identity() -> None:
    first_id = uuid.UUID(int=1)
    second_id = uuid.UUID(int=2)
    first = _candidate(source_id=first_id, ordinal=0)
    second = _candidate(source_id=second_id, ordinal=0)

    coverages = source_coverages_from_records(
        [second, first],
        [
            _work(second, ResearchWorkState.SUCCESSFUL),
            _work(first, ResearchWorkState.SUCCESSFUL),
        ],
    )

    assert [coverage.source_id for coverage in coverages] == [first_id, second_id]


def test_source_coverages_fail_closed_on_unknown_or_duplicate_work_identity() -> None:
    candidate = _candidate(source_id=uuid.uuid4(), ordinal=0)
    unknown = _candidate(source_id=uuid.uuid4(), ordinal=0)

    with pytest.raises(ResearchStateError, match="unknown candidate"):
        source_coverages_from_records(
            [candidate],
            [_work(unknown, ResearchWorkState.SUCCESSFUL)],
        )

    work = _work(candidate, ResearchWorkState.SUCCESSFUL)
    with pytest.raises(ResearchStateError, match="multiple Research work items"):
        source_coverages_from_records([candidate], [work, work])


def test_source_coverage_result_payloads_are_storage_ready_and_truthful() -> None:
    source_id = uuid.UUID(int=9)
    successful = _candidate(source_id=source_id, ordinal=0)
    failed = _candidate(source_id=source_id, ordinal=1)

    payloads = source_coverage_result_payloads_from_records(
        [failed, successful],
        [
            _work(failed, ResearchWorkState.FAILED),
            _work(successful, ResearchWorkState.SUCCESSFUL),
        ],
    )

    assert payloads == (
        {
            "formula_id": "eligible-units-success-or-irrelevant-v1",
            "source_id": str(source_id),
            "unit_total": 2,
            "processed_count": 2,
            "successful_count": 1,
            "irrelevant_count": 0,
            "failed_count": 1,
            "unavailable_count": 0,
            "excluded_count": 0,
            "eligible_count": 2,
            "coverage_ratio": 0.5,
        },
    )


def test_research_result_content_reserves_truthful_source_coverage() -> None:
    source_id = uuid.UUID(int=17)
    successful = _candidate(source_id=source_id, ordinal=0)
    unavailable = _candidate(source_id=source_id, ordinal=1)

    payload = research_result_content_with_source_coverage(
        {"findings": ["grounded"]},
        [unavailable, successful],
        [
            _work(unavailable, ResearchWorkState.UNAVAILABLE),
            _work(successful, ResearchWorkState.SUCCESSFUL),
        ],
    )

    assert payload["findings"] == ["grounded"]
    assert payload[SOURCE_COVERAGE_RESULT_KEY] == [
        {
            "formula_id": "eligible-units-success-or-irrelevant-v1",
            "source_id": str(source_id),
            "unit_total": 2,
            "processed_count": 2,
            "successful_count": 1,
            "irrelevant_count": 0,
            "failed_count": 0,
            "unavailable_count": 1,
            "excluded_count": 0,
            "eligible_count": 2,
            "coverage_ratio": 0.5,
        }
    ]


def test_research_result_content_rejects_semantic_source_coverage_override() -> None:
    with pytest.raises(ResearchStateError, match="Core-owned source coverage"):
        research_result_content_with_source_coverage(
            {SOURCE_COVERAGE_RESULT_KEY: []},
            [],
            [],
        )
