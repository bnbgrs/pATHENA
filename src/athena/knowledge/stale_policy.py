"""Compatibility surface for stale Knowledge maintenance signals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.knowledge.staleness_policy import (
    KnowledgeStalenessReason,
    _assess_temporal_staleness,
)


class StaleKnowledgeState(str, Enum):
    """Maintenance state without making a truth judgment about Knowledge."""

    CURRENT_OR_UNKNOWN = "current_or_unknown"
    STALE_SIGNAL = "stale_signal"


class StaleKnowledgeReason(str, Enum):
    """Concrete evidence that can trigger a stale maintenance signal."""

    VALIDITY_ENDED = "validity_ended"
    SOURCE_AGE_EXCEEDED = "source_age_exceeded"


_REASON_MAP = {
    KnowledgeStalenessReason.VALIDITY_ENDED: StaleKnowledgeReason.VALIDITY_ENDED,
    KnowledgeStalenessReason.SOURCE_AGE_EXCEEDED: StaleKnowledgeReason.SOURCE_AGE_EXCEEDED,
}


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
    """Preserve the legacy stale-policy API on the canonical decision engine.

    This adapter keeps its established value-validation and result contract, but
    stale-maintenance decisions are delegated to ``KnowledgeStalenessPolicy``'s
    shared temporal evaluator. No second stale-rule implementation is retained.
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

        signals = _assess_temporal_staleness(
            assessed_at_us=now_us,
            valid_to_us=valid_to_us,
            source_observed_at_us=source_observed_at_us,
            max_source_age_us=max_source_age_us,
        )
        reasons = tuple(_REASON_MAP[reason] for reason in signals.reasons)
        state = (
            StaleKnowledgeState.STALE_SIGNAL
            if reasons
            else StaleKnowledgeState.CURRENT_OR_UNKNOWN
        )
        return StaleKnowledgeAssessment(state=state, reasons=reasons)

    @staticmethod
    def _validate_non_negative(name: str, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer timestamp/duration.")
