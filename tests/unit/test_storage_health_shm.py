from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.health as health_module
from athena.storage.database import SQLiteDatabase
from athena.storage.health import StorageHealthService, StorageHealthSnapshot


def test_storage_health_reports_sqlite_shm_size(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.sqlite3")
    database.start()
    try:
        snapshot = StorageHealthService(database).snapshot()
    finally:
        database.stop()

    assert snapshot.status == "available"
    assert snapshot.shm_size_bytes is not None
    assert snapshot.shm_size_bytes >= 0


def test_storage_health_shm_probe_failure_does_not_expose_partial_sizes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.sqlite3")
    database.start()
    original_file_size = health_module._file_size

    def deny_shm_size(path: Path) -> int:
        if path.name.endswith("-shm"):
            raise PermissionError("private shm detail")
        return original_file_size(path)

    monkeypatch.setattr(health_module, "_file_size", deny_shm_size)
    try:
        snapshot = StorageHealthService(database).snapshot()
    finally:
        database.stop()

    assert snapshot.status == "error"
    assert snapshot.database_size_bytes is None
    assert snapshot.wal_size_bytes is None
    assert snapshot.shm_size_bytes is None
    assert snapshot.detail == "Storage telemetry read failed: PermissionError."
    assert "private shm detail" not in snapshot.detail


def test_storage_health_snapshot_rejects_negative_shm_size() -> None:
    with pytest.raises(ValueError, match="SHM size cannot be negative"):
        StorageHealthSnapshot(
            status="available",
            database_open=True,
            database_path="athena.sqlite3",
            database_size_bytes=1,
            wal_size_bytes=0,
            shm_size_bytes=-1,
            observed_at_us=1,
            detail=None,
        )
