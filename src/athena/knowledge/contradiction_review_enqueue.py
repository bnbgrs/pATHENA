"""Canonical composition boundary for contradiction-review persistence."""

from __future__ import annotations

import sqlite3
import uuid

from athena.knowledge.contradiction_review_gate import (
    assess_canonical_contradiction_candidate,
)
from athena.knowledge.review_service import ReviewService


def enqueue_canonical_contradiction_review(
    connection: sqlite3.Connection,
    *,
    processing_run_id: uuid.UUID,
    model_signature_id: uuid.UUID,
    left_entity_id: uuid.UUID,
    left_revision_id: uuid.UUID,
    right_entity_id: uuid.UUID,
    right_revision_id: uuid.UUID,
    confidence: float,
    reason: str,
    created_at_us: int,
) -> uuid.UUID | None:
    """Persist a contradiction review only when canonical deterministic gates permit it.

    The assessment is bound to the exact immutable Claim revision identifiers that
    are then handed to the existing persistent review queue.  A deterministic
    temporal or attribution rejection produces no review row.  Missing revisions
    continue to fail closed through ``assess_canonical_contradiction_candidate``.
    """

    assessment = assess_canonical_contradiction_candidate(
        connection,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )
    if not assessment.permits_contradiction_candidate:
        return None

    return ReviewService.enqueue_contradiction(
        connection,
        processing_run_id=processing_run_id,
        model_signature_id=model_signature_id,
        left_entity_id=left_entity_id,
        left_revision_id=left_revision_id,
        right_entity_id=right_entity_id,
        right_revision_id=right_revision_id,
        confidence=confidence,
        reason=reason,
        created_at_us=created_at_us,
    )
