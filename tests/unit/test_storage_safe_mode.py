from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.disk_pressure import DiskPressureController
from athena.storage.safe_mode import StorageSafeModeError, StorageSafeModeService

_GIB = 1024 * 1024 * 1024


@dataclass
class _ReserveStub:
    released_bytes: int
    calls: int = 0

    def release(self) -> int:
        self.calls += 1
        return self.released_bytes


def _create_database(path: Path) -> None:
    database = SQLiteDatabase(path)
    database.start()
    database.stop()


def test_safe_mode_releases_reserve_and_opens_database_read_only(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    database_path = state_root / "athena.db"
    _create_database(database_path)
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    readings = iter([(100 * _GIB, 1 * _GIB), (100 * _GIB, 2 * _GIB)])
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: next(readings),
    )
    service = StorageSafeModeService(
        database_path=database_path,
        disk_pressure=controller,
    )

    service.start()
    try:
        assert service.status is not None
        assert service.status.reserve_released_bytes == 1 * _GIB
        assert reserve.calls == 1
        row = service.database.connection.execute("PRAGMA query_only").fetchone()
        assert row is not None
        assert int(row[0]) == 1
        with pytest.raises(sqlite3.OperationalError):
            service.database.connection.execute("CREATE TABLE forbidden (id INTEGER)")
    finally:
        service.stop()


def test_safe_mode_refuses_non_emergency_start(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    database_path = state_root / "athena.db"
    _create_database(database_path)
    controller = DiskPressureController(
        state_root,
        disk_usage_provider=lambda _path: (100 * _GIB, 4 * _GIB),
    )
    service = StorageSafeModeService(
        database_path=database_path,
        disk_pressure=controller,
    )

    with pytest.raises(StorageSafeModeError, match="reserved for EMERGENCY"):
        service.start()

    assert service.status is None


def test_safe_mode_does_not_require_reserve_to_exist(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    database_path = state_root / "athena.db"
    _create_database(database_path)
    reserve = _ReserveStub(released_bytes=0)
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 1 * _GIB),
    )
    service = StorageSafeModeService(
        database_path=database_path,
        disk_pressure=controller,
    )

    service.start()
    try:
        assert service.status is not None
        assert service.status.reserve_released_bytes == 0
        assert reserve.calls == 1
    finally:
        service.stop()
