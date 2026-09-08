from __future__ import annotations

import pytest

from athena.storage.wal_maintenance import WalMaintenanceOrchestrator
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


class _ForeignWalMaintenanceOrchestrator(WalMaintenanceOrchestrator):
    def __getattribute__(self, name: str):
        if name != "__class__":
            raise AssertionError("foreign orchestrator state must not be accessed")
        return super().__getattribute__(name)


def test_interval_runner_rejects_foreign_orchestrator_before_state_access() -> None:
    orchestrator = object.__new__(_ForeignWalMaintenanceOrchestrator)

    with pytest.raises(
        TypeError,
        match="requires canonical WalMaintenanceOrchestrator",
    ):
        WalMaintenanceIntervalRunner(orchestrator, interval_seconds=60.0)
