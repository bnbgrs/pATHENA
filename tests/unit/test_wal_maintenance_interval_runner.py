from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from athena.storage.wal_maintenance import (
    WalMaintenanceCycle,
    WalMaintenanceDiagnosis,
    WalMaintenanceError,
    WalMaintenanceOrchestrator,
    WalRuntimeStatus,
)
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


def _diagnosis() -> WalMaintenanceDiagnosis:
    status = WalRuntimeStatus(
        wal_path=Path.cwd().resolve() / "athena.db-wal",
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


class _RecordingOrchestrator(WalMaintenanceOrchestrator):
    def __init__(self, result: WalMaintenanceDiagnosis) -> None:
        self.result = result
        self.calls = 0

    def run_cycle(self) -> WalMaintenanceDiagnosis:
        self.calls += 1
        return self.result


class _InvalidOrchestrator(WalMaintenanceOrchestrator):
    def __init__(self) -> None:
        self.calls = 0

    def run_cycle(self) -> WalMaintenanceDiagnosis:
        self.calls += 1
        return cast(WalMaintenanceDiagnosis, object())


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, float("nan"), float("inf"), float("-inf")],
)
def test_interval_runner_rejects_invalid_interval(value: object) -> None:
    with pytest.raises(WalMaintenanceError):
        WalMaintenanceIntervalRunner(
            _RecordingOrchestrator(_diagnosis()),
            interval_seconds=cast(float, value),
        )


def test_interval_runner_runs_immediately_then_only_when_due() -> None:
    orchestrator = _RecordingOrchestrator(_diagnosis())
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    first = runner.run_due(now_monotonic=100.0)
    early = runner.run_due(now_monotonic=109.999)
    second = runner.run_due(now_monotonic=110.0)

    assert first is orchestrator.result
    assert early is None
    assert second is orchestrator.result
    assert orchestrator.calls == 2
    assert runner.next_due_monotonic == 120.0


@pytest.mark.parametrize(
    "value",
    [True, False, -1, float("nan"), float("inf"), float("-inf")],
)
def test_interval_runner_rejects_invalid_now_before_orchestrator_side_effect(
    value: object,
) -> None:
    orchestrator = _RecordingOrchestrator(_diagnosis())
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    with pytest.raises(WalMaintenanceError):
        runner.run_due(now_monotonic=cast(float, value))

    assert orchestrator.calls == 0
    assert runner.next_due_monotonic is None


def test_interval_runner_rejects_monotonic_regression_before_cycle() -> None:
    orchestrator = _RecordingOrchestrator(_diagnosis())
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)
    runner.run_due(now_monotonic=100.0)

    with pytest.raises(WalMaintenanceError, match="must not move backwards"):
        runner.run_due(now_monotonic=99.0)

    assert orchestrator.calls == 1
    assert runner.next_due_monotonic == 110.0


def test_interval_runner_rejects_invalid_orchestrator_result_without_reschedule() -> None:
    orchestrator = _InvalidOrchestrator()
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    with pytest.raises(WalMaintenanceError, match="invalid diagnosis"):
        runner.run_due(now_monotonic=100.0)

    assert orchestrator.calls == 1
    assert runner.next_due_monotonic is None
