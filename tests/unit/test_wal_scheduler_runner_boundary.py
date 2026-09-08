from __future__ import annotations

import pytest

from athena.storage.wal_schedule import WalMaintenanceIntervalRunner
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class _ForeignWalMaintenanceIntervalRunner(WalMaintenanceIntervalRunner):
    @property
    def orchestrator(self):  # type: ignore[override]
        raise AssertionError("foreign runner state must not be accessed")

    @orchestrator.setter
    def orchestrator(self, value):  # type: ignore[override]
        raise AssertionError("foreign runner state must not be assigned")


def test_scheduler_adapter_rejects_foreign_runner_before_state_access() -> None:
    runner = object.__new__(_ForeignWalMaintenanceIntervalRunner)

    with pytest.raises(
        TypeError,
        match="requires canonical WalMaintenanceIntervalRunner",
    ):
        WalMaintenanceSchedulerAdapter(runner)
