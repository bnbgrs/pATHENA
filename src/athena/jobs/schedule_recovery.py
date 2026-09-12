"""Recovery enumeration for durable scheduled job occurrences."""

from __future__ import annotations

import sqlite3

from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id
from athena.jobs.schedule_policy import MissedRunPolicy, select_missed_occurrences


def recoverable_schedule_occurrences(
    connection: sqlite3.Connection,
    *,
    schedule: ScheduleDefinition,
    candidate_occurrences_us: tuple[int, ...],
    now_us: int,
) -> tuple[int, ...]:
    """Return due schedule occurrences that still require durable materialization.

    Existing deterministic occurrence job IDs are treated as already materialized.
    Identity collisions fail closed instead of silently adopting an unrelated job.
    Missed-run policy is applied only after durable-state reconciliation.
    """

    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("connection must be a sqlite3.Connection.")
    if not isinstance(schedule, ScheduleDefinition):
        raise TypeError("schedule must be a ScheduleDefinition.")
    if not schedule.enabled:
        return ()

    due_occurrences = select_missed_occurrences(
        candidate_occurrences_us,
        now_us=now_us,
        policy=MissedRunPolicy.BACKFILL_ALL,
    )

    missing: list[int] = []
    for scheduled_at_us in due_occurrences:
        job_id = occurrence_id(schedule.schedule_id, scheduled_at_us)
        row = connection.execute(
            """
            SELECT job_type, created_by_actor_id
            FROM jobs
            WHERE job_id = ?
            """,
            (job_id.bytes,),
        ).fetchone()
        if row is None:
            missing.append(scheduled_at_us)
            continue

        if (
            str(row[0]) != schedule.job_type
            or bytes(row[1]) != schedule.created_by_actor_id.bytes
        ):
            raise RuntimeError(
                "Scheduled occurrence identity is already bound to a different job."
            )

    return select_missed_occurrences(
        missing,
        now_us=now_us,
        policy=schedule.missed_run_policy,
        max_backfill=schedule.max_backfill,
    )
