"""Deterministic maintenance policy for stale Knowledge signals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StaleKnowledgeState(str, Enum):
    """Maintenance state without making a truth judgment about Knowledge."""

    CURRENT_OR_UNKNOWN = "current_or_unknown"
    STALE_SIGNAL = "stale_signal"


class StaleKnowledgeReason(str, Enum):
    """Concrete evidence that can trigger a stale maintenance signal."""

    VALIDITY_ENDED = "validity_ended"
    SOURCE_AGE_EXCEEDED = "source_age_exceeded"


@dataclass(frozen=True, slots=True)
class StaleKnowledgeAssessment:
    """Explain why Knowledge should or should not enter stale maintenance."""

    state: StaleKnowledgeState
    reasons: tuple[StaleKnowledgeReason, ...]

    @property
    def requires_revalidation(self) -> bool:
        """Return whether maintenance should consider revalidation."""

        return self.state is StaleKnowledgeState.STALE_SIGNAL


class StaleKnowledgePolicy:
    """Evaluate Beta §63 stale signals without changing canonical truth/status.

    A passed validity end or sufficiently old source observation can request
    maintenance. Missing information remains unknown/current and never invents
    staleness. This policy does not mutate Knowledge, Claims, or provenance.
    """

    @staticmethod
    def assess(
        *,
        now_us: int,
        valid_to_us: int | None = None,
        source_observed_at_us: int | None = None,
        max_source_age_us: int | None = None,
    ) -> StaleKnowledgeAssessment:
        StaleKnowledgePolicy._validate_non_negative("now_us", now_us)
        if valid_to_us is not None:
            StaleKnowledgePolicy._validate_non_negative("valid_to_us", valid_to_us)
        if source_observed_at_us is not None:
            StaleKnowledgePolicy._validate_non_negative(
                "source_observed_at_us", source_observed_at_us
            )
        if max_source_age_us is not None:
            StaleKnowledgePolicy._validate_non_negative(
                "max_source_age_us", max_source_age_us
            )
        if (source_observed_at_us is None) is not (max_source_age_us is None):
            raise ValueError(
                "Source-age assessment requires both source_observed_at_us and "
                "max_source_age_us."
            )
        if source_observed_at_us is not None and source_observed_at_us > now_us:
            raise ValueError("source_observed_at_us cannot be later than now_us.")

        reasons: list[StaleKnowledgeReason] = []
        if valid_to_us is not None and valid_to_us < now_us:
            reasons.append(StaleKnowledgeReason.VALIDITY_ENDED)
        if (
            source_observed_at_us is not None
            and max_source_age_us is not None
            and now_us - source_observed_at_us > max_source_age_us
        ):
            reasons.append(StaleKnowledgeReason.SOURCE_AGE_EXCEEDED)

        frozen_reasons = tuple(reasons)
        state = (
            StaleKnowledgeState.STALE_SIGNAL
            if frozen_reasons
            else StaleKnowledgeState.CURRENT_OR_UNKNOWN
        )
        return StaleKnowledgeAssessment(state=state, reasons=frozen_reasons)

    @staticmethod
    def _validate_non_negative(name: str, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer timestamp/duration.")
