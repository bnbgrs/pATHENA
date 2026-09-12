from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest

from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id
from athena.jobs.schedule_policy import MissedRunPolicy
from athena.jobs.schedule_recovery import recoverable_schedule_occurrences
from athena.jobs.scheduled_materialization import materialize_scheduled_job
from athena.storage.schema import initialize_schema


@pytest.fixture
def connection(tmp_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / "schedule-recovery.sqlite3", autocommit=True)
    conn.row_factory = sqlite3.Row
    initialize_schema(conn, created_at_us=1)
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


def _insert_actor(connection: sqlite3.Connection) -> uuid.UUID:
    actor_id = uuid.uuid4()
    connection.execute(
        """
        INSERT INTO actors (
            actor_id, actor_type, display_name, plugin_id, created_at_us, active
        ) VALUES (?, 'system', NULL, NULL, 1, 1)
        """,
        (actor_id.bytes,),
    )
    return actor_id


def _schedule(
    actor_id: uuid.UUID,
    *,
    policy: MissedRunPolicy = MissedRunPolicy.RUN_ONCE,
    max_backfill: int | None = None,
    enabled: bool = True,
) -> ScheduleDefinition:
    return ScheduleDefinition(
        schedule_id=uuid.uuid4(),
        job_type="research",
        schedule_expression="0 * * * *",
        timezone_name="UTC",
        created_by_actor_id=actor_id,
        created_at_us=1,
        updated_at_us=1,
        missed_run_policy=policy,
        max_backfill=max_backfill,
        enabled=enabled,
    )


def test_recovery_excludes_durable_occurrences_before_policy(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    connection.execute("BEGIN IMMEDIATE")
    materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=300,
        materialized_at_us=310,
    )
    connection.execute("COMMIT")

    assert recoverable_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200, 300),
        now_us=300,
    ) == (200,)


def test_recovery_applies_bounded_backfill_after_reconciliation(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(
        _insert_actor(connection),
        policy=MissedRunPolicy.BACKFILL_BOUNDED,
        max_backfill=2,
    )

    connection.execute("BEGIN IMMEDIATE")
    materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=200,
        materialized_at_us=210,
    )
    connection.execute("COMMIT")

    assert recoverable_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200, 300, 400),
        now_us=400,
    ) == (100, 300)


def test_recovery_ignores_future_occurrences(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(
        _insert_actor(connection),
        policy=MissedRunPolicy.BACKFILL_ALL,
    )

    assert recoverable_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200, 300),
        now_us=200,
    ) == (100, 200)


def test_disabled_schedule_has_no_recoverable_occurrences(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection), enabled=False)

    assert recoverable_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200),
        now_us=200,
    ) == ()


def test_recovery_rejects_foreign_occurrence_identity_binding(
    connection: sqlite3.Connection,
) -> None:
    actor_id = _insert_actor(connection)
    other_actor_id = _insert_actor(connection)
    schedule = _schedule(actor_id)
    job_id = occurrence_id(schedule.schedule_id, 100)

    connection.execute(
        """
        INSERT INTO jobs (
            job_id,
            job_type,
            created_at_us,
            created_by_actor_id,
            priority,
            state,
            retry_count,
            fencing_sequence,
            updated_at_us
        ) VALUES (?, 'foreign-job', 1, ?, 3, 'queued', 0, 0, 1)
        """,
        (job_id.bytes, other_actor_id.bytes),
    )

    with pytest.raises(RuntimeError, match="different job"):
        recoverable_schedule_occurrences(
            connection,
            schedule=schedule,
            candidate_occurrences_us=(100,),
            now_us=100,
        )


@pytest.mark.parametrize(
    "candidate_occurrences_us",
    [
        (200, 100),
        (100, 100),
    ],
)
def test_recovery_rejects_noncanonical_occurrence_sequence(
    connection: sqlite3.Connection,
    candidate_occurrences_us: tuple[int, ...],
) -> None:
    schedule = _schedule(_insert_actor(connection))

    with pytest.raises(ValueError, match="strictly increasing"):
        recoverable_schedule_occurrences(
            connection,
            schedule=schedule,
            candidate_occurrences_us=candidate_occurrences_us,
            now_us=200,
        )
