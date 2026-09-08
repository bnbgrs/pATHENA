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


def _canonical_orchestrator(
    monkeypatch: pytest.MonkeyPatch,
    result: WalMaintenanceDiagnosis,
) -> tuple[WalMaintenanceOrchestrator, list[None]]:
    orchestrator = object.__new__(WalMaintenanceOrchestrator)
    calls: list[None] = []

    def run_cycle(_self: WalMaintenanceOrchestrator) -> WalMaintenanceDiagnosis:
        calls.append(None)
        return result

    monkeypatch.setattr(WalMaintenanceOrchestrator, "run_cycle", run_cycle)
    return orchestrator, calls


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, float("nan"), float("inf"), float("-inf")],
)
def test_interval_runner_rejects_invalid_interval(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator, calls = _canonical_orchestrator(monkeypatch, _diagnosis())

    with pytest.raises(WalMaintenanceError):
        WalMaintenanceIntervalRunner(
            orchestrator,
            interval_seconds=cast(float, value),
        )

    assert calls == []


def test_interval_runner_runs_immediately_then_only_when_due(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    diagnosis = _diagnosis()
    orchestrator, calls = _canonical_orchestrator(monkeypatch, diagnosis)
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    first = runner.run_due(now_monotonic=100.0)
    early = runner.run_due(now_monotonic=109.999)
    second = runner.run_due(now_monotonic=110.0)

    assert first is diagnosis
    assert early is None
    assert second is diagnosis
    assert len(calls) == 2
    assert runner.next_due_monotonic == 120.0


@pytest.mark.parametrize(
    "value",
    [True, False, -1, float("nan"), float("inf"), float("-inf")],
)
def test_interval_runner_rejects_invalid_now_before_orchestrator_side_effect(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator, calls = _canonical_orchestrator(monkeypatch, _diagnosis())
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    with pytest.raises(WalMaintenanceError):
        runner.run_due(now_monotonic=cast(float, value))

    assert calls == []
    assert runner.next_due_monotonic is None


def test_interval_runner_rejects_monotonic_regression_before_cycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator, calls = _canonical_orchestrator(monkeypatch, _diagnosis())
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)
    runner.run_due(now_monotonic=100.0)

    with pytest.raises(WalMaintenanceError, match="must not move backwards"):
        runner.run_due(now_monotonic=99.0)

    assert len(calls) == 1
    assert runner.next_due_monotonic == 110.0


def test_interval_runner_rejects_invalid_orchestrator_result_without_reschedule(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    orchestrator, calls = _canonical_orchestrator(
        monkeypatch,
        cast(WalMaintenanceDiagnosis, object()),
    )
    runner = WalMaintenanceIntervalRunner(orchestrator, interval_seconds=10.0)

    with pytest.raises(WalMaintenanceError, match="invalid diagnosis"):
        runner.run_due(now_monotonic=100.0)

    assert len(calls) == 1
    assert runner.next_due_monotonic is None
