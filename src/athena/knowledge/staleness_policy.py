"""Deterministic staleness signaling for canonical Knowledge revisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.knowledge.models import KnowledgeUnitRevision


class KnowledgeStalenessState(str, Enum):
    """What recorded temporal evidence can truthfully say about staleness."""

    STALE_BY_VALIDITY = "stale_by_validity"
    STALE_BY_SOURCE_AGE = "stale_by_source_age"
    STALE_BY_MULTIPLE_SIGNALS = "stale_by_multiple_signals"
    NOT_STALE_BY_RECORDED_EVIDENCE = "not_stale_by_recorded_evidence"
    INSUFFICIENT_TEMPORAL_EVIDENCE = "insufficient_temporal_evidence"


class KnowledgeStalenessReason(str, Enum):
    """Recorded maintenance evidence that justifies a stale signal."""

    VALIDITY_ENDED = "validity_ended"
    SOURCE_AGE_EXCEEDED = "source_age_exceeded"


@dataclass(frozen=True, slots=True)
class KnowledgeStalenessAssessment:
    """Explain a staleness signal without turning it into a truth verdict."""

    state: KnowledgeStalenessState
    reasons: tuple[KnowledgeStalenessReason, ...]
    knowledge_id: str
    revision_id: str
    valid_from_us: int | None
    valid_to_us: int | None
    source_observed_at_us: int | None
    max_source_age_us: int | None
    assessed_at_us: int

    @property
    def should_signal_stale(self) -> bool:
        """Return whether recorded maintenance evidence justifies a stale signal."""

        return bool(self.reasons)


@dataclass(frozen=True, slots=True)
class _TemporalStalenessSignals:
    """Shared temporal decision result used by all Knowledge stale-policy adapters."""

    reasons: tuple[KnowledgeStalenessReason, ...]
    has_recorded_temporal_evidence: bool


class KnowledgeStalenessPolicy:
    """Apply Beta stale-Knowledge semantics using only explicit recorded evidence.

    Recorded validity and explicitly supplied source-observation age may emit a
    maintenance signal. The policy never infers source timestamps, falsity, or
    replacement revisions. Missing evidence therefore remains unknown instead
    of being reported as current forever.
    """

    @staticmethod
    def assess(
        revision: KnowledgeUnitRevision,
        *,
        assessed_at_us: int,
        source_observed_at_us: int | None = None,
        max_source_age_us: int | None = None,
    ) -> KnowledgeStalenessAssessment:
        if not isinstance(revision, KnowledgeUnitRevision):
            raise TypeError("Staleness assessment requires a KnowledgeUnitRevision.")

        valid_to_us = revision.payload.valid_to_us
        signals = _assess_temporal_staleness(
            assessed_at_us=assessed_at_us,
            valid_to_us=valid_to_us,
            source_observed_at_us=source_observed_at_us,
            max_source_age_us=max_source_age_us,
        )

        if len(signals.reasons) > 1:
            state = KnowledgeStalenessState.STALE_BY_MULTIPLE_SIGNALS
        elif signals.reasons == (KnowledgeStalenessReason.VALIDITY_ENDED,):
            state = KnowledgeStalenessState.STALE_BY_VALIDITY
        elif signals.reasons == (KnowledgeStalenessReason.SOURCE_AGE_EXCEEDED,):
            state = KnowledgeStalenessState.STALE_BY_SOURCE_AGE
        elif not signals.has_recorded_temporal_evidence:
            state = KnowledgeStalenessState.INSUFFICIENT_TEMPORAL_EVIDENCE
        else:
            state = KnowledgeStalenessState.NOT_STALE_BY_RECORDED_EVIDENCE

        return KnowledgeStalenessAssessment(
            state=state,
            reasons=signals.reasons,
            knowledge_id=str(revision.knowledge_id),
            revision_id=str(revision.revision_id),
            valid_from_us=revision.payload.valid_from_us,
            valid_to_us=valid_to_us,
            source_observed_at_us=source_observed_at_us,
            max_source_age_us=max_source_age_us,
            assessed_at_us=assessed_at_us,
        )


def _assess_temporal_staleness(
    *,
    assessed_at_us: int,
    valid_to_us: int | None,
    source_observed_at_us: int | None,
    max_source_age_us: int | None,
) -> _TemporalStalenessSignals:
    """Evaluate stale-maintenance signals once for all Knowledge policy surfaces."""

    _require_non_negative_int("assessed_at_us", assessed_at_us)
    if (source_observed_at_us is None) != (max_source_age_us is None):
        raise ValueError(
            "source_observed_at_us and max_source_age_us must be supplied together."
        )
    if source_observed_at_us is not None and max_source_age_us is not None:
        _require_non_negative_int("source_observed_at_us", source_observed_at_us)
        _require_non_negative_int("max_source_age_us", max_source_age_us)
        if source_observed_at_us > assessed_at_us:
            raise ValueError("source_observed_at_us must not be in the future.")

    reasons: list[KnowledgeStalenessReason] = []
    if valid_to_us is not None and valid_to_us < assessed_at_us:
        reasons.append(KnowledgeStalenessReason.VALIDITY_ENDED)
    if source_observed_at_us is not None and max_source_age_us is not None:
        if assessed_at_us - source_observed_at_us > max_source_age_us:
            reasons.append(KnowledgeStalenessReason.SOURCE_AGE_EXCEEDED)

    return _TemporalStalenessSignals(
        reasons=tuple(reasons),
        has_recorded_temporal_evidence=(
            valid_to_us is not None or source_observed_at_us is not None
        ),
    )


def _require_non_negative_int(name: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer.")
    if value < 0:
        raise ValueError(f"{name} must not be negative.")
