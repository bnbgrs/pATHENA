from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from athena.storage.connection_policy import (
    DEFAULT_BUSY_TIMEOUT_MS,
    MAX_BUSY_TIMEOUT_MS,
    MIN_BUSY_TIMEOUT_MS,
    apply_and_verify_connection_policy,
    validated_busy_timeout_ms,
)
from athena.storage.database import SQLiteDatabase


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, 1.5, "5000", None, MIN_BUSY_TIMEOUT_MS - 1, MAX_BUSY_TIMEOUT_MS + 1],
)
def test_busy_timeout_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        validated_busy_timeout_ms(value)


@pytest.mark.parametrize(
    "value",
    [MIN_BUSY_TIMEOUT_MS, DEFAULT_BUSY_TIMEOUT_MS, 15_000, MAX_BUSY_TIMEOUT_MS],
)
def test_busy_timeout_accepts_bounded_integer_values(value: int) -> None:
    assert validated_busy_timeout_ms(value) == value


def test_connection_policy_applies_and_verifies_required_pragmas() -> None:
    connection = sqlite3.connect(":memory:", autocommit=True)
    try:
        apply_and_verify_connection_policy(connection, busy_timeout_ms=15_000)

        assert int(connection.execute("PRAGMA foreign_keys").fetchone()[0]) == 1
        assert int(connection.execute("PRAGMA trusted_schema").fetchone()[0]) == 0
        assert int(connection.execute("PRAGMA busy_timeout").fetchone()[0]) == 15_000
    finally:
        connection.close()


def test_database_start_uses_configured_busy_timeout(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db", busy_timeout_ms=12_000)
    database.start()
    try:
        assert int(database.connection.execute("PRAGMA foreign_keys").fetchone()[0]) == 1
        assert int(database.connection.execute("PRAGMA trusted_schema").fetchone()[0]) == 0
        assert int(database.connection.execute("PRAGMA busy_timeout").fetchone()[0]) == 12_000
    finally:
        database.stop()
