"""Canonical temporal gate for contradiction-review candidates."""

from __future__ import annotations

import sqlite3
import uuid

from athena.common.ids import uuid_to_blob
from athena.knowledge.contradiction_policy import (
    TemporalContradictionAssessment,
    TemporalContradictionPolicy,
)
from athena.knowledge.models import ClaimDraft, ClaimKind, EpistemicStatus


class ContradictionReviewGateError(LookupError):
    """Raised when an exact Claim revision cannot be assessed safely."""


def assess_canonical_claim_revisions(
    connection: sqlite3.Connection,
    *,
    left_revision_id: uuid.UUID,
    right_revision_id: uuid.UUID,
) -> TemporalContradictionAssessment:
    """Assess exact persisted Claim revisions before contradiction review enqueue.

    The lookup is revision-bound rather than head-bound so the caller can assess the
    same canonical revisions it is about to place into the durable review item.
    Missing or non-Claim revisions fail closed instead of inventing temporal data.
    """

    left = _load_claim_draft(connection, revision_id=left_revision_id)
    right = _load_claim_draft(connection, revision_id=right_revision_id)
    return TemporalContradictionPolicy.assess(left, right)


def _load_claim_draft(
    connection: sqlite3.Connection,
    *,
    revision_id: uuid.UUID,
) -> ClaimDraft:
    if not isinstance(revision_id, uuid.UUID):
        raise TypeError("revision_id must be a UUID.")

    row = connection.execute(
        """
        SELECT
            cr.claim_kind,
            cr.statement,
            cr.subject_entity_id,
            cr.predicate,
            cr.object_entity_id,
            cr.attributed_to_entity_id,
            cr.valid_from_us,
            cr.valid_to_us,
            cr.epistemic_status
        FROM claim_revisions AS cr
        JOIN revisions AS r ON r.revision_id = cr.revision_id
        JOIN claims AS c ON c.claim_id = r.entity_id
        WHERE cr.revision_id = ?
        """,
        (uuid_to_blob(revision_id),),
    ).fetchone()
    if row is None:
        raise ContradictionReviewGateError(
            f"Canonical Claim revision not found: {revision_id}"
        )

    def optional_uuid(value: object) -> uuid.UUID | None:
        if value is None:
            return None
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise ContradictionReviewGateError("Invalid UUID BLOB in Claim revision.")
        return uuid.UUID(bytes=bytes(value))

    return ClaimDraft(
        claim_kind=ClaimKind(str(row["claim_kind"])),
        statement=str(row["statement"]),
        epistemic_status=EpistemicStatus(str(row["epistemic_status"])),
        subject_entity_id=optional_uuid(row["subject_entity_id"]),
        predicate=None if row["predicate"] is None else str(row["predicate"]),
        object_entity_id=optional_uuid(row["object_entity_id"]),
        attributed_to_entity_id=optional_uuid(row["attributed_to_entity_id"]),
        valid_from_us=(
            None if row["valid_from_us"] is None else int(row["valid_from_us"])
        ),
        valid_to_us=None if row["valid_to_us"] is None else int(row["valid_to_us"]),
    )
