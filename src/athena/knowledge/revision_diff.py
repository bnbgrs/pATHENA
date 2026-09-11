"""Derived, deterministic diffs between immutable canonical Claim revisions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

from athena.knowledge.models import ClaimRevision


DiffValue: TypeAlias = str | int | None


@dataclass(frozen=True, slots=True)
class ClaimFieldChange:
    """One semantic Claim field changed between two immutable revisions."""

    field: str
    before: DiffValue
    after: DiffValue


@dataclass(frozen=True, slots=True)
class ClaimRevisionDiff:
    """Derived history-view diff; never authoritative persisted state."""

    claim_id: uuid.UUID
    from_revision_id: uuid.UUID
    to_revision_id: uuid.UUID
    changes: tuple[ClaimFieldChange, ...]


_FIELDS = (
    "claim_kind",
    "statement",
    "epistemic_status",
    "subject_entity_id",
    "predicate",
    "object_entity_id",
    "attributed_to_entity_id",
    "valid_from_us",
    "valid_to_us",
)


def diff_claim_revisions(
    before: ClaimRevision,
    after: ClaimRevision,
) -> ClaimRevisionDiff:
    """Return a stable semantic diff for two forward revisions of one Claim.

    Metadata such as actor, provenance and timestamps is intentionally excluded:
    the history surface presents those independently.  This function compares
    only canonical Claim payload fields and does not write or infer state.
    """
    if not isinstance(before, ClaimRevision) or not isinstance(after, ClaimRevision):
        raise TypeError("before and after must be ClaimRevision instances.")
    if before.claim_id != after.claim_id:
        raise ValueError("Claim revisions belong to different Claims.")
    if after.revision_no <= before.revision_no:
        raise ValueError("after must be a later Claim revision than before.")

    changes = tuple(
        ClaimFieldChange(
            field=field,
            before=_diff_value(getattr(before.payload, field)),
            after=_diff_value(getattr(after.payload, field)),
        )
        for field in _FIELDS
        if getattr(before.payload, field) != getattr(after.payload, field)
    )
    return ClaimRevisionDiff(
        claim_id=before.claim_id,
        from_revision_id=before.revision_id,
        to_revision_id=after.revision_id,
        changes=changes,
    )


def _diff_value(value: object) -> DiffValue:
    if value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Enum):
        enum_value = value.value
        if isinstance(enum_value, str):
            return enum_value
    raise TypeError(f"Unsupported Claim diff value: {type(value).__name__}.")
