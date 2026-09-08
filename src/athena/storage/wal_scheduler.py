"""Scheduler-control-lane adapter for periodic SQLite WAL maintenance."""

from __future__ import annotations

from athena.storage.wal_maintenance import WalMaintenanceDiagnosis, WalMaintenanceError
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


class WalMaintenanceSchedulerAdapter:
    """Bridge an existing scheduler control lane to bounded WAL maintenance.

    The adapter deliberately owns no thread, timer, retry loop, or TRUNCATE path.
    Callers state whether the current scheduler tick owns control housekeeping;
    provider-only lanes therefore remain side-effect free.
    """

    def __init__(self, runner: WalMaintenanceIntervalRunner) -> None:
        if type(runner) is not WalMaintenanceIntervalRunner:
            raise TypeError(
                "WAL scheduler adapter requires canonical WalMaintenanceIntervalRunner."
            )
        self.runner = runner

    def run_tick(
        self,
        *,
        owns_control_housekeeping: bool,
        now_monotonic: float,
    ) -> WalMaintenanceDiagnosis | None:
        """Run due maintenance only for the scheduler control-housekeeping lane."""
        if not isinstance(owns_control_housekeeping, bool):
            raise WalMaintenanceError(
                "WAL scheduler ownership flag must be boolean."
            )
        if not owns_control_housekeeping:
            return None
        return self.runner.run_due(now_monotonic=now_monotonic)
