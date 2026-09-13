"""Human-control policy for automatic revisions after explicit user correction."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from athena.knowledge.models import EvidenceRole


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


@dataclass(frozen=True, slots=True)
class UserCorrectionConflictAssessment:
    """Visible external conflict retained alongside an explicit user correction."""

    contradicting_evidence_revision_ids: frozenset[uuid.UUID]

    @property
    def conflict_visible(self) -> bool:
        """A contradiction remains visible while contrary evidence exists."""

        return bool(self.contradicting_evidence_revision_ids)

    @property
    def source_deletion_allowed(self) -> bool:
        """Conflict handling never authorizes deletion of contrary source evidence."""

        return False


class UserOverridePolicy:
    """Protect explicit user corrections from evidence-free model reversal.

    Beta chapter 05 requires that later automatic extraction cannot silently undo
    an explicit user correction without new evidence. Beta chapter 07 additionally
    requires external evidence that still contradicts the correction to remain
    visible instead of being deleted. This policy is deliberately conservative:
    identical or older evidence is blocked, genuinely unseen evidence can only open
    a semantic-review path, and contradictory evidence remains an explicit conflict.
    It never authorizes a direct canonical write or source deletion.
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

    @staticmethod
    def assess_source_conflict(
        override: UserOverrideSnapshot,
        *,
        evidence: Iterable[tuple[uuid.UUID, EvidenceRole]],
    ) -> UserCorrectionConflictAssessment:
        """Retain contradictory evidence as a visible conflict without deletion.

        The caller supplies stable evidence-revision identities and their canonical
        semantic roles. This boundary classifies only explicit ``contradicts`` links;
        supports, mentions, contextualization, and origin links are not promoted into
        conflicts. Malformed runtime values fail closed before any caller can act on
        the assessment.
        """

        if not isinstance(override, UserOverrideSnapshot):
            raise TypeError("override must be a UserOverrideSnapshot.")

        contradictions: set[uuid.UUID] = set()
        for item in evidence:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError("evidence entries must be (revision_id, EvidenceRole) tuples.")
            revision_id, role = item
            if not isinstance(revision_id, uuid.UUID):
                raise TypeError("evidence revision_id must be a UUID.")
            if not isinstance(role, EvidenceRole):
                raise TypeError("evidence role must be an EvidenceRole.")
            if role is EvidenceRole.CONTRADICTS:
                contradictions.add(revision_id)

        return UserCorrectionConflictAssessment(
            contradicting_evidence_revision_ids=frozenset(contradictions),
        )
