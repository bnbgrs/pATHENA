from __future__ import annotations

import pytest

from athena.jobs.scheduler import DurableJobScheduler
from athena.storage.wal_job_hook import run_scheduler_tick_with_wal_housekeeping


class _ExplosiveScheduler(DurableJobScheduler):
    @property
    def tick(self) -> object:  # type: ignore[override]
        raise AssertionError("scheduler tick attribute must not be accessed")


def test_noncanonical_scheduler_fails_before_dependency_access() -> None:
    scheduler = object.__new__(_ExplosiveScheduler)

    with pytest.raises(
        TypeError,
        match="canonical DurableJobScheduler",
    ):
        run_scheduler_tick_with_wal_housekeeping(
            scheduler,
            object(),  # type: ignore[arg-type]
            worker_id="control-worker",
        )
