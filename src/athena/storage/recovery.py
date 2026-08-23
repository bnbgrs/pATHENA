"""Read-only startup inspection for ATHENA's canonical SQLite database."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from athena.storage.locality import ActiveStateLocalityError, assert_active_state_root_local
from athena.storage.schema import (
    ATHENA_APPLICATION_ID,
    SCHEMA_VERSION,
    DatabaseCompatibilityError,
)


class DatabaseRecoveryRequiredError(DatabaseCompatibilityError):
    """Raised when normal writer startup must stop and recovery is required."""


def _require_path(value: object) -> Path:
    if not isinstance(value, Path):
        raise TypeError("ATHENA database preflight path must be a pathlib.Path.")
    return value


def _reject_symlink_ancestors(path: Path) -> None:
    cursor = path.parent
    while True:
        if cursor.is_symlink():
            raise DatabaseRecoveryRequiredError(
                "ATHENA database path has a symbolic-link ancestor; recovery review is required."
            )
        if cursor.exists() and not cursor.is_dir():
            raise DatabaseRecoveryRequiredError(
                "ATHENA database path ancestor is not a directory."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _optional_nonnegative_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer or None.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")
    return value


@dataclass(frozen=True, slots=True)
class DatabasePreflightReport:
    """Read-only facts established before the live database is opened for writes."""

    path: Path
    exists: bool
    application_id: int | None
    schema_version: int | None
    wal_present: bool
    shm_present: bool

    def __post_init__(self) -> None:
        _require_path(self.path)
        if not isinstance(self.exists, bool):
            raise TypeError("Database preflight exists must be bool.")
        _optional_nonnegative_int(self.application_id, "Database preflight application_id")
        _optional_nonnegative_int(self.schema_version, "Database preflight schema_version")
        if not isinstance(self.wal_present, bool) or not isinstance(self.shm_present, bool):
            raise TypeError("Database preflight sidecar flags must be bool.")
        if self.exists:
            if self.application_id is None or self.schema_version is None:
                raise ValueError(
                    "Existing database preflight requires application_id and schema_version."
                )
        elif self.application_id is not None or self.schema_version is not None:
            raise ValueError(
                "Missing database preflight must not carry application/schema metadata."
            )


def inspect_database_read_only(path: Path) -> DatabasePreflightReport:
    """Validate an existing ATHENA database before any normal writer connection."""
    requested = _require_path(path).expanduser().absolute()
    try:
        assert_active_state_root_local(requested.parent)
    except ActiveStateLocalityError as exc:
        raise DatabaseRecoveryRequiredError(
            "ATHENA refuses to open its active SQLite state on a network-backed root: "
            f"{exc}"
        ) from exc

    _reject_symlink_ancestors(requested)
    wal_path = requested.with_name(f"{requested.name}-wal")
    shm_path = requested.with_name(f"{requested.name}-shm")

    if requested.is_symlink():
        raise DatabaseRecoveryRequiredError(
            "ATHENA database path is a symbolic link; recovery review is required."
        )

    if not requested.exists():
        orphaned = tuple(
            sidecar
            for sidecar in (wal_path, shm_path)
            if os.path.lexists(sidecar)
        )
        if orphaned:
            raise DatabaseRecoveryRequiredError(
                "SQLite WAL/SHM sidecar exists without the primary ATHENA database."
            )
        return DatabasePreflightReport(
            path=requested,
            exists=False,
            application_id=None,
            schema_version=None,
            wal_present=False,
            shm_present=False,
        )

    if not requested.is_file():
        raise DatabaseRecoveryRequiredError(
            "ATHENA database path is not a regular file."
        )

    for sidecar in (wal_path, shm_path):
        if sidecar.is_symlink():
            raise DatabaseRecoveryRequiredError(
                "SQLite WAL/SHM sidecar is a symbolic link; recovery review is required."
            )
        if os.path.lexists(sidecar) and not sidecar.is_file():
            raise DatabaseRecoveryRequiredError(
                "SQLite WAL/SHM sidecar is not a regular file."
            )

    try:
        connection = sqlite3.connect(
            f"{requested.resolve().as_uri()}?mode=ro",
            uri=True,
            timeout=5.0,
            autocommit=True,
        )
    except sqlite3.Error as exc:
        raise DatabaseRecoveryRequiredError(
            "ATHENA database could not be opened read-only for startup preflight."
        ) from exc

    try:
        connection.execute("PRAGMA query_only = ON")
        application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
        schema_version = int(connection.execute("PRAGMA user_version").fetchone()[0])

        if application_id == 0:
            raise DatabaseRecoveryRequiredError(
                "Refusing to adopt a non-empty SQLite database without ATHENA application_id."
            )
        if application_id != ATHENA_APPLICATION_ID:
            raise DatabaseRecoveryRequiredError(
                "Database application_id does not belong to ATHENA."
            )
        if schema_version < 1:
            raise DatabaseRecoveryRequiredError(
                "Existing ATHENA database has no supported schema version."
            )
        if schema_version > SCHEMA_VERSION:
            raise DatabaseRecoveryRequiredError(
                f"Database schema version {schema_version} is newer than supported "
                f"version {SCHEMA_VERSION}."
            )

        quick_check_rows = connection.execute("PRAGMA quick_check").fetchall()
        quick_check = tuple(str(row[0]) for row in quick_check_rows)
        if quick_check != ("ok",):
            detail = "; ".join(quick_check[:8]) or "no result"
            raise DatabaseRecoveryRequiredError(
                f"SQLite startup quick_check failed: {detail}"
            )
    except DatabaseRecoveryRequiredError:
        raise
    except (sqlite3.Error, TypeError, ValueError, IndexError) as exc:
        raise DatabaseRecoveryRequiredError(
            "ATHENA database read-only startup preflight could not establish integrity."
        ) from exc
    finally:
        connection.close()

    return DatabasePreflightReport(
        path=requested,
        exists=True,
        application_id=application_id,
        schema_version=schema_version,
        wal_present=os.path.lexists(wal_path),
        shm_present=os.path.lexists(shm_path),
    )
