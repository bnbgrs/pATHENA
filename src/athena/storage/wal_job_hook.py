"""Bridge durable job-scheduler lane ownership to WAL maintenance."""

from __future__ import annotations

import time

from athena.jobs.scheduler import DurableJobScheduler, SchedulerLane, SchedulerTickResult
from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceDiagnosis
from athena.storage.wal_runtime import build_wal_maintenance_runtime
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


def _normalize_worker_id(worker_id: object) -> str:
    """Validate scheduler worker identity before any WAL or job side effect."""
    if not isinstance(worker_id, str):
        raise TypeError("Scheduler worker_id must be text.")
    normalized_worker_id = worker_id.strip()
    if not normalized_worker_id:
        raise ValueError("Scheduler worker_id must not be empty.")
    return normalized_worker_id


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


def run_scheduler_tick_with_wal_housekeeping(
    scheduler: DurableJobScheduler,
    hook: WalJobSchedulerHook,
    *,
    worker_id: str,
    lane: SchedulerLane = SchedulerLane.ALL,
    now_us: int | None = None,
    now_monotonic: float | None = None,
) -> SchedulerTickResult:
    """Run one existing durable scheduler tick with bounded WAL housekeeping.

    WAL housekeeping executes only through the already selected scheduler lane.
    Provider-only lanes remain WAL-side-effect free. A housekeeping validation or
    maintenance failure aborts before durable job selection/dispatch, so the two
    control-plane effects cannot silently diverge.
    """
    normalized_worker_id = _normalize_worker_id(worker_id)
    normalized_lane = SchedulerLane(lane)
    if type(scheduler) is not DurableJobScheduler:
        raise TypeError(
            "WAL scheduler boundary requires the canonical DurableJobScheduler."
        )
    if not isinstance(hook, WalJobSchedulerHook):
        raise TypeError("WAL scheduler boundary requires WalJobSchedulerHook.")
    hook.run_for_lane(
        lane=normalized_lane,
        now_monotonic=now_monotonic,
    )
    return scheduler.tick(
        worker_id=normalized_worker_id,
        now_us=now_us,
        lane=normalized_lane,
    )


class WalAwareDurableJobScheduler(DurableJobScheduler):
    """Use the existing durable scheduler loop with bounded WAL housekeeping.

    This class intentionally inherits ``drain`` and ``run_loop`` unchanged. Their
    existing ``self.tick(...)`` dispatch reaches this override, so WAL maintenance
    is attached without introducing a second loop, timer, thread, or retry path.
    A hook must be explicitly bound before the first tick.
    """

    _wal_housekeeping_hook: WalJobSchedulerHook | None = None

    @classmethod
    def from_scheduler(
        cls,
        scheduler: DurableJobScheduler,
        hook: WalJobSchedulerHook,
    ) -> WalAwareDurableJobScheduler:
        """Recompose an existing scheduler with identical dependencies and policy.

        The conversion performs no scheduler tick, WAL access, database open, thread
        creation, or timer creation. It exists so application composition can replace
        the scheduler atomically without duplicating its dependency list or changing
        the inherited run-loop semantics.
        """
        if isinstance(scheduler, WalAwareDurableJobScheduler):
            raise ValueError("Scheduler is already WAL-aware.")
        if type(scheduler) is not DurableJobScheduler:
            raise TypeError(
                "WAL-aware scheduler source must be the canonical DurableJobScheduler."
            )
        if not isinstance(hook, WalJobSchedulerHook):
            raise TypeError("WAL-aware scheduler requires WalJobSchedulerHook.")

        converted = cls(
            jobs=scheduler.jobs,
            source_worker=scheduler.source_worker,
            embedding_worker=scheduler.embedding_worker,
            analysis_worker=scheduler.analysis_worker,
            extraction_worker=scheduler.extraction_worker,
            research_worker=scheduler.research_worker,
            archive_replication_worker=scheduler.archive_replication_worker,
            backup_worker=scheduler.backup_worker,
            resources=scheduler.resources,
            news_worker=scheduler.news_worker,
            policy=scheduler.policy,
        )
        converted.bind_wal_housekeeping(hook)
        return converted

    def bind_wal_housekeeping(self, hook: WalJobSchedulerHook) -> None:
        """Bind the composed WAL hook exactly once without performing I/O."""
        if not isinstance(hook, WalJobSchedulerHook):
            raise TypeError("WAL-aware scheduler requires WalJobSchedulerHook.")
        if self._wal_housekeeping_hook is not None:
            raise RuntimeError("WAL-aware scheduler housekeeping is already bound.")
        self._wal_housekeeping_hook = hook

    def tick(
        self,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        """Run bounded WAL housekeeping, then the canonical durable scheduler tick."""
        normalized_worker_id = _normalize_worker_id(worker_id)
        normalized_lane = SchedulerLane(lane)
        hook = self._wal_housekeeping_hook
        if hook is None:
            raise RuntimeError(
                "WAL-aware scheduler requires housekeeping binding before tick."
            )
        hook.run_for_lane(lane=normalized_lane)
        return super().tick(
            worker_id=normalized_worker_id,
            now_us=now_us,
            lane=normalized_lane,
        )