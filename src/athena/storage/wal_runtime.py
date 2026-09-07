"""Composition root for scheduler-owned SQLite WAL maintenance."""

from __future__ import annotations

from dataclasses import dataclass

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import (
    WalMaintenanceOrchestrator,
    WalMaintenanceService,
)
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


@dataclass(frozen=True, slots=True)
class WalMaintenanceRuntime:
    """One internally consistent scheduler-facing WAL maintenance stack."""

    service: WalMaintenanceService
    orchestrator: WalMaintenanceOrchestrator
    runner: WalMaintenanceIntervalRunner
    scheduler: WalMaintenanceSchedulerAdapter

    def __post_init__(self) -> None:
        if not isinstance(self.service, WalMaintenanceService):
            raise TypeError("WAL runtime service must be WalMaintenanceService.")
        if not isinstance(self.orchestrator, WalMaintenanceOrchestrator):
            raise TypeError("WAL runtime orchestrator must be WalMaintenanceOrchestrator.")
        if not isinstance(self.runner, WalMaintenanceIntervalRunner):
            raise TypeError("WAL runtime runner must be WalMaintenanceIntervalRunner.")
        if not isinstance(self.scheduler, WalMaintenanceSchedulerAdapter):
            raise TypeError("WAL runtime scheduler must be WalMaintenanceSchedulerAdapter.")
        if self.orchestrator.service is not self.service:
            raise ValueError("WAL runtime orchestrator must use the runtime service.")
        if self.runner.orchestrator is not self.orchestrator:
            raise ValueError("WAL runtime runner must use the runtime orchestrator.")
        if self.scheduler.runner is not self.runner:
            raise ValueError("WAL runtime scheduler must use the runtime runner.")


def build_wal_maintenance_runtime(
    database: SQLiteDatabase,
    *,
    interval_seconds: float,
    abnormal_size_multiplier: int = 4,
    blocked_cycle_threshold: int = 3,
    growth_cycle_threshold: int = 3,
) -> WalMaintenanceRuntime:
    """Build one bounded PASSIVE-only WAL maintenance stack.

    This function owns composition only. It starts no thread or timer, performs no
    checkpoint while constructing the stack, and exposes no automatic TRUNCATE path.
    """
    service = WalMaintenanceService(database)
    orchestrator = WalMaintenanceOrchestrator(
        service,
        abnormal_size_multiplier=abnormal_size_multiplier,
        blocked_cycle_threshold=blocked_cycle_threshold,
        growth_cycle_threshold=growth_cycle_threshold,
    )
    runner = WalMaintenanceIntervalRunner(
        orchestrator,
        interval_seconds=interval_seconds,
    )
    scheduler = WalMaintenanceSchedulerAdapter(runner)
    return WalMaintenanceRuntime(
        service=service,
        orchestrator=orchestrator,
        runner=runner,
        scheduler=scheduler,
    )
