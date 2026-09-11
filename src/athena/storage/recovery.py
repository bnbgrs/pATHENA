"""Read-only startup inspection for ATHENA's canonical SQLite database."""

from __future__ import annotations

import os
import sqlite3
import stat
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import is_link_boundary
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
        if is_link_boundary(cursor):
            raise DatabaseRecoveryRequiredError(
                "ATHENA database path has a symbolic-link ancestor or reparse-point ancestor; "
                "recovery review is required."
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
class DatabaseFileIdentity:
    """Filesystem identity and mutation marker for one SQLite file-set member."""

    path: Path
    exists: bool
    device: int | None
    inode: int | None
    size: int | None
    mtime_ns: int | None
    ctime_ns: int | None

    def __post_init__(self) -> None:
        _require_path(self.path)
        if not isinstance(self.exists, bool):
            raise TypeError("Database file identity exists must be bool.")
        values = (self.device, self.inode, self.size, self.mtime_ns, self.ctime_ns)
        if self.exists:
            if any(value is None for value in values):
                raise ValueError("Existing database file identity requires complete metadata.")
            for label, value in zip(
                ("device", "inode", "size", "mtime_ns", "ctime_ns"),
                values,
                strict=True,
            ):
                _optional_nonnegative_int(value, f"Database file identity {label}")
        elif any(value is not None for value in values):
            raise ValueError("Missing database file identity must not carry metadata.")

    def same_object(self, other: DatabaseFileIdentity) -> bool:
        if not isinstance(other, DatabaseFileIdentity):
            return False
        return (
            self.exists
            and other.exists
            and self.device == other.device
            and self.inode == other.inode
        )


@dataclass(frozen=True, slots=True)
class DatabaseFileSetIdentity:
    """Attested primary DB, WAL and SHM state at one filesystem instant."""

    primary: DatabaseFileIdentity
    wal: DatabaseFileIdentity
    shm: DatabaseFileIdentity

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, DatabaseFileIdentity)
            for value in (self.primary, self.wal, self.shm)
        ):
            raise TypeError("Database file-set identity requires file identities.")


def _capture_file_identity(path: Path) -> DatabaseFileIdentity:
    if is_link_boundary(path):
        raise DatabaseRecoveryRequiredError(
            "SQLite file-set member became a symbolic link or reparse point; "
            "recovery review is required."
        )
    try:
        result = path.stat(follow_symlinks=False)
    except FileNotFoundError:
        return DatabaseFileIdentity(
            path=path,
            exists=False,
            device=None,
            inode=None,
            size=None,
            mtime_ns=None,
            ctime_ns=None,
        )
    except OSError as exc:
        raise DatabaseRecoveryRequiredError(
            "SQLite file-set identity could not be read."
        ) from exc

    if not stat.S_ISREG(result.st_mode):
        raise DatabaseRecoveryRequiredError(
            "SQLite file-set member is not a regular file."
        )
    return DatabaseFileIdentity(
        path=path,
        exists=True,
        device=int(result.st_dev),
        inode=int(result.st_ino),
        size=int(result.st_size),
        mtime_ns=int(result.st_mtime_ns),
        ctime_ns=int(result.st_ctime_ns),
    )


def capture_database_file_set(path: Path) -> DatabaseFileSetIdentity:
    """Capture fail-closed primary/WAL/SHM identity for continuity checks."""
    requested = _require_path(path).expanduser().absolute()
    _reject_symlink_ancestors(requested)
    return DatabaseFileSetIdentity(
        primary=_capture_file_identity(requested),
        wal=_capture_file_identity(requested.with_name(f"{requested.name}-wal")),
        shm=_capture_file_identity(requested.with_name(f"{requested.name}-shm")),
    )


@dataclass(frozen=True, slots=True)
class DatabasePreflightReport:
    """Read-only facts established before the live database is opened for writes."""

    path: Path
    exists: bool
    application_id: int | None
    schema_version: int | None
    wal_present: bool
    shm_present: bool
    file_set: DatabaseFileSetIdentity

    def __post_init__(self) -> None:
        _require_path(self.path)
        if not isinstance(self.exists, bool):
            raise TypeError("Database preflight exists must be bool.")
        _optional_nonnegative_int(self.application_id, "Database preflight application_id")
        _optional_nonnegative_int(self.schema_version, "Database preflight schema_version")
        if not isinstance(self.wal_present, bool) or not isinstance(self.shm_present, bool):
            raise TypeError("Database preflight sidecar flags must be bool.")
        if not isinstance(self.file_set, DatabaseFileSetIdentity):
            raise TypeError("Database preflight file_set must be DatabaseFileSetIdentity.")
        if self.file_set.primary.path != self.path:
            raise ValueError("Database preflight file-set primary path must match report path.")
        if self.file_set.primary.exists != self.exists:
            raise ValueError("Database preflight primary existence must match file-set identity.")
        if self.file_set.wal.exists != self.wal_present:
            raise ValueError("Database preflight WAL presence must match file-set identity.")
        if self.file_set.shm.exists != self.shm_present:
            raise ValueError("Database preflight SHM presence must match file-set identity.")
        if self.exists:
            if self.application_id is None or self.schema_version is None:
                raise ValueError(
                    "Existing database preflight requires application_id and schema_version."
                )
        elif self.application_id is not None or self.schema_version is not None:
            raise ValueError(
                "Missing database preflight must not carry application/schema metadata."
            )


def assert_database_preflight_current(report: DatabasePreflightReport) -> None:
    """Fail if DB/WAL/SHM changed after the read-only preflight returned."""
    if not isinstance(report, DatabasePreflightReport):
        raise TypeError("Database preflight continuity requires a preflight report.")
    current = capture_database_file_set(report.path)
    if current != report.file_set:
        raise DatabaseRecoveryRequiredError(
            "SQLite DB/WAL/SHM file set changed after read-only startup preflight."
        )


def assert_database_writer_bound(report: DatabasePreflightReport) -> None:
    """Verify pre-existing file objects still back the writer after connect.

    Opening SQLite may legitimately create a previously absent database or sidecar,
    so only objects that existed at the preflight boundary are identity-bound here.
    Content metadata is checked immediately before connect by
    :func:`assert_database_preflight_current`.
    """
    if not isinstance(report, DatabasePreflightReport):
        raise TypeError("Database writer binding requires a preflight report.")
    current = capture_database_file_set(report.path)
    for label, before, after in (
        ("primary", report.file_set.primary, current.primary),
        ("WAL", report.file_set.wal, current.wal),
        ("SHM", report.file_set.shm, current.shm),
    ):
        if before.exists and not before.same_object(after):
            raise DatabaseRecoveryRequiredError(
                f"SQLite {label} filesystem identity changed during writer establishment."
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

    if is_link_boundary(requested):
        raise DatabaseRecoveryRequiredError(
            "ATHENA database path is a symbolic link or reparse point; "
            "recovery review is required."
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
        file_set = capture_database_file_set(requested)
        return DatabasePreflightReport(
            path=requested,
            exists=False,
            application_id=None,
            schema_version=None,
            wal_present=file_set.wal.exists,
            shm_present=file_set.shm.exists,
            file_set=file_set,
        )

    if not requested.is_file():
        raise DatabaseRecoveryRequiredError(
            "ATHENA database path is not a regular file."
        )

    for sidecar in (wal_path, shm_path):
        if is_link_boundary(sidecar):
            raise DatabaseRecoveryRequiredError(
                "SQLite WAL/SHM sidecar is a symbolic link or reparse point; "
                "recovery review is required."
            )
        if os.path.lexists(sidecar) and not sidecar.is_file():
            raise DatabaseRecoveryRequiredError(
                "SQLite WAL/SHM sidecar is not a regular file."
            )

    pre_open_file_set = capture_database_file_set(requested)
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

    file_set = capture_database_file_set(requested)
    if not pre_open_file_set.primary.same_object(file_set.primary):
        raise DatabaseRecoveryRequiredError(
            "ATHENA database filesystem identity changed during read-only preflight."
        )
    for label, before, after in (
        ("WAL", pre_open_file_set.wal, file_set.wal),
        ("SHM", pre_open_file_set.shm, file_set.shm),
    ):
        if before.exists and not before.same_object(after):
            raise DatabaseRecoveryRequiredError(
                f"SQLite {label} filesystem identity changed during read-only preflight."
            )

    return DatabasePreflightReport(
        path=requested,
        exists=True,
        application_id=application_id,
        schema_version=schema_version,
        wal_present=file_set.wal.exists,
        shm_present=file_set.shm.exists,
        file_set=file_set,
    )
