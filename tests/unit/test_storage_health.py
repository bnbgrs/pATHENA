from __future__ import annotations

from pathlib import Path

import pytest

import athena.storage.health as health_module
from athena.storage.database import SQLiteDatabase
from athena.storage.health import StorageHealthService, StorageHealthSnapshot


def test_storage_health_reports_unavailable_before_database_start(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.sqlite3")

    snapshot = StorageHealthService(database).snapshot()

    assert snapshot.status == "unavailable"
    assert snapshot.database_open is False
    assert snapshot.database_path == str(database.path)
    assert snapshot.database_size_bytes is None
    assert snapshot.wal_size_bytes is None
    assert snapshot.detail == "SQLite database service is not started."
    assert snapshot.observed_at_us > 0


def test_storage_health_reports_measured_available_state(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.sqlite3")
    database.start()
    try:
        snapshot = StorageHealthService(database).snapshot()
    finally:
        database.stop()

    assert snapshot.status == "available"
    assert snapshot.database_open is True
    assert snapshot.database_path == str(database.path)
    assert snapshot.database_size_bytes is not None
    assert snapshot.database_size_bytes > 0
    assert snapshot.wal_size_bytes is not None
    assert snapshot.wal_size_bytes >= 0
    assert snapshot.detail is None
    assert snapshot.observed_at_us > 0


def test_storage_health_reports_safe_error_without_invented_sizes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.sqlite3")
    database.start()

    def deny_size(_path: Path) -> int:
        raise PermissionError("secret filesystem detail")

    monkeypatch.setattr(health_module, "_file_size", deny_size)
    try:
        snapshot = StorageHealthService(database).snapshot()
    finally:
        database.stop()

    assert snapshot.status == "error"
    assert snapshot.database_open is True
    assert snapshot.database_path == str(database.path)
    assert snapshot.database_size_bytes is None
    assert snapshot.wal_size_bytes is None
    assert snapshot.detail == "Storage telemetry read failed: PermissionError."
    assert "secret filesystem detail" not in snapshot.detail


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "status": "available",
                "database_open": False,
                "database_path": "athena.sqlite3",
                "database_size_bytes": 1,
                "wal_size_bytes": 0,
                "observed_at_us": 1,
                "detail": None,
            },
            "open database",
        ),
        (
            {
                "status": "unavailable",
                "database_open": False,
                "database_path": "athena.sqlite3",
                "database_size_bytes": 1,
                "wal_size_bytes": None,
                "observed_at_us": 1,
                "detail": "not started",
            },
            "partial measured sizes",
        ),
        (
            {
                "status": "error",
                "database_open": False,
                "database_path": "athena.sqlite3",
                "database_size_bytes": None,
                "wal_size_bytes": None,
                "observed_at_us": 1,
                "detail": "probe failed",
            },
            "live database boundary",
        ),
        (
            {
                "status": "available",
                "database_open": True,
                "database_path": "athena.sqlite3",
                "database_size_bytes": -1,
                "wal_size_bytes": 0,
                "observed_at_us": 1,
                "detail": None,
            },
            "cannot be negative",
        ),
    ],
)
def test_storage_health_snapshot_rejects_contradictory_or_invented_facts(
    kwargs: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        StorageHealthSnapshot(**kwargs)  # type: ignore[arg-type]