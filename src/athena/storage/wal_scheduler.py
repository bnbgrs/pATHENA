"""Scheduler-control-lane adapter for periodic SQLite WAL maintenance."""

from __future__ import annotations

import time
from collections.abc import Callable

from athena.storage.wal_maintenance import WalMaintenanceDiagnosis, WalMaintenanceError
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


class WalMaintenanceSchedulerAdapter:
    """Bridge an existing scheduler control lane to bounded WAL maintenance.

    The adapter deliberately owns no thread, timer, retry loop, or TRUNCATE path.
    Callers state whether the current scheduler tick owns control housekeeping;
    provider-only lanes therefore remain side-effect free.
    """

    def __init__(
        self,
        runner: WalMaintenanceIntervalRunner,
        *,
        monotonic_clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not isinstance(runner, WalMaintenanceIntervalRunner):
            raise TypeError(
                "WAL scheduler adapter requires WalMaintenanceIntervalRunner."
            )
        if not callable(monotonic_clock):
            raise TypeError("WAL scheduler monotonic_clock must be callable.")
        self.runner = runner
        self._monotonic_clock = monotonic_clock

    def run_control_housekeeping(
        self,
        *,
        now_monotonic: float | None = None,
    ) -> WalMaintenanceDiagnosis | None:
        """Run the WAL interval gate for a scheduler-owned control tick."""
        return self.run_tick(
            owns_control_housekeeping=True,
            now_monotonic=now_monotonic,
        )

    def run_tick(
        self,
        *,
        owns_control_housekeeping: bool,
        now_monotonic: float | None = None,
    ) -> WalMaintenanceDiagnosis | None:
        """Run due maintenance only for the scheduler control-housekeeping lane."""
        if not isinstance(owns_control_housekeeping, bool):
            raise WalMaintenanceError(
                "WAL scheduler ownership flag must be boolean."
            )
        if not owns_control_housekeeping:
            return None
        now = self._monotonic_clock() if now_monotonic is None else now_monotonic
        return self.runner.run_due(now_monotonic=now)
