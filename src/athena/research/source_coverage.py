"""Deterministic source-internal coverage policy for Exhaustive Research."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.research.errors import ResearchStateError

SOURCE_COVERAGE_FORMULA_ID = "eligible-units-success-or-irrelevant-v1"


def _count(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ResearchStateError(f"{field} must be a non-negative integer.")
    return value


@dataclass(frozen=True, slots=True)
class SourceCoverage:
    """Coverage of required Research work units for one concrete source."""

    source_id: uuid.UUID
    unit_total: int
    successful_count: int
    irrelevant_count: int
    failed_count: int
    unavailable_count: int
    excluded_count: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, uuid.UUID):
            raise TypeError("source_id must be a UUID.")
        for value, field in (
            (self.unit_total, "unit_total"),
            (self.successful_count, "successful_count"),
            (self.irrelevant_count, "irrelevant_count"),
            (self.failed_count, "failed_count"),
            (self.unavailable_count, "unavailable_count"),
            (self.excluded_count, "excluded_count"),
        ):
            _count(value, field)
        if self.excluded_count > self.unit_total:
            raise ResearchStateError("excluded_count exceeds unit_total.")
        if self.processed_count > self.eligible_count:
            raise ResearchStateError(
                "terminal source work exceeds the eligible source-unit count."
            )

    @property
    def eligible_count(self) -> int:
        return self.unit_total - self.excluded_count

    @property
    def processed_count(self) -> int:
        return (
            self.successful_count
            + self.irrelevant_count
            + self.failed_count
            + self.unavailable_count
        )

    @property
    def coverage_positive_count(self) -> int:
        return self.successful_count + self.irrelevant_count

    @property
    def coverage_ratio(self) -> float:
        if self.eligible_count == 0:
            return 0.0
        return self.coverage_positive_count / self.eligible_count

    @property
    def fully_covered(self) -> bool:
        return self.eligible_count > 0 and self.coverage_positive_count == self.eligible_count

    def result_payload(self) -> dict[str, int | float | str]:
        """Return a stable, storage-ready source coverage representation."""

        return {
            "formula_id": SOURCE_COVERAGE_FORMULA_ID,
            "source_id": str(self.source_id),
            "unit_total": self.unit_total,
            "processed_count": self.processed_count,
            "successful_count": self.successful_count,
            "irrelevant_count": self.irrelevant_count,
            "failed_count": self.failed_count,
            "unavailable_count": self.unavailable_count,
            "excluded_count": self.excluded_count,
            "eligible_count": self.eligible_count,
            "coverage_ratio": self.coverage_ratio,
        }
