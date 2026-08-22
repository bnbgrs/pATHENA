"""Canonical snapshot invariants for durable Grounded provider execution."""

from __future__ import annotations

import sqlite3
import uuid

from athena.common.ids import uuid_to_blob
from athena.retrieval.context_package import ContextPackage, ContextPackageError
from athena.storage.database import SQLiteDatabase


class GroundedSnapshotBindingError(RuntimeError):
    """A Grounded ContextPackage is detached from its canonical snapshot."""


def _user_commit_seq(
    connection: sqlite3.Connection,
    *,
    package: ContextPackage,
    operation_id: uuid.UUID,
) -> int:
    try:
        current_ref = package.current_user_ref()
    except ContextPackageError as exc:
        raise GroundedSnapshotBindingError(
            "Grounded ContextPackage has no unique CURRENT-USER snapshot anchor."
        ) from exc
    if (
        current_ref.entity_type != "chat_message"
        or current_ref.entity_id != operation_id
        or current_ref.revision_id is None
    ):
        raise GroundedSnapshotBindingError(
            "Grounded ContextPackage CURRENT-USER snapshot anchor is invalid."
        )
    row = connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.entity_id = ? AND r.revision_id = ?
        """,
        (
            uuid_to_blob(operation_id),
            uuid_to_blob(current_ref.revision_id),
        ),
    ).fetchone()
    if row is None:
        raise GroundedSnapshotBindingError(
            "Grounded CURRENT-USER revision has no canonical commit sequence."
        )
    return int(row["commit_seq"])


def validate_grounded_snapshot_identity(
    database: SQLiteDatabase,
    *,
    package: ContextPackage,
    operation_id: uuid.UUID,
) -> None:
    """Bind the package snapshot sequence to its durable CURRENT-USER commit."""
    user_commit_seq = _user_commit_seq(
        database.connection,
        package=package,
        operation_id=operation_id,
    )
    if package.snapshot_commit_seq != user_commit_seq:
        raise GroundedSnapshotBindingError(
            "Grounded ContextPackage snapshot sequence conflicts with CURRENT-USER commit."
        )


def validate_grounded_snapshot_current(
    database: SQLiteDatabase,
    *,
    package: ContextPackage,
    operation_id: uuid.UUID,
) -> None:
    """Require the pinned canonical snapshot to remain current before provider I/O."""
    validate_grounded_snapshot_identity(
        database,
        package=package,
        operation_id=operation_id,
    )
    row = database.connection.execute(
        "SELECT COALESCE(MAX(commit_seq), 0) AS commit_seq FROM commit_records"
    ).fetchone()
    current_commit_seq = 0 if row is None else int(row["commit_seq"])
    if current_commit_seq != package.snapshot_commit_seq:
        raise GroundedSnapshotBindingError(
            "Canonical state changed after the Grounded ContextPackage snapshot was pinned."
        )
