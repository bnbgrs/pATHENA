"""SQLite Online Backup primitives for clone-first schema migration."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import fsync_directory


class MigrationCloneError(RuntimeError):
    """Raised when a pre-migration SQLite clone cannot be trusted."""


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, Path):
        raise TypeError(f"{label} must be a pathlib.Path.")
    expanded = value.expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"{label} must be absolute.")
    return expanded


def _reject_symlink_path(path: Path, *, label: str) -> None:
    cursor = path
    while True:
        if cursor.is_symlink():
            raise MigrationCloneError(f"{label} must not contain a symbolic link.")
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _sidecars(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.name}-wal"),
        path.with_name(f"{path.name}-shm"),
    )


def _remove_candidate_files(candidate: Path) -> None:
    for path in (candidate, *_sidecars(candidate)):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def _fsync_file(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@dataclass(frozen=True, slots=True)
class MigrationCloneReport:
    source_db: Path
    candidate_db: Path
    schema_version: int
    database_size_bytes: int

    def __post_init__(self) -> None:
        source = _absolute_path(self.source_db, "Migration clone source_db")
        candidate = _absolute_path(self.candidate_db, "Migration clone candidate_db")
        if source == candidate:
            raise ValueError("Migration clone source and candidate must differ.")
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version < 0
        ):
            raise ValueError("Migration clone schema_version must be a non-negative integer.")
        if (
            isinstance(self.database_size_bytes, bool)
            or not isinstance(self.database_size_bytes, int)
            or self.database_size_bytes < 0
        ):
            raise ValueError(
                "Migration clone database_size_bytes must be a non-negative integer."
            )


def create_migration_clone(
    *,
    source_db: Path,
    candidate_db: Path,
) -> MigrationCloneReport:
    """Create and validate a standalone SQLite snapshot with Online Backup API.

    The source is opened read-only. The destination must not already exist, so
    recovery can distinguish an old candidate from the one created by the current
    migration attempt. The clone is fsynced before the function returns.
    """
    source = _absolute_path(source_db, "Migration clone source_db")
    candidate = _absolute_path(candidate_db, "Migration clone candidate_db")
    if source == candidate:
        raise MigrationCloneError("Migration clone source and candidate must differ.")

    _reject_symlink_path(source, label="Migration clone source")
    _reject_symlink_path(candidate.parent, label="Migration clone candidate parent")

    if not source.is_file():
        raise MigrationCloneError("Migration clone source must be an existing regular file.")
    if not candidate.parent.is_dir():
        raise MigrationCloneError("Migration clone candidate parent must be a directory.")
    if candidate.exists() or candidate.is_symlink():
        raise MigrationCloneError("Migration clone candidate must not already exist.")
    if any(path.exists() or path.is_symlink() for path in _sidecars(candidate)):
        raise MigrationCloneError("Migration clone candidate has stale SQLite sidecars.")

    source_connection: sqlite3.Connection | None = None
    candidate_connection: sqlite3.Connection | None = None
    created_candidate = False
    try:
        source_connection = sqlite3.connect(
            f"{source.resolve(strict=True).as_uri()}?mode=ro",
            uri=True,
            timeout=5.0,
            autocommit=True,
        )
        source_connection.execute("PRAGMA query_only = ON")

        candidate_connection = sqlite3.connect(
            candidate,
            timeout=5.0,
            autocommit=True,
        )
        created_candidate = True
        source_connection.backup(candidate_connection)

        quick_check = tuple(
            str(row[0])
            for row in candidate_connection.execute("PRAGMA quick_check").fetchall()
        )
        if quick_check != ("ok",):
            detail = "; ".join(quick_check[:8]) or "no result"
            raise MigrationCloneError(
                f"Migration clone SQLite quick_check failed: {detail}"
            )

        foreign_key_rows = candidate_connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()
        if foreign_key_rows:
            raise MigrationCloneError(
                "Migration clone SQLite foreign_key_check reported violations."
            )

        schema_row = candidate_connection.execute("PRAGMA user_version").fetchone()
        if schema_row is None:
            raise MigrationCloneError("Migration clone schema version could not be read.")
        schema_version = int(schema_row[0])
        if schema_version < 0:
            raise MigrationCloneError("Migration clone schema version must not be negative.")
    except MigrationCloneError:
        raise
    except (OSError, sqlite3.Error, TypeError, ValueError, IndexError) as exc:
        raise MigrationCloneError("Migration clone could not be created safely.") from exc
    finally:
        if candidate_connection is not None:
            candidate_connection.close()
        if source_connection is not None:
            source_connection.close()

    try:
        if not candidate.is_file() or candidate.is_symlink():
            raise MigrationCloneError("Migration clone candidate is not a regular file.")
        if os.name == "posix":
            os.chmod(candidate, 0o600)
        _fsync_file(candidate)
        fsync_directory(candidate.parent)
        database_size = candidate.stat().st_size
    except (OSError, MigrationCloneError) as exc:
        if created_candidate:
            _remove_candidate_files(candidate)
        if isinstance(exc, MigrationCloneError):
            raise
        raise MigrationCloneError("Migration clone could not be durably published.") from exc

    return MigrationCloneReport(
        source_db=source,
        candidate_db=candidate,
        schema_version=schema_version,
        database_size_bytes=database_size,
    )
