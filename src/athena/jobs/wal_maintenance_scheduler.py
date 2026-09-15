"""WAL-maintained durable scheduler composition for the control lane."""

from __future__ import annotations

from typing import Any

from athena.jobs.scheduler import (
    DurableJobScheduler,
    SchedulerLane,
    SchedulerTickResult,
)
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class WalMaintainedDurableJobScheduler(DurableJobScheduler):
    """Durable scheduler variant that runs existing WAL housekeeping safely.

    The class adds no WAL engine, timer, retry loop, or checkpoint policy. It reuses
    :class:`WalMaintenanceSchedulerAdapter` exactly once before CONTROL/ALL ticks and
    never touches WAL maintenance from the PROVIDER lane. Adapter errors propagate so
    the control tick fails closed before durable work is dispatched.
    """

    def __init__(
        self,
        *args: Any,
        wal_maintenance: WalMaintenanceSchedulerAdapter,
        **kwargs: Any,
    ) -> None:
        if not isinstance(wal_maintenance, WalMaintenanceSchedulerAdapter):
            raise TypeError(
                "WAL-maintained scheduler requires WalMaintenanceSchedulerAdapter."
            )
        super().__init__(*args, **kwargs)
        self.wal_maintenance = wal_maintenance

    def tick(
        self,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        """Run WAL housekeeping before scheduler-owned control work only."""
        normalized_lane = SchedulerLane(lane)
        if normalized_lane is not SchedulerLane.PROVIDER:
            self.wal_maintenance.run_control_housekeeping()
        return super().tick(
            worker_id=worker_id,
            now_us=now_us,
            lane=normalized_lane,
        )
