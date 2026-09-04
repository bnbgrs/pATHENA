"""Deterministic Exhaustive Research coverage accounting policy.

The policy intentionally separates processed work from coverage-positive work:
failed and unavailable work units are terminal for resume/accounting purposes but
must never inflate coverage.
"""

from __future__ import annotations

from dataclasses import dataclass

from athena.research.errors import ResearchStateError


def _count(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ResearchStateError(f"{field} must be a non-negative integer.")
    return value


@dataclass(frozen=True, slots=True)
class ResearchCoverage:
    """Canonical coverage counters derived from one frozen candidate set."""

    candidate_total: int
    successful_count: int
    irrelevant_count: int
    failed_count: int
    unavailable_count: int
    excluded_count: int

    def __post_init__(self) -> None:
        for value, field in (
            (self.candidate_total, "candidate_total"),
            (self.successful_count, "successful_count"),
            (self.irrelevant_count, "irrelevant_count"),
            (self.failed_count, "failed_count"),
            (self.unavailable_count, "unavailable_count"),
            (self.excluded_count, "excluded_count"),
        ):
            _count(value, field)

        if self.excluded_count > self.candidate_total:
            raise ResearchStateError("excluded_count exceeds candidate_total.")
        if self.processed_count > self.eligible_count:
            raise ResearchStateError(
                "terminal Research work exceeds the eligible candidate count."
            )

    @property
    def eligible_count(self) -> int:
        return self.candidate_total - self.excluded_count

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
        """Return covered eligible work without treating failures as coverage."""

        if self.eligible_count == 0:
            return 0.0
        return self.coverage_positive_count / self.eligible_count

    @property
    def fully_covered(self) -> bool:
        """True only when every eligible work unit succeeded or was irrelevant."""

        return self.eligible_count > 0 and self.coverage_positive_count == self.eligible_count
