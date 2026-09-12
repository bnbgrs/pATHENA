"""Human-control guard for automatic updates after explicit user corrections."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import StrEnum


class AutomaticUpdateDisposition(StrEnum):
    """Allowed next step for an automatic update that meets a user override."""

    REJECT_NO_NEW_EVIDENCE = "reject_no_new_evidence"
    REQUIRE_REVIEW_NEW_EVIDENCE = "require_review_new_evidence"


@dataclass(frozen=True, slots=True)
class UserOverrideAssessment:
    """Fail-closed assessment for one proposed automatic Knowledge update."""

    user_revision_id: uuid.UUID
    disposition: AutomaticUpdateDisposition
    new_evidence_revision_ids: tuple[uuid.UUID, ...]


def _revision_ids(
    value: object,
    *,
    field_name: str,
) -> tuple[uuid.UUID, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple of UUID revision ids.")
    if any(not isinstance(item, uuid.UUID) for item in value):
        raise TypeError(f"{field_name} must contain only UUID revision ids.")
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must not contain duplicate revision ids.")
    return value


def assess_automatic_update_after_user_override(
    *,
    user_revision_id: uuid.UUID,
    prior_evidence_revision_ids: tuple[uuid.UUID, ...],
    proposed_evidence_revision_ids: tuple[uuid.UUID, ...],
) -> UserOverrideAssessment:
    """Protect an explicit user correction from evidence-stale automation.

    The function does not authorize a canonical write. A proposal that carries no
    evidence revision that was absent when the user correction was made is rejected.
    If genuinely new evidence is present, the proposal is surfaced for explicit
    semantic review instead of silently reversing the user's canonical revision.
    """
    if not isinstance(user_revision_id, uuid.UUID):
        raise TypeError("user_revision_id must be a UUID revision id.")

    prior = _revision_ids(
        prior_evidence_revision_ids,
        field_name="prior_evidence_revision_ids",
    )
    proposed = _revision_ids(
        proposed_evidence_revision_ids,
        field_name="proposed_evidence_revision_ids",
    )
    prior_set = set(prior)
    new_evidence = tuple(item for item in proposed if item not in prior_set)

    if not new_evidence:
        return UserOverrideAssessment(
            user_revision_id=user_revision_id,
            disposition=AutomaticUpdateDisposition.REJECT_NO_NEW_EVIDENCE,
            new_evidence_revision_ids=(),
        )

    return UserOverrideAssessment(
        user_revision_id=user_revision_id,
        disposition=AutomaticUpdateDisposition.REQUIRE_REVIEW_NEW_EVIDENCE,
        new_evidence_revision_ids=new_evidence,
    )
