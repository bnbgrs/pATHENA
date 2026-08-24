"""Fail-closed SQLite connection policy verification for ATHENA."""

from __future__ import annotations

import sqlite3

from athena.storage.schema_contract import DatabaseCompatibilityError

MIN_BUSY_TIMEOUT_MS = 5_000
MAX_BUSY_TIMEOUT_MS = 120_000
DEFAULT_BUSY_TIMEOUT_MS = MIN_BUSY_TIMEOUT_MS


def validated_busy_timeout_ms(value: object) -> int:
    """Return a bounded SQLite busy timeout in milliseconds.

    ATHENA v1 keeps the historical 5 second floor while permitting longer,
    explicitly configured waits up to two minutes. Booleans are rejected even
    though ``bool`` is an ``int`` subclass.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("SQLite busy timeout must be an integer number of milliseconds.")
    if not MIN_BUSY_TIMEOUT_MS <= value <= MAX_BUSY_TIMEOUT_MS:
        raise ValueError(
            "SQLite busy timeout must be between "
            f"{MIN_BUSY_TIMEOUT_MS} and {MAX_BUSY_TIMEOUT_MS} milliseconds."
        )
    return value


def apply_and_verify_connection_policy(
    connection: sqlite3.Connection,
    *,
    busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
) -> None:
    """Apply runtime-only SQLite policy and verify safety-critical readback.

    Schema/bootstrap code owns WAL and schema evolution. This helper owns the
    per-connection settings whose silent refusal would invalidate writer and
    foreign-key safety assumptions.
    """
    if not isinstance(connection, sqlite3.Connection):
        raise TypeError("connection must be a sqlite3.Connection.")
    timeout_ms = validated_busy_timeout_ms(busy_timeout_ms)

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA busy_timeout = {timeout_ms}")
    connection.execute("PRAGMA trusted_schema = OFF")

    foreign_keys_row = connection.execute("PRAGMA foreign_keys").fetchone()
    if foreign_keys_row is None or int(foreign_keys_row[0]) != 1:
        raise DatabaseCompatibilityError(
            "SQLite foreign_keys could not be enabled for the ATHENA connection."
        )

    trusted_schema_row = connection.execute("PRAGMA trusted_schema").fetchone()
    if trusted_schema_row is None or int(trusted_schema_row[0]) != 0:
        raise DatabaseCompatibilityError(
            "SQLite trusted_schema could not be disabled for the ATHENA connection."
        )

    busy_timeout_row = connection.execute("PRAGMA busy_timeout").fetchone()
    if busy_timeout_row is None or int(busy_timeout_row[0]) != timeout_ms:
        raise DatabaseCompatibilityError(
            "SQLite busy_timeout readback does not match the configured ATHENA value."
        )
