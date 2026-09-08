from dataclasses import replace

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceOrchestrator, WalMaintenanceService
from athena.storage.wal_runtime import build_wal_maintenance_runtime
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner
from athena.storage.wal_scheduler import WalMaintenanceSchedulerAdapter


class ForeignService(WalMaintenanceService):
    pass


class ForeignOrchestrator(WalMaintenanceOrchestrator):
    pass


class ForeignRunner(WalMaintenanceIntervalRunner):
    pass


class ForeignScheduler(WalMaintenanceSchedulerAdapter):
    pass


def test_wal_runtime_rejects_foreign_component_subclasses_before_state_access(tmp_path):
    runtime = build_wal_maintenance_runtime(
        SQLiteDatabase(tmp_path / "athena.db"),
        interval_seconds=60.0,
    )

    cases = (
        ("service", object.__new__(ForeignService), "canonical WalMaintenanceService"),
        (
            "orchestrator",
            object.__new__(ForeignOrchestrator),
            "canonical WalMaintenanceOrchestrator",
        ),
        (
            "runner",
            object.__new__(ForeignRunner),
            "canonical WalMaintenanceIntervalRunner",
        ),
        (
            "scheduler",
            object.__new__(ForeignScheduler),
            "canonical WalMaintenanceSchedulerAdapter",
        ),
    )

    for field_name, foreign_component, message in cases:
        with pytest.raises(TypeError, match=message):
            replace(runtime, **{field_name: foreign_component})
