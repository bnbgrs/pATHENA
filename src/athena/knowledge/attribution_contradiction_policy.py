"""Deterministic attribution policy for Claim contradiction candidates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from athena.knowledge.models import ClaimDraft, ClaimKind


class AttributionContradictionState(str, Enum):
    """Whether attribution alone rules out an objective contradiction candidate."""

    NOT_DISJOINT = "not_disjoint"
    DISTINCT_ATTRIBUTED_OPINIONS = "distinct_attributed_opinions"


@dataclass(frozen=True, slots=True)
class AttributionContradictionAssessment:
    """Explain the attribution gate applied before contradiction marking."""

    state: AttributionContradictionState
    left_attributed_to_entity_id: object | None
    right_attributed_to_entity_id: object | None

    @property
    def permits_contradiction_candidate(self) -> bool:
        """Return whether attribution does not rule out a contradiction."""

        return self.state is AttributionContradictionState.NOT_DISJOINT


class AttributionContradictionPolicy:
    """Apply Beta attribution semantics without model inference.

    Two explicit attributed opinions from different identified sources describe
    different speakers' positions and therefore must not be promoted automatically
    into an objective contradiction candidate. Same-speaker opinions, factual claims,
    mixed kinds, and missing attribution remain eligible for separate semantic review.
    """

    @staticmethod
    def assess(
        left: ClaimDraft,
        right: ClaimDraft,
    ) -> AttributionContradictionAssessment:
        if not isinstance(left, ClaimDraft) or not isinstance(right, ClaimDraft):
            raise TypeError("Attribution contradiction assessment requires ClaimDraft values.")

        distinct_attributed_opinions = (
            left.claim_kind is ClaimKind.ATTRIBUTED_OPINION
            and right.claim_kind is ClaimKind.ATTRIBUTED_OPINION
            and left.attributed_to_entity_id is not None
            and right.attributed_to_entity_id is not None
            and left.attributed_to_entity_id != right.attributed_to_entity_id
        )
        state = (
            AttributionContradictionState.DISTINCT_ATTRIBUTED_OPINIONS
            if distinct_attributed_opinions
            else AttributionContradictionState.NOT_DISJOINT
        )
        return AttributionContradictionAssessment(
            state=state,
            left_attributed_to_entity_id=left.attributed_to_entity_id,
            right_attributed_to_entity_id=right.attributed_to_entity_id,
        )
