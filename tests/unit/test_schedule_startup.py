from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id
from athena.jobs.schedule_policy import MissedRunPolicy
from athena.jobs.schedule_startup import recover_and_materialize_schedule_occurrences
from athena.jobs.scheduled_materialization import materialize_scheduled_job
from athena.storage.schema import initialize_schema


@pytest.fixture
def connection(tmp_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / "schedule-startup.sqlite3", autocommit=True)
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
    policy: MissedRunPolicy = MissedRunPolicy.BACKFILL_ALL,
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


def test_startup_recovery_materializes_only_missing_due_occurrences(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    connection.execute("BEGIN IMMEDIATE")
    materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=200,
        materialized_at_us=201,
    )
    connection.execute("COMMIT")

    connection.execute("BEGIN IMMEDIATE")
    results = recover_and_materialize_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200, 300, 400),
        now_us=300,
        materialized_at_us=350,
    )
    connection.execute("COMMIT")

    assert tuple(result.job_id for result in results) == (
        occurrence_id(schedule.schedule_id, 100),
        occurrence_id(schedule.schedule_id, 300),
    )
    assert all(result.created for result in results)
    assert connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 3


def test_startup_recovery_applies_policy_before_materialization(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(
        _insert_actor(connection),
        policy=MissedRunPolicy.BACKFILL_BOUNDED,
        max_backfill=2,
    )

    connection.execute("BEGIN IMMEDIATE")
    results = recover_and_materialize_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200, 300),
        now_us=300,
        materialized_at_us=400,
        priority=JobPriority.HIGH,
    )
    connection.execute("COMMIT")

    assert tuple(result.job_id for result in results) == (
        occurrence_id(schedule.schedule_id, 100),
        occurrence_id(schedule.schedule_id, 200),
    )
    rows = connection.execute(
        "SELECT job_id, priority FROM jobs ORDER BY next_run_at_us"
    ).fetchall()
    assert tuple(bytes(row[0]) for row in rows) == tuple(
        result.job_id.bytes for result in results
    )
    assert all(int(row[1]) == int(JobPriority.HIGH) for row in rows)


def test_startup_recovery_disabled_schedule_creates_nothing(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection), enabled=False)

    connection.execute("BEGIN IMMEDIATE")
    results = recover_and_materialize_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=(100, 200),
        now_us=200,
        materialized_at_us=250,
    )
    connection.execute("COMMIT")

    assert results == ()
    assert connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 0


def test_startup_recovery_requires_caller_transaction(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    with pytest.raises(RuntimeError, match="active write transaction"):
        recover_and_materialize_schedule_occurrences(
            connection,
            schedule=schedule,
            candidate_occurrences_us=(100,),
            now_us=100,
            materialized_at_us=101,
        )


def test_startup_recovery_fails_before_inserts_on_foreign_identity_collision(
    connection: sqlite3.Connection,
) -> None:
    actor_id = _insert_actor(connection)
    foreign_actor_id = _insert_actor(connection)
    schedule = _schedule(actor_id)
    colliding_job_id = occurrence_id(schedule.schedule_id, 200)

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
        (colliding_job_id.bytes, foreign_actor_id.bytes),
    )

    connection.execute("BEGIN IMMEDIATE")
    with pytest.raises(RuntimeError, match="different job"):
        recover_and_materialize_schedule_occurrences(
            connection,
            schedule=schedule,
            candidate_occurrences_us=(100, 200),
            now_us=200,
            materialized_at_us=250,
        )
    connection.execute("ROLLBACK")

    assert connection.execute(
        "SELECT COUNT(*) FROM jobs WHERE job_id = ?",
        (occurrence_id(schedule.schedule_id, 100).bytes,),
    ).fetchone()[0] == 0
