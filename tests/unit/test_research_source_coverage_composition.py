from __future__ import annotations

import sqlite3
import uuid
from dataclasses import replace

import pytest

from athena.common.ids import uuid_to_blob
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
    research_result_content_with_source_coverage_from_connection,
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


def test_connection_composition_reads_only_real_scope_rows_in_one_connection() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE research_candidate_sets (
            candidate_set_id BLOB PRIMARY KEY,
            scope_id BLOB NOT NULL
        );
        CREATE TABLE research_candidates (
            candidate_id BLOB PRIMARY KEY,
            candidate_set_id BLOB NOT NULL,
            source_id BLOB NOT NULL,
            ordinal INTEGER NOT NULL,
            content_sha256 BLOB NOT NULL,
            eligibility_state TEXT NOT NULL,
            duplicate_of_candidate_id BLOB,
            created_at_us INTEGER NOT NULL
        );
        CREATE TABLE research_work_items (
            work_item_id BLOB PRIMARY KEY,
            scope_id BLOB NOT NULL,
            candidate_id BLOB NOT NULL,
            state TEXT NOT NULL,
            idempotency_key BLOB NOT NULL,
            source_processing_job_id BLOB,
            source_analysis_job_id BLOB,
            attempt_count INTEGER NOT NULL,
            created_at_us INTEGER NOT NULL,
            updated_at_us INTEGER NOT NULL
        );
        """
    )
    scope_id = uuid.uuid4()
    other_scope_id = uuid.uuid4()
    source_id = uuid.UUID(int=31)
    successful = _candidate(source_id=source_id, ordinal=0)
    failed = _candidate(source_id=source_id, ordinal=1)
    other = _candidate(source_id=uuid.UUID(int=32), ordinal=0)

    for candidate, candidate_scope in (
        (successful, scope_id),
        (failed, scope_id),
        (other, other_scope_id),
    ):
        connection.execute(
            "INSERT INTO research_candidate_sets (candidate_set_id, scope_id) VALUES (?, ?)",
            (uuid_to_blob(candidate.candidate_set_id), uuid_to_blob(candidate_scope)),
        )
        connection.execute(
            """
            INSERT INTO research_candidates (
                candidate_id, candidate_set_id, source_id, ordinal,
                content_sha256, eligibility_state, duplicate_of_candidate_id,
                created_at_us
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uuid_to_blob(candidate.candidate_id),
                uuid_to_blob(candidate.candidate_set_id),
                uuid_to_blob(candidate.source_id),
                candidate.ordinal,
                candidate.content_sha256,
                candidate.eligibility.value,
                None,
                candidate.created_at_us,
            ),
        )

    for candidate, state, work_scope in (
        (successful, ResearchWorkState.SUCCESSFUL, scope_id),
        (failed, ResearchWorkState.FAILED, scope_id),
        (other, ResearchWorkState.SUCCESSFUL, other_scope_id),
    ):
        work = replace(_work(candidate, state), scope_id=work_scope)
        connection.execute(
            """
            INSERT INTO research_work_items (
                work_item_id, scope_id, candidate_id, state, idempotency_key,
                source_processing_job_id, source_analysis_job_id, attempt_count,
                created_at_us, updated_at_us
            ) VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?, ?)
            """,
            (
                uuid_to_blob(work.work_item_id),
                uuid_to_blob(work.scope_id),
                uuid_to_blob(work.candidate_id),
                work.state.value,
                work.idempotency_key,
                work.attempt_count,
                work.created_at_us,
                work.updated_at_us,
            ),
        )

    payload = research_result_content_with_source_coverage_from_connection(
        {"summary": "grounded"},
        connection,
        scope_id,
    )

    assert payload["summary"] == "grounded"
    assert payload[SOURCE_COVERAGE_RESULT_KEY] == [
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
        }
    ]
