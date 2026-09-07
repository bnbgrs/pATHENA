"""Bridge durable job-scheduler lane ownership to WAL maintenance."""

from __future__ import annotations

import time

from athena.jobs.scheduler import SchedulerLane
from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceDiagnosis
from athena.storage.wal_runtime import build_wal_maintenance_runtime
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class WalJobSchedulerHook:
    """Invoke WAL maintenance from an existing durable scheduler tick.

    The hook owns no thread, timer, retry loop, or TRUNCATE path. Provider-only
    lanes remain side-effect free; ALL and CONTROL own control housekeeping.
    """

    def __init__(self, scheduler: WalMaintenanceSchedulerAdapter) -> None:
        if not isinstance(scheduler, WalMaintenanceSchedulerAdapter):
            raise TypeError(
                "WAL job scheduler hook requires WalMaintenanceSchedulerAdapter."
            )
        self.scheduler = scheduler

    def run_for_lane(
        self,
        *,
        lane: SchedulerLane,
        now_monotonic: float | None = None,
    ) -> WalMaintenanceDiagnosis | None:
        """Run due WAL maintenance for one already-selected scheduler lane."""
        normalized_lane = SchedulerLane(lane)
        observed_monotonic = time.monotonic() if now_monotonic is None else now_monotonic
        return self.scheduler.run_tick(
            owns_control_housekeeping=normalized_lane is not SchedulerLane.PROVIDER,
            now_monotonic=observed_monotonic,
        )


def build_wal_job_scheduler_hook(
    database: SQLiteDatabase,
    *,
    interval_seconds: float,
    abnormal_size_multiplier: int = 4,
    blocked_cycle_threshold: int = 3,
    growth_cycle_threshold: int = 3,
) -> WalJobSchedulerHook:
    """Compose one scheduler-lane hook from the bounded WAL runtime stack.

    Construction is side-effect free: it starts no scheduler/thread/timer, opens no
    database connection, performs no checkpoint, and exposes no automatic TRUNCATE.
    """
    runtime = build_wal_maintenance_runtime(
        database,
        interval_seconds=interval_seconds,
        abnormal_size_multiplier=abnormal_size_multiplier,
        blocked_cycle_threshold=blocked_cycle_threshold,
        growth_cycle_threshold=growth_cycle_threshold,
    )
    return WalJobSchedulerHook(runtime.scheduler)
