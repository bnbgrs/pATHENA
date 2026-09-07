from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceError
from athena.storage.wal_runtime import build_wal_maintenance_runtime


def _database(tmp_path: Path) -> SQLiteDatabase:
    return SQLiteDatabase((tmp_path / "athena.db").resolve())


def test_wal_runtime_composes_one_identity_chain(tmp_path: Path) -> None:
    database = _database(tmp_path)

    runtime = build_wal_maintenance_runtime(
        database,
        interval_seconds=60.0,
    )

    assert runtime.service.database is database
    assert runtime.orchestrator.service is runtime.service
    assert runtime.runner.orchestrator is runtime.orchestrator
    assert runtime.scheduler.runner is runtime.runner


def test_wal_runtime_construction_has_no_database_side_effect(tmp_path: Path) -> None:
    database = _database(tmp_path)

    build_wal_maintenance_runtime(
        database,
        interval_seconds=60.0,
    )

    assert not database.path.exists()
    assert not database.path.with_name(f"{database.path.name}-wal").exists()


@pytest.mark.parametrize("interval_seconds", [True, False])
def test_wal_runtime_rejects_boolean_interval_before_database_side_effect(
    tmp_path: Path,
    interval_seconds: object,
) -> None:
    database = _database(tmp_path)

    with pytest.raises(WalMaintenanceError):
        build_wal_maintenance_runtime(
            database,
            interval_seconds=interval_seconds,  # type: ignore[arg-type]
        )

    assert not database.path.exists()
