from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

from athena.storage.bootstrap import StorageBootstrapService
from athena.storage.database import SQLiteDatabase
from athena.storage.disk_pressure import DiskPressureController
from athena.storage.emergency_reserve import EmergencyReserveStatus
from athena.storage.migration_coordinator import MigrationCoordinatorResult
from athena.storage.paths import RuntimePaths
from athena.storage.recovery import (
    DatabaseFileSetIdentity,
    DatabasePreflightReport,
    DatabaseStartupIdentityChangedError,
    capture_database_file_set_identity,
    inspect_database_read_only,
)
from athena.storage.schema_contract import SCHEMA_VERSION

_GIB = 1024 * 1024 * 1024


@dataclass
class _ReserveStub:
    ensure_calls: int = 0

    def ensure(
        self,
        *,
        required_bytes: int,
        write_chunk_bytes: int,
    ) -> EmergencyReserveStatus:
        self.ensure_calls += 1
        return EmergencyReserveStatus(
            path=Path.cwd() / "bootstrap-identity-emergency.reserve",
            required_bytes=required_bytes,
            file_size_bytes=required_bytes,
            allocated_bytes=required_bytes,
        )

    def release(self) -> int:
        return 0


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


def _controller(paths: RuntimePaths) -> DiskPressureController:
    return DiskPressureController(
        paths.state_root,
        reserve_store=_ReserveStub(),  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 20 * _GIB),
    )


def _create_current_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    database = SQLiteDatabase(path)
    database.start()
    database.stop()


def _create_legacy_database(path: Path) -> None:
    _create_current_database(path)
    connection = sqlite3.connect(path, autocommit=True)
    try:
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION - 1}")
    finally:
        connection.close()


def _remove_sidecars(path: Path) -> None:
    for sidecar in (
        path.with_name(f"{path.name}-wal"),
        path.with_name(f"{path.name}-shm"),
    ):
        sidecar.unlink(missing_ok=True)


def _replace_with_current_database(source: Path, replacement: Path) -> None:
    _create_current_database(replacement)
    _remove_sidecars(source)
    _remove_sidecars(replacement)
    os.replace(replacement, source)


def test_bootstrap_repreflights_activated_database_before_writer_start(
    tmp_path: Path,
) -> None:
    paths = _paths(tmp_path)
    _create_legacy_database(paths.database_path)
    original = inspect_database_read_only(paths.database_path).file_set_identity
    assert original is not None
    observed: dict[str, DatabaseFileSetIdentity] = {}

    def runner(**kwargs: Any) -> MigrationCoordinatorResult:
        source = kwargs["source_db"]
        assert isinstance(source, Path)
        replacement = paths.state_root / "activated-current.db"
        _replace_with_current_database(source, replacement)
        observed["activated_identity"] = capture_database_file_set_identity(source)
        return cast(MigrationCoordinatorResult, object())

    database = SQLiteDatabase(paths.database_path)
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=_controller(paths),
        migration_runner=runner,
    )

    service.start()
    try:
        assert service.migration_plan is not None
        assert service.migration_plan.migration_required is True
        assert service.preflight is not None
        assert service.preflight.schema_version == SCHEMA_VERSION
        assert service.preflight.file_set_identity is not None
        assert (
            service.preflight.file_set_identity.database
            == observed["activated_identity"].database
        )
        assert service.preflight.file_set_identity.database != original.database
        assert database.connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        service.stop()


class _ReplaceAfterBindDatabase(SQLiteDatabase):
    def __init__(self, path: Path, replacement: Path) -> None:
        super().__init__(path)
        self.replacement = replacement
        self.bound_preflight: DatabasePreflightReport | None = None

    def bind_startup_preflight(self, preflight: DatabasePreflightReport) -> None:
        super().bind_startup_preflight(preflight)
        self.bound_preflight = preflight
        _remove_sidecars(self.path)
        _remove_sidecars(self.replacement)
        os.replace(self.replacement, self.path)


def test_bootstrap_rejects_replacement_after_post_migration_preflight(
    tmp_path: Path,
) -> None:
    paths = _paths(tmp_path)
    _create_legacy_database(paths.database_path)
    post_bind_replacement = paths.state_root / "post-bind-replacement.db"
    _create_current_database(post_bind_replacement)

    def runner(**kwargs: Any) -> MigrationCoordinatorResult:
        source = kwargs["source_db"]
        assert isinstance(source, Path)
        activated = paths.state_root / "activated-before-race.db"
        _replace_with_current_database(source, activated)
        return cast(MigrationCoordinatorResult, object())

    database = _ReplaceAfterBindDatabase(
        paths.database_path,
        post_bind_replacement,
    )
    service = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=_controller(paths),
        migration_runner=runner,
    )

    try:
        with pytest.raises(DatabaseStartupIdentityChangedError, match="identity changed"):
            service.start()
        assert database.bound_preflight is not None
        assert database.bound_preflight.file_set_identity is not None
        assert service.preflight is None
    finally:
        database.stop()
        service.layout.stop()
