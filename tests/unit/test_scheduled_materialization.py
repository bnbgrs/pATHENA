from __future__ import annotations

import sqlite3
import uuid

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id
from athena.jobs.schedule_policy import MissedRunPolicy
from athena.jobs.scheduled_materialization import materialize_scheduled_job
from athena.storage.schema import initialize_schema


@pytest.fixture
def connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", autocommit=True)
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


def _schedule(actor_id: uuid.UUID, *, enabled: bool = True) -> ScheduleDefinition:
    return ScheduleDefinition(
        schedule_id=uuid.uuid4(),
        job_type="research",
        schedule_expression="0 * * * *",
        timezone_name="UTC",
        created_by_actor_id=actor_id,
        created_at_us=1,
        updated_at_us=1,
        missed_run_policy=MissedRunPolicy.RUN_ONCE,
        max_backfill=None,
        enabled=enabled,
    )


def test_same_occurrence_materializes_once_across_retry(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    connection.execute("BEGIN IMMEDIATE")
    first = materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=100,
        materialized_at_us=110,
    )
    connection.execute("COMMIT")

    connection.execute("BEGIN IMMEDIATE")
    retry = materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=100,
        materialized_at_us=120,
    )
    connection.execute("COMMIT")

    assert first.job_id == retry.job_id
    assert first.created is True
    assert retry.created is False
    assert connection.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1


def test_distinct_occurrences_materialize_distinct_jobs(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    connection.execute("BEGIN IMMEDIATE")
    first = materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=100,
        materialized_at_us=110,
    )
    second = materialize_scheduled_job(
        connection,
        schedule=schedule,
        scheduled_at_us=200,
        materialized_at_us=210,
        priority=JobPriority.TIME_CRITICAL,
    )
    connection.execute("COMMIT")

    assert first.job_id != second.job_id
    assert connection.execute("SELECT count(*) FROM jobs").fetchone()[0] == 2


def test_materialization_requires_existing_write_transaction(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection))

    with pytest.raises(RuntimeError, match="active write transaction"):
        materialize_scheduled_job(
            connection,
            schedule=schedule,
            scheduled_at_us=100,
            materialized_at_us=110,
        )


def test_disabled_schedule_fails_closed_without_row(
    connection: sqlite3.Connection,
) -> None:
    schedule = _schedule(_insert_actor(connection), enabled=False)

    connection.execute("BEGIN IMMEDIATE")
    with pytest.raises(ValueError, match="Disabled schedules"):
        materialize_scheduled_job(
            connection,
            schedule=schedule,
            scheduled_at_us=100,
            materialized_at_us=110,
        )
    connection.execute("ROLLBACK")

    assert connection.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0


def test_existing_foreign_binding_fails_closed(
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

    connection.execute("BEGIN IMMEDIATE")
    with pytest.raises(RuntimeError, match="different job"):
        materialize_scheduled_job(
            connection,
            schedule=schedule,
            scheduled_at_us=100,
            materialized_at_us=110,
        )
    connection.execute("ROLLBACK")

    assert connection.execute("SELECT count(*) FROM jobs").fetchone()[0] == 1
