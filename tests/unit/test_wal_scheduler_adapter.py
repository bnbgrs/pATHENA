from __future__ import annotations

import pytest

from athena.storage.wal_maintenance import (
    WalMaintenanceCycle,
    WalMaintenanceDiagnosis,
    WalMaintenanceError,
    WalRuntimeStatus,
)
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class _StubOrchestrator:
    def __init__(self, diagnosis: WalMaintenanceDiagnosis) -> None:
        self.diagnosis = diagnosis
        self.calls = 0

    def run_cycle(self) -> WalMaintenanceDiagnosis:
        self.calls += 1
        return self.diagnosis


def _diagnosis(tmp_path) -> WalMaintenanceDiagnosis:
    status = WalRuntimeStatus(
        wal_path=(tmp_path / "athena.db-wal").resolve(),
        present=False,
        size_bytes=0,
        page_size_bytes=4096,
        autocheckpoint_pages=1000,
        autocheckpoint_bytes=4_096_000,
    )
    cycle = WalMaintenanceCycle(
        status_before=status,
        checkpoint=None,
        status_after=status,
    )
    return WalMaintenanceDiagnosis(
        level="HEALTHY",
        cycle=cycle,
        consecutive_blocked_cycles=0,
        consecutive_growth_cycles=0,
    )


def _adapter(tmp_path):
    orchestrator = _StubOrchestrator(_diagnosis(tmp_path))
    runner = object.__new__(WalMaintenanceIntervalRunner)
    runner.orchestrator = orchestrator
    runner.interval_seconds = 60.0
    runner._next_due_monotonic = None
    runner._last_observed_monotonic = None
    return WalMaintenanceSchedulerAdapter(runner), orchestrator


def test_provider_only_tick_is_side_effect_free(tmp_path) -> None:
    adapter, orchestrator = _adapter(tmp_path)

    result = adapter.run_tick(
        owns_control_housekeeping=False,
        now_monotonic=10.0,
    )

    assert result is None
    assert orchestrator.calls == 0
    assert adapter.runner.next_due_monotonic is None


def test_control_tick_runs_existing_interval_gate(tmp_path) -> None:
    adapter, orchestrator = _adapter(tmp_path)

    result = adapter.run_tick(
        owns_control_housekeeping=True,
        now_monotonic=10.0,
    )

    assert isinstance(result, WalMaintenanceDiagnosis)
    assert orchestrator.calls == 1
    assert adapter.runner.next_due_monotonic == 70.0


def test_non_boolean_lane_ownership_fails_before_runner(tmp_path) -> None:
    adapter, orchestrator = _adapter(tmp_path)

    with pytest.raises(WalMaintenanceError, match="ownership flag must be boolean"):
        adapter.run_tick(
            owns_control_housekeeping=1,  # type: ignore[arg-type]
            now_monotonic=10.0,
        )

    assert orchestrator.calls == 0
    assert adapter.runner.next_due_monotonic is None
