"""Deterministic temporal policy for Claim contradiction candidates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.knowledge.models import ClaimDraft


class TemporalContradictionState(str, Enum):
    """Whether two Claim validity windows can describe the same time."""

    OVERLAPPING_OR_UNKNOWN = "overlapping_or_unknown"
    DISJOINT = "disjoint"


@dataclass(frozen=True, slots=True)
class TemporalContradictionAssessment:
    """Explain the temporal gate applied before contradiction marking."""

    state: TemporalContradictionState
    left_valid_from_us: int | None
    left_valid_to_us: int | None
    right_valid_from_us: int | None
    right_valid_to_us: int | None

    @property
    def permits_contradiction_candidate(self) -> bool:
        """Return whether temporal data does not rule out a contradiction."""

        return self.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN


class TemporalContradictionPolicy:
    """Apply Beta temporal non-contradiction semantics without model inference.

    Missing bounds are treated as unknown/open rather than evidence of separation.
    Only provably disjoint closed/open-ended windows suppress a contradiction
    candidate. Semantic contradiction detection remains a separate concern.
    """

    @staticmethod
    def assess(
        left: ClaimDraft,
        right: ClaimDraft,
    ) -> TemporalContradictionAssessment:
        if not isinstance(left, ClaimDraft) or not isinstance(right, ClaimDraft):
            raise TypeError("Temporal contradiction assessment requires ClaimDraft values.")

        disjoint = (
            left.valid_to_us is not None
            and right.valid_from_us is not None
            and left.valid_to_us < right.valid_from_us
        ) or (
            right.valid_to_us is not None
            and left.valid_from_us is not None
            and right.valid_to_us < left.valid_from_us
        )
        state = (
            TemporalContradictionState.DISJOINT
            if disjoint
            else TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
        )
        return TemporalContradictionAssessment(
            state=state,
            left_valid_from_us=left.valid_from_us,
            left_valid_to_us=left.valid_to_us,
            right_valid_from_us=right.valid_from_us,
            right_valid_to_us=right.valid_to_us,
        )
