from __future__ import annotations

import sqlite3
import uuid

import pytest

from athena.common.ids import uuid_to_blob
from athena.knowledge.contradiction_policy import TemporalContradictionState
from athena.knowledge.contradiction_review_gate import (
    ContradictionReviewGateError,
    assess_canonical_claim_revisions,
)


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE claims (
            claim_id BLOB PRIMARY KEY
        );
        CREATE TABLE revisions (
            revision_id BLOB PRIMARY KEY,
            entity_id BLOB NOT NULL
        );
        CREATE TABLE claim_revisions (
            revision_id BLOB PRIMARY KEY,
            claim_kind TEXT NOT NULL,
            statement TEXT NOT NULL,
            subject_entity_id BLOB,
            predicate TEXT,
            object_entity_id BLOB,
            attributed_to_entity_id BLOB,
            valid_from_us INTEGER,
            valid_to_us INTEGER,
            epistemic_status TEXT NOT NULL
        );
        """
    )
    return connection


def _insert_claim_revision(
    connection: sqlite3.Connection,
    *,
    valid_from_us: int | None,
    valid_to_us: int | None,
) -> uuid.UUID:
    claim_id = uuid.uuid4()
    revision_id = uuid.uuid4()
    connection.execute(
        "INSERT INTO claims (claim_id) VALUES (?)",
        (uuid_to_blob(claim_id),),
    )
    connection.execute(
        "INSERT INTO revisions (revision_id, entity_id) VALUES (?, ?)",
        (uuid_to_blob(revision_id), uuid_to_blob(claim_id)),
    )
    connection.execute(
        """
        INSERT INTO claim_revisions (
            revision_id, claim_kind, statement,
            subject_entity_id, predicate, object_entity_id,
            attributed_to_entity_id, valid_from_us, valid_to_us,
            epistemic_status
        ) VALUES (?, 'factual_assertion', 'A works somewhere', NULL, NULL, NULL, NULL, ?, ?, 'asserted')
        """,
        (uuid_to_blob(revision_id), valid_from_us, valid_to_us),
    )
    return revision_id


def test_disjoint_canonical_revisions_suppress_contradiction_candidate() -> None:
    connection = _connection()
    left_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=1_000,
        valid_to_us=2_000,
    )
    right_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=3_000,
        valid_to_us=4_000,
    )

    assessment = assess_canonical_claim_revisions(
        connection,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert assessment.state is TemporalContradictionState.DISJOINT
    assert assessment.permits_contradiction_candidate is False


def test_touching_canonical_revisions_remain_review_candidates() -> None:
    connection = _connection()
    left_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=1_000,
        valid_to_us=2_000,
    )
    right_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=2_000,
        valid_to_us=3_000,
    )

    assessment = assess_canonical_claim_revisions(
        connection,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert assessment.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
    assert assessment.permits_contradiction_candidate is True


def test_unknown_temporal_bounds_remain_review_candidates() -> None:
    connection = _connection()
    left_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=None,
        valid_to_us=None,
    )
    right_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=3_000,
        valid_to_us=4_000,
    )

    assessment = assess_canonical_claim_revisions(
        connection,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
    )

    assert assessment.state is TemporalContradictionState.OVERLAPPING_OR_UNKNOWN
    assert assessment.permits_contradiction_candidate is True


def test_missing_canonical_revision_fails_closed() -> None:
    connection = _connection()
    existing_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=1_000,
        valid_to_us=2_000,
    )

    with pytest.raises(ContradictionReviewGateError, match="Canonical Claim revision not found"):
        assess_canonical_claim_revisions(
            connection,
            left_revision_id=existing_revision_id,
            right_revision_id=uuid.uuid4(),
        )


def test_non_uuid_revision_id_is_rejected() -> None:
    connection = _connection()
    existing_revision_id = _insert_claim_revision(
        connection,
        valid_from_us=1_000,
        valid_to_us=2_000,
    )

    with pytest.raises(TypeError, match="revision_id must be a UUID"):
        assess_canonical_claim_revisions(
            connection,
            left_revision_id=existing_revision_id,
            right_revision_id="not-a-uuid",  # type: ignore[arg-type]
        )
