"""Bridge durable job-scheduler lane ownership to WAL maintenance."""

from __future__ import annotations

import time

from athena.jobs.scheduler import SchedulerLane
from athena.storage.wal_maintenance import WalMaintenanceDiagnosis
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
