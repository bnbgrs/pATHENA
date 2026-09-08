from __future__ import annotations

from typing import Any, cast

import pytest

from athena.jobs.scheduler import DurableJobScheduler
from athena.storage.wal_job_hook import (
    WalJobSchedulerHook,
    run_scheduler_tick_with_wal_housekeeping,
)


def _canonical_scheduler() -> DurableJobScheduler:
    return DurableJobScheduler(
        jobs=cast(Any, object()),
        source_worker=cast(Any, object()),
        embedding_worker=cast(Any, object()),
    )


def test_invalid_scheduler_fails_before_wal_hook_side_effect() -> None:
    hook = cast(WalJobSchedulerHook, object())

    with pytest.raises(
        TypeError,
        match="requires the canonical DurableJobScheduler",
    ):
        run_scheduler_tick_with_wal_housekeeping(
            cast(DurableJobScheduler, object()),
            hook,
            worker_id="control-1",
        )


def test_invalid_hook_fails_before_scheduler_dispatch() -> None:
    scheduler = _canonical_scheduler()

    with pytest.raises(TypeError, match="requires canonical WalJobSchedulerHook"):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            cast(WalJobSchedulerHook, object()),
            worker_id="control-1",
        )
