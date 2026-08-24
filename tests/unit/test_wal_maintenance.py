from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.wal_maintenance import WalMaintenanceError, WalMaintenanceService


def _started_database(tmp_path: Path) -> SQLiteDatabase:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    return database


def test_wal_status_reports_live_policy_and_size(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        status = WalMaintenanceService(database).status()
    finally:
        database.stop()

    assert status.wal_path == tmp_path / "athena.db-wal"
    assert status.page_size_bytes > 0
    assert status.autocheckpoint_pages == 1000
    assert status.autocheckpoint_bytes == (
        status.page_size_bytes * status.autocheckpoint_pages
    )
    assert status.size_bytes >= 0


def test_passive_checkpoint_reports_sqlite_result(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        with database.write_transaction() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS wal_test (id INTEGER PRIMARY KEY, value TEXT)"
            )
            connection.execute("INSERT INTO wal_test(value) VALUES ('x')")

        result = WalMaintenanceService(database).checkpoint_passive()
    finally:
        database.stop()

    assert result.mode == "PASSIVE"
    assert isinstance(result.busy, bool)
    assert result.log_frames >= 0
    assert 0 <= result.checkpointed_frames <= result.log_frames
    assert result.wal_size_after_bytes >= 0


def test_checkpoint_rejects_active_athena_transaction(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        with database.write_transaction():
            with pytest.raises(WalMaintenanceError, match="active ATHENA transaction"):
                service.checkpoint_passive()
    finally:
        database.stop()


def test_truncate_checkpoint_requires_explicit_idle_confirmation(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        service = WalMaintenanceService(database)
        with pytest.raises(WalMaintenanceError, match="confirmed idle boundary"):
            service.checkpoint_truncate(idle_confirmed=False)

        result = service.checkpoint_truncate(idle_confirmed=True)
    finally:
        database.stop()

    assert result.mode == "TRUNCATE"
    assert isinstance(result.busy, bool)
    assert result.wal_size_after_bytes >= 0


def test_status_fails_closed_if_wal_autocheckpoint_is_disabled(tmp_path: Path) -> None:
    database = _started_database(tmp_path)
    try:
        database.connection.execute("PRAGMA wal_autocheckpoint = 0")
        with pytest.raises(WalMaintenanceError, match="wal_autocheckpoint"):
            WalMaintenanceService(database).status()
    finally:
        database.stop()
