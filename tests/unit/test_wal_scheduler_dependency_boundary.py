from __future__ import annotations

from typing import Any, cast

import pytest

from athena.jobs.scheduler import DurableJobScheduler
from athena.storage.wal_job_hook import (
    WalJobSchedulerHook,
    run_scheduler_tick_with_wal_housekeeping,
)


class _ExplodingHook(WalJobSchedulerHook):
    def run_for_lane(self, **kwargs: Any) -> None:  # type: ignore[override]
        del kwargs
        raise AssertionError("WAL hook must not run before scheduler validation")


class _ExplodingScheduler:
    def tick(self, **kwargs: Any) -> None:
        del kwargs
        raise AssertionError("scheduler must not run before hook validation")


def test_invalid_scheduler_fails_before_wal_hook_side_effect() -> None:
    hook = object.__new__(_ExplodingHook)

    with pytest.raises(TypeError, match="callable scheduler tick"):
        run_scheduler_tick_with_wal_housekeeping(
            cast(DurableJobScheduler, object()),
            hook,
            worker_id="control-1",
        )


def test_invalid_hook_fails_before_scheduler_dispatch() -> None:
    scheduler = cast(DurableJobScheduler, _ExplodingScheduler())

    with pytest.raises(TypeError, match="requires WalJobSchedulerHook"):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            cast(WalJobSchedulerHook, object()),
            worker_id="control-1",
        )
