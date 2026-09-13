"""Fail-closed semantic identity policy for same_as and different_from relations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IdentityRelationDecision(str, Enum):
    """Permitted next step for a proposed semantic identity relation."""

    ALLOW_SAME_AS = "allow_same_as"
    KEEP_DISTINCT = "keep_distinct"
    REQUIRE_REVIEW = "require_review"


@dataclass(frozen=True, slots=True)
class IdentityRelationAssessment:
    """Explain why Core may or may not materialize a semantic identity relation."""

    decision: IdentityRelationDecision
    reason: str

    @property
    def permits_same_as(self) -> bool:
        """Return whether evidence is sufficient to create a same_as relation."""

        return self.decision is IdentityRelationDecision.ALLOW_SAME_AS


class IdentityRelationPolicy:
    """Apply Beta identity safeguards without inferring semantic facts.

    String similarity may nominate a review candidate, but it never proves
    semantic identity. An explicit different_from decision is strong evidence
    against same_as. Conflicting explicit identity signals require human/model
    review rather than an automatic overwrite.
    """

    @staticmethod
    def assess(
        *,
        semantic_identity_confirmed: bool,
        different_from_confirmed: bool,
        string_similarity_only: bool,
    ) -> IdentityRelationAssessment:
        for label, value in (
            ("semantic_identity_confirmed", semantic_identity_confirmed),
            ("different_from_confirmed", different_from_confirmed),
            ("string_similarity_only", string_similarity_only),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{label} must be a bool.")

        if semantic_identity_confirmed and different_from_confirmed:
            return IdentityRelationAssessment(
                decision=IdentityRelationDecision.REQUIRE_REVIEW,
                reason="conflicting_explicit_identity_evidence",
            )

        if different_from_confirmed:
            return IdentityRelationAssessment(
                decision=IdentityRelationDecision.KEEP_DISTINCT,
                reason="explicit_different_from",
            )

        if semantic_identity_confirmed:
            return IdentityRelationAssessment(
                decision=IdentityRelationDecision.ALLOW_SAME_AS,
                reason="semantic_identity_confirmed",
            )

        if string_similarity_only:
            return IdentityRelationAssessment(
                decision=IdentityRelationDecision.REQUIRE_REVIEW,
                reason="string_similarity_is_not_identity_evidence",
            )

        return IdentityRelationAssessment(
            decision=IdentityRelationDecision.REQUIRE_REVIEW,
            reason="insufficient_identity_evidence",
        )
