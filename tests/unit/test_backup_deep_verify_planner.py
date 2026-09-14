from __future__ import annotations

import sqlite3
import uuid
from typing import cast

import pytest

from athena.jobs.backup_verify import (
    deep_verify_occurrence_slot_us,
    select_deep_verify_candidate,
)


class _Database:
    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "CREATE TABLE backup_targets ("
            "target_id BLOB PRIMARY KEY, status TEXT NOT NULL)"
        )
        self.connection.execute(
            """
            CREATE TABLE backup_snapshots (
                snapshot_id BLOB PRIMARY KEY,
                target_id BLOB NOT NULL,
                state TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                completed_at_us INTEGER,
                last_verified_at_us INTEGER,
                pruned_at_us INTEGER
            )
            """
        )


class _Backup:
    def __init__(self) -> None:
        self.database = _Database()


def _add_snapshot(
    backup: _Backup,
    *,
    snapshot_id: uuid.UUID,
    target_id: uuid.UUID,
    target_status: str = "active",
    state: str = "complete",
    verification_status: str = "verified_light",
    completed_at_us: int = 1,
    last_verified_at_us: int | None = 1,
    pruned_at_us: int | None = None,
) -> None:
    backup.database.connection.execute(
        "INSERT OR REPLACE INTO backup_targets VALUES (?, ?)",
        (target_id.bytes, target_status),
    )
    backup.database.connection.execute(
        "INSERT INTO backup_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            snapshot_id.bytes,
            target_id.bytes,
            state,
            verification_status,
            completed_at_us,
            last_verified_at_us,
            pruned_at_us,
        ),
    )


def test_deep_verify_planner_selects_oldest_due_active_snapshot() -> None:
    backup = _Backup()
    target_id = uuid.uuid4()
    older = uuid.uuid4()
    newer = uuid.uuid4()
    _add_snapshot(
        backup,
        snapshot_id=newer,
        target_id=target_id,
        completed_at_us=30,
        last_verified_at_us=20,
    )
    _add_snapshot(
        backup,
        snapshot_id=older,
        target_id=target_id,
        completed_at_us=10,
        last_verified_at_us=5,
    )

    candidate = select_deep_verify_candidate(
        backup,
        now_us=2_000_000,
        interval_seconds=1,
    )

    assert candidate is not None
    assert candidate.snapshot_id == older
    assert candidate.target_id == target_id
    assert candidate.occurrence_slot_us == 2_000_000
    assert candidate.idempotency_key == (
        f"backup.verify_deep:{older}:2000000"
    )


def test_deep_verify_planner_excludes_unsafe_or_not_due_snapshots() -> None:
    backup = _Backup()
    _add_snapshot(
        backup,
        snapshot_id=uuid.uuid4(),
        target_id=uuid.uuid4(),
        verification_status="failed",
        last_verified_at_us=0,
    )
    _add_snapshot(
        backup,
        snapshot_id=uuid.uuid4(),
        target_id=uuid.uuid4(),
        pruned_at_us=1,
        last_verified_at_us=0,
    )
    _add_snapshot(
        backup,
        snapshot_id=uuid.uuid4(),
        target_id=uuid.uuid4(),
        target_status="offline",
        last_verified_at_us=0,
    )
    _add_snapshot(
        backup,
        snapshot_id=uuid.uuid4(),
        target_id=uuid.uuid4(),
        last_verified_at_us=9_000_000,
    )

    assert (
        select_deep_verify_candidate(
            backup,
            now_us=10_000_000,
            interval_seconds=5,
        )
        is None
    )


def test_deep_verify_planner_keeps_environment_retry_candidate_due() -> None:
    backup = _Backup()
    snapshot_id = uuid.uuid4()
    _add_snapshot(
        backup,
        snapshot_id=snapshot_id,
        target_id=uuid.uuid4(),
        last_verified_at_us=None,
    )

    candidate = select_deep_verify_candidate(
        backup,
        now_us=10_000_000,
        interval_seconds=5,
    )

    assert candidate is not None
    assert candidate.snapshot_id == snapshot_id


@pytest.mark.parametrize(
    ("now_us", "interval_seconds"),
    ((True, 5), (1, 0), (1, True)),
)
def test_deep_verify_occurrence_slot_rejects_invalid_runtime_types(
    now_us: object,
    interval_seconds: object,
) -> None:
    with pytest.raises(ValueError):
        deep_verify_occurrence_slot_us(
            cast(int, now_us),
            interval_seconds=cast(int, interval_seconds),
        )
