"""Candidate-only execution wrapper for ATHENA schema migrations."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from athena.storage.durable_fs import is_link_boundary
from athena.storage.schema import SCHEMA_VERSION, initialize_schema


class MigrationExecutorError(RuntimeError):
    """Raised when a migration candidate cannot be advanced safely."""


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
        initialize_schema(connection, created_at_us=created_at_us)
        row = connection.execute("PRAGMA user_version").fetchone()
        if row is None or int(row[0]) != SCHEMA_VERSION:
            raise MigrationExecutorError("Migration candidate did not reach current schema.")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        mode = connection.execute("PRAGMA journal_mode = DELETE").fetchone()
        if mode is None or str(mode[0]).casefold() != "delete":
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
