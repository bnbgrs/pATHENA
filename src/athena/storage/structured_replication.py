"""Durable monotone state for structured long-term replication."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import cast

from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


class StructuredReplicationError(RuntimeError):
    """Base error for structured replication state transitions."""


class StructuredReplicationInvariantError(StructuredReplicationError):
    """Raised when a transition would fork or rewind confirmed history."""


class ReplicationTargetState(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CONFLICT = "conflict"
    RECOVERING = "recovering"
    PAUSED = "paused"


class ReplicationCommitState(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"


@dataclass(frozen=True, slots=True)
class ReplicationTarget:
    target_id: uuid.UUID
    target_locator: str
    state: ReplicationTargetState
    confirmed_commit_seq: int
    confirmed_head_hash: str | None
    conflict_code: str | None
    created_at_us: int
    updated_at_us: int
    verified_at_us: int | None


@dataclass(frozen=True, slots=True)
class ReplicationCommit:
    target_id: uuid.UUID
    commit_seq: int
    state: ReplicationCommitState
    head_hash: str
    previous_head_hash: str | None
    created_at_us: int
    verified_at_us: int | None


def _timestamp(value: int | None) -> int:
    result = utc_now_us() if value is None else value
    if isinstance(result, bool) or not isinstance(result, int):
        raise TypeError("Structured replication timestamp must be an integer.")
    if result < 0:
        raise ValueError("Structured replication timestamp must not be negative.")
    return result


def _hash(value: str | None, *, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("Structured replication hashes must contain 64 hex characters.")
    normalized = value.lower()
    try:
        bytes.fromhex(normalized)
    except ValueError as exc:
        raise ValueError(
            "Structured replication hashes must contain 64 hex characters."
        ) from exc
    return normalized


class StructuredReplicationRepository:
    """Persist pending work and atomically advance a verified target head."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def register_target(
        self,
        target_locator: str,
        *,
        target_id: uuid.UUID | None = None,
        now_us: int | None = None,
    ) -> ReplicationTarget:
        if not isinstance(target_locator, str) or not target_locator.strip():
            raise ValueError("Structured replication target_locator must not be empty.")
        identifier = new_uuid7() if target_id is None else target_id
        now = _timestamp(now_us)
        with self.database.write_transaction() as connection:
            connection.execute(
                """
                INSERT INTO replication_targets (
                    target_id, target_role, target_locator, state,
                    confirmed_commit_seq, confirmed_head_hash, conflict_code,
                    created_at_us, updated_at_us, verified_at_us
                ) VALUES (?, 'long_term_root', ?, 'pending', 0, NULL, NULL, ?, ?, NULL)
                """,
                (uuid_to_blob(identifier), target_locator.strip(), now, now),
            )
        return self.get_target(identifier)

    def stage_commit(
        self,
        target_id: uuid.UUID,
        *,
        commit_seq: int,
        head_hash: str,
        previous_head_hash: str | None,
        now_us: int | None = None,
    ) -> ReplicationCommit:
        if isinstance(commit_seq, bool) or not isinstance(commit_seq, int) or commit_seq < 1:
            raise ValueError("Structured replication commit_seq must be a positive integer.")
        head = _hash(head_hash)
        previous = _hash(previous_head_hash, optional=True)
        now = _timestamp(now_us)
        with self.database.write_transaction() as connection:
            target = self._target_row(connection, target_id)
            state = ReplicationTargetState(str(target["state"]))
            if state is ReplicationTargetState.CONFLICT:
                raise StructuredReplicationInvariantError(
                    "Conflicted replication target must enter recovery before staging."
                )
            last = connection.execute(
                """
                SELECT commit_seq, head_hash
                FROM replication_commits
                WHERE target_id = ?
                ORDER BY commit_seq DESC LIMIT 1
                """,
                (uuid_to_blob(target_id),),
            ).fetchone()
            confirmed_seq = int(target["confirmed_commit_seq"])
            expected_seq = (int(last["commit_seq"]) + 1) if last is not None else confirmed_seq + 1
            expected_previous = (
                str(last["head_hash"])
                if last is not None
                else (
                    str(target["confirmed_head_hash"])
                    if target["confirmed_head_hash"] is not None
                    else None
                )
            )
            if commit_seq != expected_seq or previous != expected_previous:
                raise StructuredReplicationInvariantError(
                    "Structured replication history must be staged contiguously."
                )
            connection.execute(
                """
                INSERT INTO replication_commits (
                    target_id, commit_seq, state, head_hash,
                    previous_head_hash, created_at_us, verified_at_us
                ) VALUES (?, ?, 'pending', ?, ?, ?, NULL)
                """,
                (uuid_to_blob(target_id), commit_seq, head, previous, now),
            )
            connection.execute(
                "UPDATE replication_targets SET updated_at_us = ? WHERE target_id = ?",
                (now, uuid_to_blob(target_id)),
            )
        return self.get_commit(target_id, commit_seq)

    def confirm_commit(
        self,
        target_id: uuid.UUID,
        *,
        commit_seq: int,
        head_hash: str,
        now_us: int | None = None,
    ) -> ReplicationTarget:
        head = _hash(head_hash)
        now = _timestamp(now_us)
        with self.database.write_transaction() as connection:
            target = self._target_row(connection, target_id)
            expected = int(target["confirmed_commit_seq"]) + 1
            row = connection.execute(
                """
                SELECT state, head_hash FROM replication_commits
                WHERE target_id = ? AND commit_seq = ?
                """,
                (uuid_to_blob(target_id), commit_seq),
            ).fetchone()
            if (
                commit_seq != expected
                or row is None
                or str(row["state"]) != ReplicationCommitState.PENDING.value
                or str(row["head_hash"]) != head
            ):
                raise StructuredReplicationInvariantError(
                    "Structured replication confirmation must advance exactly one pending commit."
                )
            connection.execute(
                """
                UPDATE replication_commits
                SET state = 'verified', verified_at_us = ?
                WHERE target_id = ? AND commit_seq = ? AND state = 'pending'
                """,
                (now, uuid_to_blob(target_id), commit_seq),
            )
            cursor = connection.execute(
                """
                UPDATE replication_targets
                SET state = 'active', confirmed_commit_seq = ?,
                    confirmed_head_hash = ?, conflict_code = NULL,
                    updated_at_us = ?, verified_at_us = ?
                WHERE target_id = ? AND confirmed_commit_seq = ?
                """,
                (commit_seq, head, now, now, uuid_to_blob(target_id), commit_seq - 1),
            )
            if cursor.rowcount != 1:
                raise StructuredReplicationInvariantError(
                    "Structured replication target head changed during confirmation."
                )
        return self.get_target(target_id)

    def mark_conflict(
        self,
        target_id: uuid.UUID,
        *,
        conflict_code: str,
        now_us: int | None = None,
    ) -> ReplicationTarget:
        if not isinstance(conflict_code, str) or not conflict_code.strip():
            raise ValueError("Structured replication conflict_code must not be empty.")
        now = _timestamp(now_us)
        with self.database.write_transaction() as connection:
            self._target_row(connection, target_id)
            connection.execute(
                """
                UPDATE replication_targets
                SET state = 'conflict', conflict_code = ?, updated_at_us = ?
                WHERE target_id = ?
                """,
                (conflict_code.strip()[:200], now, uuid_to_blob(target_id)),
            )
        return self.get_target(target_id)

    def begin_recovery(
        self,
        target_id: uuid.UUID,
        *,
        now_us: int | None = None,
    ) -> ReplicationTarget:
        now = _timestamp(now_us)
        with self.database.write_transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE replication_targets
                SET state = 'recovering', conflict_code = NULL, updated_at_us = ?
                WHERE target_id = ? AND state = 'conflict'
                """,
                (now, uuid_to_blob(target_id)),
            )
            if cursor.rowcount != 1:
                raise StructuredReplicationInvariantError(
                    "Structured replication recovery requires a conflicted target."
                )
        return self.get_target(target_id)

    def get_target(self, target_id: uuid.UUID) -> ReplicationTarget:
        row = self._target_row(self.database.connection, target_id)
        return ReplicationTarget(
            target_id=uuid_from_blob(bytes(row["target_id"])),
            target_locator=str(row["target_locator"]),
            state=ReplicationTargetState(str(row["state"])),
            confirmed_commit_seq=int(row["confirmed_commit_seq"]),
            confirmed_head_hash=(
                str(row["confirmed_head_hash"])
                if row["confirmed_head_hash"] is not None
                else None
            ),
            conflict_code=(
                str(row["conflict_code"]) if row["conflict_code"] is not None else None
            ),
            created_at_us=int(row["created_at_us"]),
            updated_at_us=int(row["updated_at_us"]),
            verified_at_us=(
                int(row["verified_at_us"]) if row["verified_at_us"] is not None else None
            ),
        )

    def get_commit(self, target_id: uuid.UUID, commit_seq: int) -> ReplicationCommit:
        row = self.database.connection.execute(
            """
            SELECT * FROM replication_commits
            WHERE target_id = ? AND commit_seq = ?
            """,
            (uuid_to_blob(target_id), commit_seq),
        ).fetchone()
        if row is None:
            raise LookupError("Structured replication commit does not exist.")
        return ReplicationCommit(
            target_id=uuid_from_blob(bytes(row["target_id"])),
            commit_seq=int(row["commit_seq"]),
            state=ReplicationCommitState(str(row["state"])),
            head_hash=str(row["head_hash"]),
            previous_head_hash=(
                str(row["previous_head_hash"])
                if row["previous_head_hash"] is not None
                else None
            ),
            created_at_us=int(row["created_at_us"]),
            verified_at_us=(
                int(row["verified_at_us"]) if row["verified_at_us"] is not None else None
            ),
        )

    @staticmethod
    def _target_row(connection: sqlite3.Connection, target_id: uuid.UUID) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM replication_targets WHERE target_id = ?",
            (uuid_to_blob(target_id),),
        ).fetchone()
        if row is None:
            raise LookupError("Structured replication target does not exist.")
        return cast(sqlite3.Row, row)
