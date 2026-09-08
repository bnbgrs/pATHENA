from __future__ import annotations

from typing import Any, cast

import pytest

from athena.storage.wal_job_hook import (
    WalAwareDurableJobScheduler,
    run_scheduler_tick_with_wal_housekeeping,
)


def test_wrapper_rejects_non_text_worker_id_before_any_dependency_access() -> None:
    scheduler = cast(Any, object())
    hook = cast(Any, object())

    with pytest.raises(TypeError, match="worker_id must be text"):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            hook,
            worker_id=cast(Any, 7),
        )


def test_wal_aware_scheduler_rejects_non_text_worker_id_before_hook_access() -> None:
    scheduler = object.__new__(WalAwareDurableJobScheduler)

    with pytest.raises(TypeError, match="worker_id must be text"):
        scheduler.tick(worker_id=cast(Any, 7))
