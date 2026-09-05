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
                "status": "bogus",
                "database_open": True,
                "database_path": "athena.sqlite3",
                "database_size_bytes": None,
                "wal_size_bytes": None,
                "observed_at_us": 1,
                "detail": "probe failed",
            },
            "status is invalid",
        ),
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


@pytest.mark.parametrize("field", ["database_size_bytes", "wal_size_bytes"])
def test_storage_health_snapshot_rejects_bool_size_values(field: str) -> None:
    kwargs: dict[str, object] = {
        "status": "available",
        "database_open": True,
        "database_path": "athena.sqlite3",
        "database_size_bytes": 1,
        "wal_size_bytes": 0,
        "observed_at_us": 1,
        "detail": None,
    }
    kwargs[field] = True

    with pytest.raises(ValueError, match="non-negative integer or None"):
        StorageHealthSnapshot(**kwargs)  # type: ignore[arg-type]


def test_storage_health_snapshot_rejects_bool_observation_time() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        StorageHealthSnapshot(
            status="available",
            database_open=True,
            database_path="athena.sqlite3",
            database_size_bytes=1,
            wal_size_bytes=0,
            observed_at_us=True,  # type: ignore[arg-type]
            detail=None,
        )


def test_storage_health_snapshot_requires_real_boolean_open_state() -> None:
    with pytest.raises(TypeError, match="database_open must be bool"):
        StorageHealthSnapshot(
            status="available",
            database_open=1,  # type: ignore[arg-type]
            database_path="athena.sqlite3",
            database_size_bytes=1,
            wal_size_bytes=0,
            observed_at_us=1,
            detail=None,
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("database_path", 1, "database_path must be str or None"),
        ("detail", b"probe failed", "detail must be str or None"),
    ],
)
def test_storage_health_snapshot_rejects_non_text_runtime_values(
    field: str,
    value: object,
    message: str,
) -> None:
    kwargs: dict[str, object] = {
        "status": "error",
        "database_open": True,
        "database_path": "athena.sqlite3",
        "database_size_bytes": None,
        "wal_size_bytes": None,
        "observed_at_us": 1,
        "detail": "probe failed",
    }
    kwargs[field] = value

    with pytest.raises(TypeError, match=message):
        StorageHealthSnapshot(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["database_path", "detail"])
def test_storage_health_snapshot_rejects_empty_text_facts(field: str) -> None:
    kwargs: dict[str, object] = {
        "status": "error",
        "database_open": True,
        "database_path": "athena.sqlite3",
        "database_size_bytes": None,
        "wal_size_bytes": None,
        "observed_at_us": 1,
        "detail": "probe failed",
    }
    kwargs[field] = ""

    with pytest.raises(ValueError, match="must not be empty"):
        StorageHealthSnapshot(**kwargs)  # type: ignore[arg-type]


def test_storage_health_snapshot_requires_path_for_open_error_state() -> None:
    with pytest.raises(ValueError, match="Open storage health requires a database path"):
        StorageHealthSnapshot(
            status="error",
            database_open=True,
            database_path=None,
            database_size_bytes=None,
            wal_size_bytes=None,
            observed_at_us=1,
            detail="probe failed",
        )


def test_storage_health_snapshot_requires_path_for_unavailable_state() -> None:
    with pytest.raises(ValueError, match="Unavailable storage health requires a database path"):
        StorageHealthSnapshot(
            status="unavailable",
            database_open=False,
            database_path=None,
            database_size_bytes=None,
            wal_size_bytes=None,
            observed_at_us=1,
            detail="not started",
        )


@pytest.mark.parametrize("database_path", [" ", "\t", "\r\n"])
def test_storage_health_snapshot_rejects_whitespace_only_database_path(
    database_path: str,
) -> None:
    with pytest.raises(ValueError, match="database_path must contain non-whitespace text"):
        StorageHealthSnapshot(
            status="error",
            database_open=True,
            database_path=database_path,
            database_size_bytes=None,
            wal_size_bytes=None,
            observed_at_us=1,
            detail="probe failed",
        )


@pytest.mark.parametrize("detail", [" ", "\t", "\r\n"])
def test_storage_health_snapshot_rejects_whitespace_only_detail(detail: str) -> None:
    with pytest.raises(ValueError, match="detail must contain non-whitespace text"):
        StorageHealthSnapshot(
            status="error",
            database_open=True,
            database_path="athena.sqlite3",
            database_size_bytes=None,
            wal_size_bytes=None,
            observed_at_us=1,
            detail=detail,
        )
