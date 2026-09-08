from __future__ import annotations

import sys
from typing import cast

import pytest

from athena.storage.wal_maintenance import (
    WalMaintenanceDiagnosis,
    WalMaintenanceError,
    WalMaintenanceOrchestrator,
)
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


def _no_side_effect_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
) -> WalMaintenanceOrchestrator:
    orchestrator = object.__new__(WalMaintenanceOrchestrator)

    def run_cycle(_self: WalMaintenanceOrchestrator) -> WalMaintenanceDiagnosis:
        raise AssertionError("WAL maintenance must not run before deadline validation")

    monkeypatch.setattr(WalMaintenanceOrchestrator, "run_cycle", run_cycle)
    return orchestrator


def test_deadline_overflow_fails_before_wal_side_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = WalMaintenanceIntervalRunner(
        _no_side_effect_orchestrator(monkeypatch),
        interval_seconds=sys.float_info.max,
    )

    with pytest.raises(
        WalMaintenanceError,
        match="next due monotonic time must remain finite",
    ):
        runner.run_due(now_monotonic=sys.float_info.max)

    assert runner.next_due_monotonic is None


def test_monotonic_integer_overflow_fails_before_wal_side_effect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = WalMaintenanceIntervalRunner(
        _no_side_effect_orchestrator(monkeypatch),
        interval_seconds=60.0,
    )

    with pytest.raises(
        WalMaintenanceError,
        match="now_monotonic must be a finite non-negative number",
    ):
        runner.run_due(now_monotonic=cast(float, 10**400))

    assert runner.next_due_monotonic is None
