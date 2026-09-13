"""Transactional startup recovery for durable scheduled job occurrences."""

from __future__ import annotations

import sqlite3

from athena.jobs.models import JobPriority
from athena.jobs.schedule_definition import ScheduleDefinition
from athena.jobs.schedule_recovery import recoverable_schedule_occurrences
from athena.jobs.scheduled_materialization import (
    ScheduledJobMaterialization,
    materialize_scheduled_job,
)


def recover_and_materialize_schedule_occurrences(
    connection: sqlite3.Connection,
    *,
    schedule: ScheduleDefinition,
    candidate_occurrences_us: tuple[int, ...],
    now_us: int,
    materialized_at_us: int,
    priority: JobPriority = JobPriority.NORMAL,
    requested_scope_json: str | None = None,
    pinned_configuration_json: str | None = None,
) -> tuple[ScheduledJobMaterialization, ...]:
    """Reconcile and materialize all due missing occurrences in one transaction.

    The caller owns the write transaction. Durable reconciliation is performed
    before any inserts, then every selected occurrence is materialized using the
    deterministic occurrence identity. Any collision or write failure aborts via
    the caller's transaction boundary instead of returning a partial success set.
    """

    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("connection must be a sqlite3.Connection.")
    if not connection.in_transaction:
        raise RuntimeError(
            "Scheduled recovery materialization requires an active write transaction."
        )
    if not isinstance(schedule, ScheduleDefinition):
        raise TypeError("schedule must be a ScheduleDefinition.")
    if not isinstance(priority, JobPriority):
        raise TypeError("priority must be a JobPriority.")

    recoverable = recoverable_schedule_occurrences(
        connection,
        schedule=schedule,
        candidate_occurrences_us=candidate_occurrences_us,
        now_us=now_us,
    )

    return tuple(
        materialize_scheduled_job(
            connection,
            schedule=schedule,
            scheduled_at_us=scheduled_at_us,
            materialized_at_us=materialized_at_us,
            priority=priority,
            requested_scope_json=requested_scope_json,
            pinned_configuration_json=pinned_configuration_json,
        )
        for scheduled_at_us in recoverable
    )
