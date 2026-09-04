from __future__ import annotations

import uuid

import pytest

from athena.research.errors import ResearchStateError
from athena.research.source_coverage import (
    SOURCE_COVERAGE_FORMULA_ID,
    SourceCoverage,
)


def test_source_coverage_counts_only_successful_or_irrelevant_units() -> None:
    source_id = uuid.uuid4()
    coverage = SourceCoverage(
        source_id=source_id,
        unit_total=6,
        successful_count=2,
        irrelevant_count=1,
        failed_count=1,
        unavailable_count=1,
        excluded_count=1,
    )

    assert coverage.eligible_count == 5
    assert coverage.processed_count == 5
    assert coverage.coverage_positive_count == 3
    assert coverage.coverage_ratio == pytest.approx(3 / 5)
    assert coverage.fully_covered is False
    assert coverage.result_payload() == {
        "formula_id": SOURCE_COVERAGE_FORMULA_ID,
        "source_id": str(source_id),
        "unit_total": 6,
        "processed_count": 5,
        "successful_count": 2,
        "irrelevant_count": 1,
        "failed_count": 1,
        "unavailable_count": 1,
        "excluded_count": 1,
        "eligible_count": 5,
        "coverage_ratio": pytest.approx(3 / 5),
    }


def test_source_coverage_requires_every_eligible_unit_for_full_coverage() -> None:
    coverage = SourceCoverage(
        source_id=uuid.uuid4(),
        unit_total=4,
        successful_count=3,
        irrelevant_count=1,
        failed_count=0,
        unavailable_count=0,
    )

    assert coverage.coverage_ratio == 1.0
    assert coverage.fully_covered is True


def test_source_coverage_does_not_synthesize_full_coverage_for_zero_eligible_units() -> None:
    coverage = SourceCoverage(
        source_id=uuid.uuid4(),
        unit_total=2,
        successful_count=0,
        irrelevant_count=0,
        failed_count=0,
        unavailable_count=0,
        excluded_count=2,
    )

    assert coverage.eligible_count == 0
    assert coverage.coverage_ratio == 0.0
    assert coverage.fully_covered is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("unit_total", True),
        ("successful_count", -1),
        ("irrelevant_count", 1.5),
        ("failed_count", False),
        ("unavailable_count", -2),
        ("excluded_count", "1"),
    ],
)
def test_source_coverage_rejects_invalid_counts(field: str, value: object) -> None:
    values: dict[str, object] = {
        "source_id": uuid.uuid4(),
        "unit_total": 2,
        "successful_count": 1,
        "irrelevant_count": 0,
        "failed_count": 0,
        "unavailable_count": 0,
        "excluded_count": 0,
    }
    values[field] = value

    with pytest.raises(ResearchStateError):
        SourceCoverage(**values)  # type: ignore[arg-type]


def test_source_coverage_rejects_impossible_terminal_totals() -> None:
    with pytest.raises(
        ResearchStateError,
        match="terminal source work exceeds the eligible source-unit count",
    ):
        SourceCoverage(
            source_id=uuid.uuid4(),
            unit_total=2,
            successful_count=1,
            irrelevant_count=1,
            failed_count=1,
            unavailable_count=0,
        )


def test_source_coverage_rejects_invalid_source_id() -> None:
    with pytest.raises(TypeError, match="source_id must be a UUID"):
        SourceCoverage(
            source_id="not-a-uuid",  # type: ignore[arg-type]
            unit_total=1,
            successful_count=1,
            irrelevant_count=0,
            failed_count=0,
            unavailable_count=0,
        )
