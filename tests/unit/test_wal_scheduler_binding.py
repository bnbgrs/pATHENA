from __future__ import annotations

import pytest

from athena.storage.wal_job_hook import WalAwareDurableJobScheduler, WalJobSchedulerHook


def test_wal_housekeeping_binding_is_single_assignment() -> None:
    scheduler = object.__new__(WalAwareDurableJobScheduler)
    first_hook = object.__new__(WalJobSchedulerHook)
    replacement_hook = object.__new__(WalJobSchedulerHook)

    scheduler.bind_wal_housekeeping(first_hook)

    with pytest.raises(RuntimeError, match="already bound"):
        scheduler.bind_wal_housekeeping(replacement_hook)

    assert scheduler._wal_housekeeping_hook is first_hook
