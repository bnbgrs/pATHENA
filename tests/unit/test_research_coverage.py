from __future__ import annotations

import pytest

from athena.research.coverage import COVERAGE_FORMULA_ID, ResearchCoverage
from athena.research.errors import ResearchStateError
from athena.research.service import COVERAGE_FORMULA_ID as SERVICE_COVERAGE_FORMULA_ID


def test_coverage_formula_identity_matches_research_job_contract() -> None:
    assert COVERAGE_FORMULA_ID == "eligible-success-or-irrelevant-v1"
    assert SERVICE_COVERAGE_FORMULA_ID == COVERAGE_FORMULA_ID


def test_coverage_counts_success_and_irrelevant_only() -> None:
    coverage = ResearchCoverage(
        candidate_total=10,
        successful_count=4,
        irrelevant_count=2,
        failed_count=1,
        unavailable_count=1,
        excluded_count=2,
    )

    assert coverage.eligible_count == 8
    assert coverage.processed_count == 8
    assert coverage.coverage_positive_count == 6
    assert coverage.coverage_ratio == 0.75
    assert coverage.fully_covered is False


def test_unavailable_and_failed_work_never_produce_full_coverage() -> None:
    coverage = ResearchCoverage(
        candidate_total=4,
        successful_count=1,
        irrelevant_count=1,
        failed_count=1,
        unavailable_count=1,
        excluded_count=0,
    )

    assert coverage.coverage_ratio == 0.5
    assert coverage.fully_covered is False


def test_full_coverage_requires_every_eligible_unit_to_be_positive_terminal() -> None:
    coverage = ResearchCoverage(
        candidate_total=5,
        successful_count=3,
        irrelevant_count=1,
        failed_count=0,
        unavailable_count=0,
        excluded_count=1,
    )

    assert coverage.coverage_ratio == 1.0
    assert coverage.fully_covered is True


def test_empty_eligible_set_does_not_claim_one_hundred_percent() -> None:
    coverage = ResearchCoverage(
        candidate_total=2,
        successful_count=0,
        irrelevant_count=0,
        failed_count=0,
        unavailable_count=0,
        excluded_count=2,
    )

    assert coverage.coverage_ratio == 0.0
    assert coverage.fully_covered is False


def test_result_payload_persists_formula_identity_and_problem_counts() -> None:
    coverage = ResearchCoverage(
        candidate_total=6,
        successful_count=2,
        irrelevant_count=1,
        failed_count=1,
        unavailable_count=1,
        excluded_count=1,
    )

    assert coverage.result_payload() == {
        "formula_id": COVERAGE_FORMULA_ID,
        "candidate_total": 6,
        "processed_count": 5,
        "successful_count": 2,
        "irrelevant_count": 1,
        "failed_count": 1,
        "unavailable_count": 1,
        "excluded_count": 1,
        "eligible_count": 5,
        "coverage_ratio": 0.6,
    }


@pytest.mark.parametrize(
    "field",
    [
        "candidate_total",
        "successful_count",
        "irrelevant_count",
        "failed_count",
        "unavailable_count",
        "excluded_count",
    ],
)
def test_coverage_rejects_bool_counts(field: str) -> None:
    values = {
        "candidate_total": 1,
        "successful_count": 0,
        "irrelevant_count": 0,
        "failed_count": 0,
        "unavailable_count": 0,
        "excluded_count": 0,
    }
    values[field] = True

    with pytest.raises(ResearchStateError):
        ResearchCoverage(**values)


def test_coverage_rejects_terminal_work_beyond_eligible_candidates() -> None:
    with pytest.raises(ResearchStateError, match="terminal Research work"):
        ResearchCoverage(
            candidate_total=3,
            successful_count=2,
            irrelevant_count=1,
            failed_count=0,
            unavailable_count=0,
            excluded_count=1,
        )
