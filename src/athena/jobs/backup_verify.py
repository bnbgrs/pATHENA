"""Deterministic planning primitives for periodic durable Deep backup verification."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from typing import Protocol

from athena.common.ids import uuid_from_blob
from athena.common.time import utc_now_us

_DEFAULT_INTERVAL_SECONDS = 7 * 24 * 60 * 60
_SECOND_US = 1_000_000


class BackupVerificationPlanningError(RuntimeError):
    """Raised when periodic Deep verification cannot be planned safely."""


class _DatabaseLike(Protocol):
    connection: sqlite3.Connection


class _BackupLike(Protocol):
    database: _DatabaseLike


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyCandidate:
    """One active completed restore point due for periodic Deep verification."""

    snapshot_id: uuid.UUID
    target_id: uuid.UUID
    completed_at_us: int
    last_verified_at_us: int | None
    occurrence_slot_us: int

    @property
    def idempotency_key(self) -> str:
        return (
            "backup.verify_deep:"
            f"{self.snapshot_id}:"
            f"{self.occurrence_slot_us}"
        )


def _positive_seconds(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be an integer >= 1.")
    return value


def _nonnegative_timestamp(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def deep_verify_occurrence_slot_us(
    now_us: int,
    *,
    interval_seconds: int = _DEFAULT_INTERVAL_SECONDS,
) -> int:
    """Return the deterministic UTC occurrence slot for periodic Deep verify."""
    now = _nonnegative_timestamp(now_us, label="now_us")
    interval = _positive_seconds(
        interval_seconds,
        label="interval_seconds",
    )
    interval_us = interval * _SECOND_US
    return (now // interval_us) * interval_us


def select_deep_verify_candidate(
    backup: _BackupLike,
    *,
    now_us: int | None = None,
    interval_seconds: int = _DEFAULT_INTERVAL_SECONDS,
) -> BackupDeepVerifyCandidate | None:
    """Select the oldest active restore point whose Deep verification is due.

    Failed or pruned snapshots are deliberately excluded. Environment/busy
    failures leave the prior verification state intact, so they remain safely
    retryable by a later durable orchestration layer without creating another
    backup snapshot.
    """
    now = (
        utc_now_us()
        if now_us is None
        else _nonnegative_timestamp(now_us, label="now_us")
    )
    interval = _positive_seconds(
        interval_seconds,
        label="interval_seconds",
    )
    interval_us = interval * _SECOND_US
    cutoff_us = max(0, now - interval_us)
    occurrence_slot_us = deep_verify_occurrence_slot_us(
        now,
        interval_seconds=interval,
    )

    row = backup.database.connection.execute(
        """
        SELECT
            snapshot.snapshot_id,
            snapshot.target_id,
            snapshot.completed_at_us,
            snapshot.last_verified_at_us
        FROM backup_snapshots AS snapshot
        JOIN backup_targets AS target
          ON target.target_id = snapshot.target_id
        WHERE snapshot.state = 'complete'
          AND snapshot.pruned_at_us IS NULL
          AND snapshot.verification_status IN (
              'verified_light',
              'verified_deep'
          )
          AND snapshot.completed_at_us IS NOT NULL
          AND target.status = 'active'
          AND (
              snapshot.last_verified_at_us IS NULL
              OR snapshot.last_verified_at_us <= ?
          )
        ORDER BY
            COALESCE(snapshot.last_verified_at_us, 0),
            snapshot.completed_at_us,
            snapshot.snapshot_id
        LIMIT 1
        """,
        (cutoff_us,),
    ).fetchone()

    if row is None:
        return None

    completed_at_us = int(row[2])
    last_verified_at_us = (
        None if row[3] is None else int(row[3])
    )
    if completed_at_us < 0 or (
        last_verified_at_us is not None
        and last_verified_at_us < 0
    ):
        raise BackupVerificationPlanningError(
            "Backup verification timestamps must be non-negative."
        )

    return BackupDeepVerifyCandidate(
        snapshot_id=uuid_from_blob(bytes(row[0])),
        target_id=uuid_from_blob(bytes(row[1])),
        completed_at_us=completed_at_us,
        last_verified_at_us=last_verified_at_us,
        occurrence_slot_us=occurrence_slot_us,
    )
