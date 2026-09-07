from __future__ import annotations

import pytest

from athena.jobs.scheduler import SchedulerLane
from athena.storage.wal_job_hook import WalJobSchedulerHook
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


def _hook(tmp_path):
    status = WalRuntimeStatus(
        wal_path=(tmp_path / "athena.db-wal").resolve(),
        present=False,
        size_bytes=0,
        page_size_bytes=4096,
        autocheckpoint_pages=1000,
        autocheckpoint_bytes=4_096_000,
    )
    diagnosis = WalMaintenanceDiagnosis(
        level="HEALTHY",
        cycle=WalMaintenanceCycle(
            status_before=status,
            checkpoint=None,
            status_after=status,
        ),
        consecutive_blocked_cycles=0,
        consecutive_growth_cycles=0,
    )
    orchestrator = _StubOrchestrator(diagnosis)
    runner = object.__new__(WalMaintenanceIntervalRunner)
    runner.orchestrator = orchestrator
    runner.interval_seconds = 60.0
    runner._next_due_monotonic = None
    runner._last_observed_monotonic = None
    adapter = WalMaintenanceSchedulerAdapter(runner)
    return WalJobSchedulerHook(adapter), orchestrator


def test_provider_lane_remains_wal_side_effect_free(tmp_path) -> None:
    hook, orchestrator = _hook(tmp_path)

    result = hook.run_for_lane(
        lane=SchedulerLane.PROVIDER,
        now_monotonic=10.0,
    )

    assert result is None
    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None


@pytest.mark.parametrize("lane", [SchedulerLane.ALL, SchedulerLane.CONTROL])
def test_control_owning_lanes_delegate_to_interval_gate(tmp_path, lane: SchedulerLane) -> None:
    hook, orchestrator = _hook(tmp_path)

    result = hook.run_for_lane(lane=lane, now_monotonic=10.0)

    assert isinstance(result, WalMaintenanceDiagnosis)
    assert orchestrator.calls == 1
    assert hook.scheduler.runner.next_due_monotonic == 70.0


def test_invalid_lane_fails_before_wal_side_effect(tmp_path) -> None:
    hook, orchestrator = _hook(tmp_path)

    with pytest.raises(ValueError):
        hook.run_for_lane(
            lane="provider-ish",  # type: ignore[arg-type]
            now_monotonic=10.0,
        )

    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None


def test_nonfinite_monotonic_fails_before_wal_cycle(tmp_path) -> None:
    hook, orchestrator = _hook(tmp_path)

    with pytest.raises(WalMaintenanceError):
        hook.run_for_lane(
            lane=SchedulerLane.CONTROL,
            now_monotonic=float("nan"),
        )

    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None
