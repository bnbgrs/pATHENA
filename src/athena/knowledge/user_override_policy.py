"""Human-control policy for automatic revisions after explicit user correction."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AutomaticRevisionDecision(str, Enum):
    """Decision for model-driven revision of user-corrected canonical knowledge."""

    BLOCK_NO_NEW_EVIDENCE = "block_no_new_evidence"
    REQUIRE_REVIEW_NEW_EVIDENCE = "require_review_new_evidence"


@dataclass(frozen=True, slots=True)
class UserOverrideSnapshot:
    """Evidence boundary established by one explicit user correction.

    Evidence identifiers are stable revision-level references, such as source-anchor
    revisions or chat-message revisions. The snapshot never treats repeated access
    to the same evidence as new evidence.
    """

    entity_id: uuid.UUID
    correction_revision_id: uuid.UUID
    evidence_revision_ids: frozenset[uuid.UUID]

    @classmethod
    def create(
        cls,
        *,
        entity_id: uuid.UUID,
        correction_revision_id: uuid.UUID,
        evidence_revision_ids: Iterable[uuid.UUID] = (),
    ) -> "UserOverrideSnapshot":
        if not isinstance(entity_id, uuid.UUID):
            raise TypeError("entity_id must be a UUID.")
        if not isinstance(correction_revision_id, uuid.UUID):
            raise TypeError("correction_revision_id must be a UUID.")

        evidence = frozenset(evidence_revision_ids)
        if any(not isinstance(item, uuid.UUID) for item in evidence):
            raise TypeError("evidence_revision_ids must contain only UUID values.")

        return cls(
            entity_id=entity_id,
            correction_revision_id=correction_revision_id,
            evidence_revision_ids=evidence,
        )


@dataclass(frozen=True, slots=True)
class UserOverrideAssessment:
    """Explain why an automatic revision is blocked or routed to review."""

    decision: AutomaticRevisionDecision
    new_evidence_revision_ids: frozenset[uuid.UUID]

    @property
    def automatic_commit_allowed(self) -> bool:
        """User-corrected knowledge is never silently rewritten by this policy."""

        return False

    @property
    def requires_semantic_review(self) -> bool:
        """New evidence permits reconsideration, but only through explicit review."""

        return self.decision is AutomaticRevisionDecision.REQUIRE_REVIEW_NEW_EVIDENCE


class UserOverridePolicy:
    """Protect explicit user corrections from evidence-free model reversal.

    Beta chapter 05 requires that later automatic extraction cannot silently undo
    an explicit user correction without new evidence. This policy is deliberately
    conservative: identical or older evidence is blocked, while genuinely unseen
    evidence can only open a semantic-review path. It never authorizes a direct
    canonical write.
    """

    @staticmethod
    def assess_automatic_revision(
        override: UserOverrideSnapshot,
        *,
        incoming_evidence_revision_ids: Iterable[uuid.UUID],
    ) -> UserOverrideAssessment:
        if not isinstance(override, UserOverrideSnapshot):
            raise TypeError("override must be a UserOverrideSnapshot.")

        incoming = frozenset(incoming_evidence_revision_ids)
        if any(not isinstance(item, uuid.UUID) for item in incoming):
            raise TypeError(
                "incoming_evidence_revision_ids must contain only UUID values."
            )

        new_evidence = incoming.difference(override.evidence_revision_ids)
        decision = (
            AutomaticRevisionDecision.REQUIRE_REVIEW_NEW_EVIDENCE
            if new_evidence
            else AutomaticRevisionDecision.BLOCK_NO_NEW_EVIDENCE
        )
        return UserOverrideAssessment(
            decision=decision,
            new_evidence_revision_ids=new_evidence,
        )
