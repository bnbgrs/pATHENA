from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

from athena.storage.bootstrap import (
    StorageBootstrapReadOnlyRequiredError,
    StorageBootstrapRecoveryRequiredError,
    StorageBootstrapService,
)
from athena.storage.database import SQLiteDatabase
from athena.storage.disk_pressure import (
    DiskPressureController,
    DiskPressureWriteBlockedError,
)
from athena.storage.emergency_reserve import EmergencyReserveStatus
from athena.storage.migration_coordinator import MigrationCoordinatorResult
from athena.storage.migration_journal import (
    MigrationJournalState,
    MigrationJournalStore,
    MigrationPhase,
)
from athena.storage.paths import RuntimePaths
from athena.storage.schema_contract import SCHEMA_VERSION

_GIB = 1024 * 1024 * 1024


@dataclass
class _ReserveStub:
    ensure_calls: int = 0
    release_calls: int = 0
    released_bytes: int = 0

    def ensure(
        self,
        *,
        required_bytes: int,
        write_chunk_bytes: int,
    ) -> EmergencyReserveStatus:
        self.ensure_calls += 1
        return EmergencyReserveStatus(
            path=Path("/tmp/bootstrap-emergency.reserve"),
            required_bytes=required_bytes,
            file_size_bytes=required_bytes,
            allocated_bytes=required_bytes,
        )

    def release(self) -> int:
        self.release_calls += 1
        return self.released_bytes


class _RecordingDatabase(SQLiteDatabase):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.start_calls += 1

    def stop(self) -> None:
        self.stop_calls += 1


def _paths(tmp_path: Path) -> RuntimePaths:
    local = (tmp_path / "local").absolute()
    state = local / "state"
    return RuntimePaths(
        local_root=local,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=state / "spool",
        derived_root=local / "derived",
        log_root=local / "logs",
        temp_root=local / "tmp",
        archive_root=None,
        backup_root=None,
        projection_root=None,
    )


def _create_current_database(paths: RuntimePaths) -> None:
    paths.state_root.mkdir(parents=True, exist_ok=True)
    database = SQLiteDatabase(paths.database_path)
    database.start()
    database.stop()


def test_bootstrap_current_database_orders_reserve_before_database_start(
    tmp_path: Path,
) -> None:
    paths = _paths(tmp_path)
    _create_current_database(paths)
    reserve = _ReserveStub()
    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 20 * _GIB),
    )
    database = _RecordingDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
    )

    service.start()

    assert reserve.ensure_calls == 1
    assert database.start_calls == 1
    assert service.migration_plan is not None
    assert service.migration_plan.migration_required is False
    assert service.recovery is not None
    assert service.recovery.requires_manual_review is False
    assert service.reserve is not None
    assert service.reserve.provisioned is True
    assert (paths.state_root / "migration").is_dir()

    service.stop()
    assert database.stop_calls == 1


def test_bootstrap_emergency_refuses_writable_database_start(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    reserve = _ReserveStub()
    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 1 * _GIB),
    )
    database = _RecordingDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
    )

    with pytest.raises(StorageBootstrapReadOnlyRequiredError, match="EMERGENCY"):
        service.start()

    assert reserve.ensure_calls == 0
    assert database.start_calls == 0
    assert not paths.database_path.exists()


def test_bootstrap_rechecks_pressure_before_live_writer_start(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    _create_current_database(paths)
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    free_values = iter((20 * _GIB, 1 * _GIB, 3 * _GIB))

    def usage(_path: Path) -> tuple[int, int]:
        return 100 * _GIB, next(free_values)

    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=usage,
    )
    database = _RecordingDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
    )

    with pytest.raises(StorageBootstrapReadOnlyRequiredError, match="EMERGENCY"):
        service.start()

    assert reserve.ensure_calls == 1
    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True
    assert database.start_calls == 0


def test_bootstrap_recovery_blocks_before_reserve_or_database(tmp_path: Path) -> None:
    paths = _paths(tmp_path)
    _create_current_database(paths)
    migration_root = paths.state_root / "migration"
    migration_root.mkdir()
    candidate = migration_root / "candidate.db"
    candidate.write_bytes(b"candidate")
    MigrationJournalStore(migration_root / "migration_state.json").publish(
        MigrationJournalState(
            migration_id="schema-v1-to-v2",
            phase=MigrationPhase.MIGRATING,
            source_db=paths.database_path,
            candidate_db=candidate,
            started_at_us=1,
            last_completed_step="clone_complete",
        )
    )
    reserve = _ReserveStub()
    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 20 * _GIB),
    )
    database = _RecordingDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
    )

    with pytest.raises(StorageBootstrapRecoveryRequiredError, match="recovery review"):
        service.start()

    assert reserve.ensure_calls == 0
    assert database.start_calls == 0


def test_bootstrap_legacy_database_passes_real_reserve_requirement_to_runner(
    tmp_path: Path,
) -> None:
    paths = _paths(tmp_path)
    _create_current_database(paths)
    connection = sqlite3.connect(paths.database_path, autocommit=True)
    try:
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION - 1}")
    finally:
        connection.close()

    reserve = _ReserveStub()
    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 20 * _GIB),
    )
    database = _RecordingDatabase(paths.database_path)
    observed: dict[str, Any] = {}

    def runner(**kwargs: Any) -> MigrationCoordinatorResult:
        observed.update(kwargs)
        return cast(MigrationCoordinatorResult, object())

    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
        migration_runner=runner,
    )

    service.start()

    assert service.migration_plan is not None
    assert service.migration_plan.migration_required is True
    assert observed["source_db"] == paths.database_path
    assert observed["migration_root"] == paths.state_root / "migration"
    assert observed["emergency_reserve_bytes"] == 1 * _GIB
    assert callable(observed["executor"])
    assert database.start_calls == 1


def test_bootstrap_binds_runtime_disk_pressure_gate_to_real_database(
    tmp_path: Path,
) -> None:
    paths = _paths(tmp_path)
    _create_current_database(paths)
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    free_bytes = 20 * _GIB

    def usage(_path: Path) -> tuple[int, int]:
        return 100 * _GIB, free_bytes

    controller = DiskPressureController(
        paths.state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=usage,
    )
    database = SQLiteDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=controller,
    )
    service.start()

    free_bytes = 1 * _GIB
    with pytest.raises(DiskPressureWriteBlockedError, match="EMERGENCY"):
        with database.write_transaction():
            raise AssertionError("runtime write must be blocked before BEGIN IMMEDIATE")

    assert database.connection.in_transaction is False
    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True
    service.stop()
