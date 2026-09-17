from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from athena.jobs.scheduler import (
    DurableJobScheduler,
    SchedulerLane,
    SchedulerTickResult,
)
from athena.jobs.wal_maintenance_scheduler import WalMaintainedDurableJobScheduler
from athena.storage.wal_maintenance import WalMaintenanceError
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


def _result() -> SchedulerTickResult:
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


def _scheduler(
    wal_maintenance: WalMaintenanceSchedulerAdapter,
) -> WalMaintainedDurableJobScheduler:
    return WalMaintainedDurableJobScheduler(
        jobs=Mock(),
        source_worker=Mock(),
        embedding_worker=Mock(),
        wal_maintenance=wal_maintenance,
    )


@pytest.mark.parametrize("lane", [SchedulerLane.ALL, SchedulerLane.CONTROL])
def test_control_owned_tick_runs_wal_housekeeping_before_dispatch(lane: SchedulerLane) -> None:
    wal_maintenance = Mock(spec=WalMaintenanceSchedulerAdapter)
    scheduler = _scheduler(wal_maintenance)
    expected = _result()

    with patch.object(DurableJobScheduler, "tick", return_value=expected) as base_tick:
        result = scheduler.tick(worker_id="control-1", now_us=123, lane=lane)

    assert result is expected
    wal_maintenance.run_control_housekeeping.assert_called_once_with()
    base_tick.assert_called_once_with(
        worker_id="control-1",
        now_us=123,
        lane=lane,
    )


def test_provider_tick_never_touches_wal_housekeeping() -> None:
    wal_maintenance = Mock(spec=WalMaintenanceSchedulerAdapter)
    scheduler = _scheduler(wal_maintenance)
    expected = _result()

    with patch.object(DurableJobScheduler, "tick", return_value=expected) as base_tick:
        result = scheduler.tick(
            worker_id="provider-1",
            now_us=456,
            lane=SchedulerLane.PROVIDER,
        )

    assert result is expected
    wal_maintenance.run_control_housekeeping.assert_not_called()
    base_tick.assert_called_once_with(
        worker_id="provider-1",
        now_us=456,
        lane=SchedulerLane.PROVIDER,
    )


def test_wal_failure_fails_closed_before_scheduler_dispatch() -> None:
    wal_maintenance = Mock(spec=WalMaintenanceSchedulerAdapter)
    wal_maintenance.run_control_housekeeping.side_effect = WalMaintenanceError("boom")
    scheduler = _scheduler(wal_maintenance)

    with patch.object(DurableJobScheduler, "tick") as base_tick:
        with pytest.raises(WalMaintenanceError, match="boom"):
            scheduler.tick(worker_id="control-1", lane=SchedulerLane.CONTROL)

    base_tick.assert_not_called()


def test_constructor_rejects_non_adapter_dependency() -> None:
    with pytest.raises(TypeError, match="WalMaintenanceSchedulerAdapter"):
        WalMaintainedDurableJobScheduler(
            jobs=Mock(),
            source_worker=Mock(),
            embedding_worker=Mock(),
            wal_maintenance=object(),  # type: ignore[arg-type]
        )
