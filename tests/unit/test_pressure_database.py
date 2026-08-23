from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.disk_pressure import (
    DiskPressureController,
    DiskPressureWriteBlockedError,
)
from athena.storage.pressure_database import PressureGuardedSQLiteDatabase

_GIB = 1024 * 1024 * 1024


def _database(tmp_path: Path, *, free_bytes: int) -> PressureGuardedSQLiteDatabase:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    controller = DiskPressureController(
        state_root,
        disk_usage_provider=lambda _path: (100 * _GIB, free_bytes),
    )
    database = PressureGuardedSQLiteDatabase(
        state_root / "athena.db",
        disk_pressure=controller,
    )
    database.start()
    return database


def test_pressure_database_allows_noncritical_write_outside_emergency(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path, free_bytes=4 * _GIB)
    try:
        with database.write_transaction() as connection:
            connection.execute("CREATE TEMP TABLE pressure_test (value INTEGER)")
            connection.execute("INSERT INTO pressure_test VALUES (1)")

        assert database.connection.execute(
            "SELECT value FROM pressure_test"
        ).fetchall() == [(1,)]
    finally:
        database.stop()


def test_pressure_database_blocks_noncritical_write_before_transaction_begins(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path, free_bytes=1 * _GIB)
    try:
        assert database.connection.in_transaction is False
        with pytest.raises(DiskPressureWriteBlockedError, match="EMERGENCY"):
            with database.write_transaction():
                raise AssertionError("unreachable")
        assert database.connection.in_transaction is False
    finally:
        database.stop()


def test_pressure_database_allows_explicit_critical_recovery_write_in_emergency(
    tmp_path: Path,
) -> None:
    database = _database(tmp_path, free_bytes=1 * _GIB)
    try:
        with database.critical_write_transaction() as connection:
            connection.execute("CREATE TEMP TABLE recovery_test (value INTEGER)")
            connection.execute("INSERT INTO recovery_test VALUES (7)")

        assert database.connection.execute(
            "SELECT value FROM recovery_test"
        ).fetchall() == [(7,)]
    finally:
        database.stop()
