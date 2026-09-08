from __future__ import annotations

import pytest

from athena.storage.wal_job_hook import WalJobSchedulerHook
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class _ForeignWalSchedulerAdapter(WalMaintenanceSchedulerAdapter):
    pass


def test_wal_hook_rejects_noncanonical_scheduler_adapter_before_access() -> None:
    foreign_adapter = object.__new__(_ForeignWalSchedulerAdapter)

    with pytest.raises(
        TypeError,
        match="canonical WalMaintenanceSchedulerAdapter",
    ):
        WalJobSchedulerHook(foreign_adapter)
