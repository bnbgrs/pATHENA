"""Human-control policy for revising explicit user Knowledge corrections."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.knowledge.models import KnowledgeUnitRevision


class UserCorrectionState(str, Enum):
    """How a proposed revision relates to an explicit user correction."""

    NOT_USER_CORRECTION = "not_user_correction"
    PRESERVE_USER_CORRECTION = "preserve_user_correction"
    NEW_EVIDENCE_REVIEW_REQUIRED = "new_evidence_review_required"
    EXPLICIT_USER_REVISION = "explicit_user_revision"


@dataclass(frozen=True, slots=True)
class UserCorrectionAssessment:
    """Explain whether an existing user correction may be replaced automatically."""

    state: UserCorrectionState
    current_revision_id: uuid.UUID
    current_created_at_us: int
    newest_evidence_at_us: int | None

    @property
    def permits_automatic_replacement(self) -> bool:
        """Return whether this policy permits an automatic replacement directly."""

        return self.state is UserCorrectionState.NOT_USER_CORRECTION

    @property
    def requires_human_review(self) -> bool:
        """Return whether newer evidence must be reconciled with the user correction."""

        return self.state is UserCorrectionState.NEW_EVIDENCE_REVIEW_REQUIRED

    @property
    def permits_explicit_user_revision(self) -> bool:
        """Return whether the proposed change is itself an explicit user decision."""

        return self.state is UserCorrectionState.EXPLICIT_USER_REVISION


class UserCorrectionPolicy:
    """Preserve explicit user corrections without turning them into eternal locks.

    Beta 07 requires later automation to treat a user correction as strong existing
    evidence, while still allowing a later user decision or genuinely newer evidence
    to produce another revision. This policy therefore never silently overwrites a
    user correction. Newer evidence opens a human-review path instead; stale or absent
    evidence keeps the correction in place. No source, evidence, provenance, or truth
    status is synthesized here.
    """

    @staticmethod
    def assess(
        current: KnowledgeUnitRevision,
        *,
        user_actor_id: uuid.UUID,
        incoming_actor_id: uuid.UUID,
        newest_evidence_at_us: int | None = None,
    ) -> UserCorrectionAssessment:
        if not isinstance(current, KnowledgeUnitRevision):
            raise TypeError("User-correction assessment requires a KnowledgeUnitRevision.")
        if not isinstance(user_actor_id, uuid.UUID):
            raise TypeError("user_actor_id must be a UUID.")
        if not isinstance(incoming_actor_id, uuid.UUID):
            raise TypeError("incoming_actor_id must be a UUID.")
        if newest_evidence_at_us is not None:
            if isinstance(newest_evidence_at_us, bool) or not isinstance(
                newest_evidence_at_us, int
            ):
                raise TypeError("newest_evidence_at_us must be an integer or None.")
            if newest_evidence_at_us < 0:
                raise ValueError("newest_evidence_at_us must not be negative.")

        if current.created_by_actor_id != user_actor_id:
            state = UserCorrectionState.NOT_USER_CORRECTION
        elif incoming_actor_id == user_actor_id:
            state = UserCorrectionState.EXPLICIT_USER_REVISION
        elif (
            newest_evidence_at_us is not None
            and newest_evidence_at_us > current.created_at_us
        ):
            state = UserCorrectionState.NEW_EVIDENCE_REVIEW_REQUIRED
        else:
            state = UserCorrectionState.PRESERVE_USER_CORRECTION

        return UserCorrectionAssessment(
            state=state,
            current_revision_id=current.revision_id,
            current_created_at_us=current.created_at_us,
            newest_evidence_at_us=newest_evidence_at_us,
        )
