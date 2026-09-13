"""Deterministic staleness signaling for canonical Knowledge revisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.knowledge.models import KnowledgeUnitRevision


class KnowledgeStalenessState(str, Enum):
    """What recorded temporal validity can truthfully say about staleness."""

    STALE_BY_VALIDITY = "stale_by_validity"
    NOT_STALE_BY_VALIDITY = "not_stale_by_validity"
    INSUFFICIENT_TEMPORAL_EVIDENCE = "insufficient_temporal_evidence"


@dataclass(frozen=True, slots=True)
class KnowledgeStalenessAssessment:
    """Explain a staleness signal without turning it into a truth verdict."""

    state: KnowledgeStalenessState
    knowledge_id: str
    revision_id: str
    valid_from_us: int | None
    valid_to_us: int | None
    assessed_at_us: int

    @property
    def should_signal_stale(self) -> bool:
        """Return whether recorded validity alone justifies a stale signal."""

        return self.state is KnowledgeStalenessState.STALE_BY_VALIDITY


class KnowledgeStalenessPolicy:
    """Apply Beta stale-Knowledge semantics using only persisted validity.

    The policy never infers source age, falsity, or a replacement revision. A
    missing ``valid_to_us`` therefore remains insufficient temporal evidence
    rather than being reported as current forever.
    """

    @staticmethod
    def assess(
        revision: KnowledgeUnitRevision,
        *,
        assessed_at_us: int,
    ) -> KnowledgeStalenessAssessment:
        if not isinstance(revision, KnowledgeUnitRevision):
            raise TypeError("Staleness assessment requires a KnowledgeUnitRevision.")
        if isinstance(assessed_at_us, bool) or not isinstance(assessed_at_us, int):
            raise TypeError("assessed_at_us must be an integer.")
        if assessed_at_us < 0:
            raise ValueError("assessed_at_us must not be negative.")

        valid_to_us = revision.payload.valid_to_us
        if valid_to_us is None:
            state = KnowledgeStalenessState.INSUFFICIENT_TEMPORAL_EVIDENCE
        elif valid_to_us < assessed_at_us:
            state = KnowledgeStalenessState.STALE_BY_VALIDITY
        else:
            state = KnowledgeStalenessState.NOT_STALE_BY_VALIDITY

        return KnowledgeStalenessAssessment(
            state=state,
            knowledge_id=str(revision.knowledge_id),
            revision_id=str(revision.revision_id),
            valid_from_us=revision.payload.valid_from_us,
            valid_to_us=valid_to_us,
            assessed_at_us=assessed_at_us,
        )
