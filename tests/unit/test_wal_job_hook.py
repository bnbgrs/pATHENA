from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from athena.jobs.scheduler import (
    DurableJobScheduler,
    SchedulerLane,
    SchedulerPolicy,
    SchedulerTickResult,
)
from athena.storage.database import SQLiteDatabase
from athena.storage.wal_job_hook import (
    WalAwareDurableJobScheduler,
    WalJobSchedulerHook,
    build_wal_job_scheduler_hook,
    run_scheduler_tick_with_wal_housekeeping,
)
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


class _StubDurableScheduler:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int | None, SchedulerLane]] = []
        self.result = cast(SchedulerTickResult, object())

    def tick(
        self,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        self.calls.append((worker_id, now_us, lane))
        return self.result


def _hook(tmp_path: Path) -> tuple[WalJobSchedulerHook, _StubOrchestrator]:
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


def _database(tmp_path: Path) -> SQLiteDatabase:
    return SQLiteDatabase((tmp_path / "athena.db").resolve())


def _idle_tick_result() -> SchedulerTickResult:
    return SchedulerTickResult(
        recovered_jobs=0,
        scheduled_retries=0,
        woken_jobs=0,
        selected_job_id=None,
        selected_job_type=None,
        action="idle",
        final_state=None,
        fencing_sequence=None,
    )


def test_provider_lane_remains_wal_side_effect_free(tmp_path: Path) -> None:
    hook, orchestrator = _hook(tmp_path)

    result = hook.run_for_lane(
        lane=SchedulerLane.PROVIDER,
        now_monotonic=10.0,
    )

    assert result is None
    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None


@pytest.mark.parametrize("lane", [SchedulerLane.ALL, SchedulerLane.CONTROL])
def test_control_owning_lanes_delegate_to_interval_gate(
    tmp_path: Path,
    lane: SchedulerLane,
) -> None:
    hook, orchestrator = _hook(tmp_path)

    result = hook.run_for_lane(lane=lane, now_monotonic=10.0)

    assert isinstance(result, WalMaintenanceDiagnosis)
    assert orchestrator.calls == 1
    assert hook.scheduler.runner.next_due_monotonic == 70.0


def test_invalid_lane_fails_before_wal_side_effect(tmp_path: Path) -> None:
    hook, orchestrator = _hook(tmp_path)

    with pytest.raises(ValueError):
        hook.run_for_lane(
            lane="provider-ish",  # type: ignore[arg-type]
            now_monotonic=10.0,
        )

    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None


def test_nonfinite_monotonic_fails_before_wal_cycle(tmp_path: Path) -> None:
    hook, orchestrator = _hook(tmp_path)

    with pytest.raises(WalMaintenanceError):
        hook.run_for_lane(
            lane=SchedulerLane.CONTROL,
            now_monotonic=float("nan"),
        )

    assert orchestrator.calls == 0
    assert hook.scheduler.runner.next_due_monotonic is None


def test_hook_factory_composes_exact_runtime_identity_chain(tmp_path: Path) -> None:
    database = _database(tmp_path)

    hook = build_wal_job_scheduler_hook(
        database,
        interval_seconds=60.0,
    )

    runner = hook.scheduler.runner
    orchestrator = runner.orchestrator
    assert orchestrator.service.database is database
    assert hook.scheduler.runner is runner
    assert runner.orchestrator is orchestrator


def test_hook_factory_construction_has_no_database_or_wal_side_effect(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path)

    build_wal_job_scheduler_hook(
        database,
        interval_seconds=60.0,
    )

    assert not database.path.exists()
    assert not database.path.with_name(f"{database.path.name}-wal").exists()


@pytest.mark.parametrize("interval_seconds", [True, False])
def test_hook_factory_rejects_boolean_interval_before_database_side_effect(
    tmp_path: Path,
    interval_seconds: object,
) -> None:
    database = _database(tmp_path)

    with pytest.raises(WalMaintenanceError):
        build_wal_job_scheduler_hook(
            database,
            interval_seconds=cast(float, interval_seconds),
        )

    assert not database.path.exists()


def test_scheduler_tick_boundary_runs_control_housekeeping_before_scheduler(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler = object.__new__(DurableJobScheduler)
    scheduler_calls: list[tuple[str, int | None, SchedulerLane]] = []
    scheduler_result = cast(SchedulerTickResult, object())

    def durable_tick(
        _self: DurableJobScheduler,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        scheduler_calls.append((worker_id, now_us, lane))
        return scheduler_result

    monkeypatch.setattr(DurableJobScheduler, "tick", durable_tick)

    result = run_scheduler_tick_with_wal_housekeeping(
        scheduler,
        hook,
        worker_id="control-1",
        lane=SchedulerLane.CONTROL,
        now_us=123,
        now_monotonic=10.0,
    )

    assert result is scheduler_result
    assert orchestrator.calls == 1
    assert scheduler_calls == [("control-1", 123, SchedulerLane.CONTROL)]


def test_scheduler_tick_boundary_keeps_provider_lane_wal_side_effect_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler = object.__new__(DurableJobScheduler)
    scheduler_calls: list[tuple[str, int | None, SchedulerLane]] = []
    scheduler_result = cast(SchedulerTickResult, object())

    def durable_tick(
        _self: DurableJobScheduler,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        scheduler_calls.append((worker_id, now_us, lane))
        return scheduler_result

    monkeypatch.setattr(DurableJobScheduler, "tick", durable_tick)

    result = run_scheduler_tick_with_wal_housekeeping(
        scheduler,
        hook,
        worker_id="provider-1",
        lane=SchedulerLane.PROVIDER,
        now_us=456,
        now_monotonic=10.0,
    )

    assert result is scheduler_result
    assert orchestrator.calls == 0
    assert scheduler_calls == [("provider-1", 456, SchedulerLane.PROVIDER)]


def test_scheduler_tick_boundary_rejects_invalid_lane_before_scheduler_or_wal(
    tmp_path: Path,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler_impl = _StubDurableScheduler()
    scheduler = cast(DurableJobScheduler, scheduler_impl)

    with pytest.raises(ValueError):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            hook,
            worker_id="bad-lane",
            lane="provider-ish",  # type: ignore[arg-type]
            now_us=789,
            now_monotonic=10.0,
        )

    assert orchestrator.calls == 0
    assert scheduler_impl.calls == []


def test_scheduler_tick_boundary_rejects_blank_worker_before_wal(
    tmp_path: Path,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler_impl = _StubDurableScheduler()
    scheduler = cast(DurableJobScheduler, scheduler_impl)

    with pytest.raises(ValueError, match="worker_id must not be empty"):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            hook,
            worker_id="   ",
            lane=SchedulerLane.CONTROL,
            now_us=789,
            now_monotonic=10.0,
        )

    assert orchestrator.calls == 0
    assert scheduler_impl.calls == []


def test_wal_aware_scheduler_inherits_existing_run_loop_and_ticks_through_wal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler = object.__new__(WalAwareDurableJobScheduler)
    scheduler.policy = SchedulerPolicy(idle_poll_seconds=0.001)
    scheduler.bind_wal_housekeeping(hook)
    durable_calls: list[tuple[str, int | None, SchedulerLane]] = []

    def durable_tick(
        _self: DurableJobScheduler,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        durable_calls.append((worker_id, now_us, lane))
        return _idle_tick_result()

    monkeypatch.setattr(DurableJobScheduler, "tick", durable_tick)

    result = scheduler.run_loop(
        worker_id="control-loop",
        max_ticks=1,
        lane=SchedulerLane.CONTROL,
    )

    assert WalAwareDurableJobScheduler.run_loop is DurableJobScheduler.run_loop
    assert result.ticks == 1
    assert result.idle is True
    assert orchestrator.calls == 1
    assert durable_calls == [("control-loop", None, SchedulerLane.CONTROL)]


def test_wal_aware_scheduler_provider_loop_remains_wal_side_effect_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hook, orchestrator = _hook(tmp_path)
    scheduler = object.__new__(WalAwareDurableJobScheduler)
    scheduler.policy = SchedulerPolicy(idle_poll_seconds=0.001)
    scheduler.bind_wal_housekeeping(hook)

    monkeypatch.setattr(
        DurableJobScheduler,
        "tick",
        lambda _self, *, worker_id, now_us=None, lane=SchedulerLane.ALL: _idle_tick_result(),
    )

    result = scheduler.run_loop(
        worker_id="provider-loop",
        max_ticks=1,
        lane=SchedulerLane.PROVIDER,
    )

    assert result.ticks == 1
    assert result.idle is True
    assert orchestrator.calls == 0


def test_wal_aware_scheduler_requires_binding_before_durable_tick(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scheduler = object.__new__(WalAwareDurableJobScheduler)
    durable_calls = 0

    def durable_tick(
        _self: DurableJobScheduler,
        *,
        worker_id: str,
        now_us: int | None = None,
        lane: SchedulerLane = SchedulerLane.ALL,
    ) -> SchedulerTickResult:
        nonlocal durable_calls
        del worker_id, now_us, lane
        durable_calls += 1
        return _idle_tick_result()

    monkeypatch.setattr(DurableJobScheduler, "tick", durable_tick)

    with pytest.raises(RuntimeError, match="requires housekeeping binding"):
        scheduler.tick(worker_id="control", lane=SchedulerLane.CONTROL)

    assert durable_calls == 0
