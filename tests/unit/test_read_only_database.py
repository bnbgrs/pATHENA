from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from athena.storage.database import SQLiteDatabase
from athena.storage.read_only_database import (
    ReadOnlyDatabaseError,
    ReadOnlySQLiteDatabase,
)


def _create_database(path: Path) -> None:
    database = SQLiteDatabase(path)
    database.start()
    database.stop()


def test_read_only_database_opens_existing_canonical_database(tmp_path: Path) -> None:
    path = (tmp_path / "athena.db").absolute()
    _create_database(path)
    database = ReadOnlySQLiteDatabase(path)

    database.start()
    try:
        row = database.connection.execute("PRAGMA query_only").fetchone()
        assert row is not None
        assert int(row[0]) == 1
        assert database.connection.execute("PRAGMA user_version").fetchone() is not None
    finally:
        database.stop()


def test_read_only_database_refuses_write_statement(tmp_path: Path) -> None:
    path = (tmp_path / "athena.db").absolute()
    _create_database(path)
    database = ReadOnlySQLiteDatabase(path)

    database.start()
    try:
        with pytest.raises(sqlite3.OperationalError):
            database.connection.execute("CREATE TABLE forbidden (id INTEGER)")
    finally:
        database.stop()


def test_read_only_database_requires_existing_database(tmp_path: Path) -> None:
    path = (tmp_path / "missing.db").absolute()
    database = ReadOnlySQLiteDatabase(path)

    with pytest.raises(ReadOnlyDatabaseError, match="requires an existing"):
        database.start()

    assert not path.exists()


def test_read_only_database_start_stop_is_idempotent(tmp_path: Path) -> None:
    path = (tmp_path / "athena.db").absolute()
    _create_database(path)
    database = ReadOnlySQLiteDatabase(path)

    database.start()
    first = database.connection
    database.start()
    assert database.connection is first
    database.stop()
    database.stop()

    with pytest.raises(ReadOnlyDatabaseError, match="not started"):
        _ = database.connection
