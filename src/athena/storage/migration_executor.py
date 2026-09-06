"""Candidate-only execution wrapper for ATHENA schema migrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from athena.storage.durable_fs import is_link_boundary
from athena.storage.schema import SCHEMA_VERSION, initialize_schema


class MigrationExecutorError(RuntimeError):
    """Raised when a migration candidate cannot be advanced safely."""


def _require_sqlite_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MigrationExecutorError(f"{label} must be an integer SQLite value.")
    return value


def _require_sqlite_nonnegative_int(value: object, label: str) -> int:
    validated = _require_sqlite_int(value, label)
    if validated < 0:
        raise MigrationExecutorError(f"{label} must not be negative.")
    return validated


def _require_sqlite_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise MigrationExecutorError(f"{label} must be a text SQLite value.")
    return value


def migrate_schema_candidate(candidate_db: Path, *, created_at_us: int) -> None:
    """Advance only candidate_db, then leave it sidecar-free for activation."""
    if not isinstance(candidate_db, Path) or not candidate_db.is_absolute():
        raise TypeError("Migration candidate must be an absolute pathlib.Path.")
    if isinstance(created_at_us, bool) or not isinstance(created_at_us, int) or created_at_us < 0:
        raise ValueError("Migration created_at_us must be a non-negative integer.")
    if is_link_boundary(candidate_db) or not candidate_db.is_file():
        raise MigrationExecutorError("Migration candidate must be a real regular file.")
    for parent in candidate_db.parents:
        if is_link_boundary(parent):
            raise MigrationExecutorError("Migration candidate has an unsafe path ancestor.")

    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(candidate_db, timeout=5.0, autocommit=True)
        # Schema migrations share the same mapping-row contract as the live
        # SQLite service. Historical migration verifiers address columns by
        # name, so a raw tuple row factory would fail mid-upgrade.
        connection.row_factory = sqlite3.Row
        initialize_schema(connection, created_at_us=created_at_us)
        row = connection.execute("PRAGMA user_version").fetchone()
        if row is None:
            raise MigrationExecutorError("Migration candidate did not reach current schema.")
        user_version = _require_sqlite_int(row[0], "Migration candidate user_version")
        if user_version != SCHEMA_VERSION:
            raise MigrationExecutorError("Migration candidate did not reach current schema.")

        checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        if checkpoint is None or len(checkpoint) != 3:
            raise MigrationExecutorError("Migration candidate WAL checkpoint returned invalid status.")
        busy = _require_sqlite_int(checkpoint[0], "Migration candidate checkpoint busy")
        log_frames = _require_sqlite_nonnegative_int(
            checkpoint[1],
            "Migration candidate checkpoint log_frames",
        )
        checkpointed_frames = _require_sqlite_nonnegative_int(
            checkpoint[2],
            "Migration candidate checkpoint checkpointed_frames",
        )
        if busy != 0 or log_frames != checkpointed_frames:
            raise MigrationExecutorError(
                "Migration candidate WAL checkpoint did not fully complete."
            )

        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()
        if mode is None:
            raise MigrationExecutorError("Migration candidate could not leave WAL mode.")
        journal_mode = _require_sqlite_text(mode[0], "Migration candidate journal_mode")
        if journal_mode.casefold() != "delete":
            raise MigrationExecutorError("Migration candidate could not leave WAL mode.")
    except MigrationExecutorError:
        raise
    except (sqlite3.Error, TypeError, ValueError, IndexError) as exc:
        raise MigrationExecutorError("Migration candidate schema execution failed.") from exc
    finally:
        if connection is not None:
            connection.close()

    for sidecar in (
        candidate_db.with_name(f"{candidate_db.name}-wal"),
        candidate_db.with_name(f"{candidate_db.name}-shm"),
    ):
        if sidecar.exists() or is_link_boundary(sidecar):
            raise MigrationExecutorError("Migration candidate retained SQLite sidecars.")
