"""Transactional materialization of durable scheduled job occurrences."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from athena.jobs.models import JobPriority
from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id


@dataclass(frozen=True, slots=True)
class ScheduledJobMaterialization:
    """Outcome of materializing one logical schedule occurrence."""

    job_id: uuid.UUID
    created: bool


def _require_timestamp_us(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer microsecond timestamp.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


def materialize_scheduled_job(
    connection: sqlite3.Connection,
    *,
    schedule: ScheduleDefinition,
    scheduled_at_us: int,
    materialized_at_us: int,
    priority: JobPriority = JobPriority.NORMAL,
    requested_scope_json: str | None = None,
    pinned_configuration_json: str | None = None,
) -> ScheduledJobMaterialization:
    """Create exactly one durable job for a schedule occurrence.

    The caller must hold ATHENA's write transaction. The deterministic occurrence
    UUID is used directly as ``jobs.job_id``, so SQLite's existing primary-key
    constraint is the durable idempotency boundary across retries and restarts.
    """

    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("connection must be a sqlite3.Connection.")
    if not connection.in_transaction:
        raise RuntimeError(
            "Scheduled job materialization requires an active write transaction."
        )
    if not isinstance(schedule, ScheduleDefinition):
        raise TypeError("schedule must be a ScheduleDefinition.")
    if not schedule.enabled:
        raise ValueError("Disabled schedules cannot materialize job occurrences.")
    if not isinstance(priority, JobPriority):
        raise TypeError("priority must be a JobPriority.")

    scheduled_for = _require_timestamp_us(scheduled_at_us, "scheduled_at_us")
    materialized_at = _require_timestamp_us(materialized_at_us, "materialized_at_us")
    job_id = occurrence_id(schedule.schedule_id, scheduled_for)

    cursor = connection.execute(
        """
        INSERT INTO jobs (
            job_id,
            job_type,
            created_at_us,
            created_by_actor_id,
            priority,
            state,
            requested_scope_json,
            retry_count,
            next_run_at_us,
            pinned_configuration_json,
            fencing_sequence,
            updated_at_us
        ) VALUES (?, ?, ?, ?, ?, 'queued', ?, 0, ?, ?, 0, ?)
        ON CONFLICT(job_id) DO NOTHING
        """,
        (
            job_id.bytes,
            schedule.job_type,
            materialized_at,
            schedule.created_by_actor_id.bytes,
            int(priority),
            requested_scope_json,
            scheduled_for,
            pinned_configuration_json,
            materialized_at,
        ),
    )
    created = cursor.rowcount == 1

    row = connection.execute(
        """
        SELECT job_type, created_by_actor_id
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id.bytes,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Scheduled job materialization did not persist a job row.")
    if (
        str(row[0]) != schedule.job_type
        or bytes(row[1]) != schedule.created_by_actor_id.bytes
    ):
        raise RuntimeError(
            "Scheduled occurrence identity is already bound to a different job."
        )

    return ScheduledJobMaterialization(job_id=job_id, created=created)
