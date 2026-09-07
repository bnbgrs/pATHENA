"""Scheduler-facing interval gate for bounded SQLite WAL maintenance."""

from __future__ import annotations

import math

from athena.storage.wal_maintenance import (
    WalMaintenanceDiagnosis,
    WalMaintenanceError,
    WalMaintenanceOrchestrator,
)


def _finite_nonnegative_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WalMaintenanceError(f"{label} must be a finite non-negative number.")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise WalMaintenanceError(f"{label} must be a finite non-negative number.")
    return normalized


def _finite_positive_number(value: object, label: str) -> float:
    normalized = _finite_nonnegative_number(value, label)
    if normalized <= 0:
        raise WalMaintenanceError(f"{label} must be greater than zero.")
    return normalized


class WalMaintenanceIntervalRunner:
    """Run scheduler-owned PASSIVE WAL maintenance at bounded monotonic intervals.

    This class intentionally owns no thread, timer, retry loop, or TRUNCATE path. A
    Core scheduler supplies a monotonic timestamp and decides when to call
    :meth:`run_due`. The wrapped orchestrator remains responsible for PASSIVE-only
    automatic maintenance and long-reader diagnosis.
    """

    def __init__(
        self,
        orchestrator: WalMaintenanceOrchestrator,
        *,
        interval_seconds: float,
    ) -> None:
        if not isinstance(orchestrator, WalMaintenanceOrchestrator):
            raise TypeError(
                "WAL interval runner requires WalMaintenanceOrchestrator."
            )
        self.orchestrator = orchestrator
        self.interval_seconds = _finite_positive_number(
            interval_seconds,
            "WAL maintenance interval_seconds",
        )
        self._next_due_monotonic: float | None = None
        self._last_observed_monotonic: float | None = None

    @property
    def next_due_monotonic(self) -> float | None:
        return self._next_due_monotonic

    def run_due(self, *, now_monotonic: float) -> WalMaintenanceDiagnosis | None:
        """Run one due cycle; return ``None`` when the interval has not elapsed."""
        now = _finite_nonnegative_number(
            now_monotonic,
            "WAL maintenance now_monotonic",
        )
        if (
            self._last_observed_monotonic is not None
            and now < self._last_observed_monotonic
        ):
            raise WalMaintenanceError(
                "WAL maintenance monotonic time must not move backwards."
            )
        self._last_observed_monotonic = now

        if self._next_due_monotonic is not None and now < self._next_due_monotonic:
            return None

        next_due = now + self.interval_seconds
        if not math.isfinite(next_due):
            raise WalMaintenanceError(
                "WAL maintenance next due monotonic time must remain finite."
            )

        diagnosis = self.orchestrator.run_cycle()
        if not isinstance(diagnosis, WalMaintenanceDiagnosis):
            raise WalMaintenanceError(
                "WAL maintenance orchestrator returned an invalid diagnosis."
            )
        self._next_due_monotonic = next_due
        return diagnosis
