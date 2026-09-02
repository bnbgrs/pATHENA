"""SQLite Online Backup primitives for clone-first schema migration."""

from __future__ import annotations

import os
import sqlite3
import stat
from dataclasses import dataclass
from pathlib import Path

from athena.storage.durable_fs import fsync_directory, is_link_boundary


class MigrationCloneError(RuntimeError):
    """Raised when a pre-migration SQLite clone cannot be trusted."""


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, Path):
        raise TypeError(f"{label} must be a pathlib.Path.")
    expanded = value.expanduser()
    if not expanded.is_absolute():
        raise ValueError(f"{label} must be absolute.")
    return expanded


def _reject_link_boundary_path(path: Path, *, label: str) -> None:
    cursor = path
    while True:
        if is_link_boundary(cursor):
            raise MigrationCloneError(
                f"{label} must not contain a symlink, junction, or reparse point."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _sidecars(path: Path) -> tuple[Path, Path]:
    return (
        path.with_name(f"{path.name}-wal"),
        path.with_name(f"{path.name}-shm"),
    )


def _remove_candidate_files(candidate: Path, *, parent_fd: int | None = None) -> None:
    if parent_fd is not None:
        for name in (
            candidate.name,
            f"{candidate.name}-wal",
            f"{candidate.name}-shm",
        ):
            try:
                os.unlink(name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
            except OSError:
                pass
        try:
            os.fsync(parent_fd)
        except OSError:
            pass
        return

    for path in (candidate, *_sidecars(candidate)):
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def _fsync_file(path: Path) -> None:
    # Windows requires a writable CRT descriptor for fsync(); O_RDONLY works
    # on POSIX but can fail with EBADF on Windows. The migration candidate is a
    # private writable clone, so O_RDWR preserves semantics cross-platform.
    flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _open_posix_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise MigrationCloneError(
            "Migration clone candidate parent could not be opened safely."
        ) from exc
    try:
        handle_stat = os.fstat(descriptor)
        path_stat = os.stat(path, follow_symlinks=False)
        if not stat.S_ISDIR(handle_stat.st_mode) or not os.path.samestat(
            handle_stat,
            path_stat,
        ):
            raise MigrationCloneError(
                "Migration clone candidate parent identity changed while opening."
            )
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def _assert_posix_directory_current(path: Path, descriptor: int) -> None:
    try:
        handle_stat = os.fstat(descriptor)
        path_stat = os.stat(path, follow_symlinks=False)
    except OSError as exc:
        raise MigrationCloneError(
            "Migration clone candidate parent identity could not be verified."
        ) from exc
    if (
        is_link_boundary(path)
        or not stat.S_ISDIR(path_stat.st_mode)
        or not os.path.samestat(handle_stat, path_stat)
    ):
        raise MigrationCloneError(
            "Migration clone candidate parent changed during clone creation."
        )


def _posix_dirfd_path(parent_fd: int, filename: str) -> Path:
    """Return an SQLite-usable child path rooted at an already-open directory FD."""
    for fd_root in (Path("/proc/self/fd"), Path("/dev/fd")):
        descriptor_path = fd_root / str(parent_fd)
        if descriptor_path.exists():
            return descriptor_path / filename
    raise MigrationCloneError(
        "Identity-bound SQLite clone creation is unsupported on this POSIX platform."
    )


def _reserve_posix_candidate(candidate: Path, parent_fd: int) -> None:
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(
            candidate.name,
            flags,
            0o600,
            dir_fd=parent_fd,
        )
    except FileExistsError as exc:
        raise MigrationCloneError(
            "Migration clone candidate must not already exist."
        ) from exc
    except (NotImplementedError, TypeError) as exc:
        raise MigrationCloneError(
            "Identity-bound SQLite clone reservation is unsupported."
        ) from exc
    except OSError as exc:
        raise MigrationCloneError(
            "Migration clone candidate could not be reserved safely."
        ) from exc
    try:
        handle_stat = os.fstat(descriptor)
        if not stat.S_ISREG(handle_stat.st_mode):
            raise MigrationCloneError(
                "Migration clone candidate reservation is not a regular file."
            )
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.fsync(parent_fd)


def _inspect_posix_candidate(candidate: Path, parent_fd: int) -> os.stat_result:
    flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(candidate.name, flags, dir_fd=parent_fd)
    except OSError as exc:
        raise MigrationCloneError(
            "Migration clone candidate could not be reopened safely."
        ) from exc
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise MigrationCloneError(
                "Migration clone candidate is not a regular file."
            )
        os.fchmod(descriptor, 0o600)
        os.fsync(descriptor)
        return file_stat
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
    migration attempt. On POSIX, creation and cleanup stay rooted at an opened
    candidate-parent directory descriptor so replacing that pathname cannot redirect
    clone bytes into another directory. The clone is fsynced before return.
    """
    source = _absolute_path(source_db, "Migration clone source_db")
    candidate = _absolute_path(candidate_db, "Migration clone candidate_db")
    if source == candidate:
        raise MigrationCloneError("Migration clone source and candidate must differ.")

    _reject_link_boundary_path(source, label="Migration clone source")
    _reject_link_boundary_path(
        candidate.parent,
        label="Migration clone candidate parent",
    )

    if not source.is_file():
        raise MigrationCloneError("Migration clone source must be an existing regular file.")
    if not candidate.parent.is_dir():
        raise MigrationCloneError("Migration clone candidate parent must be a directory.")
    if candidate.exists() or is_link_boundary(candidate):
        raise MigrationCloneError("Migration clone candidate must not already exist.")
    if any(path.exists() or is_link_boundary(path) for path in _sidecars(candidate)):
        raise MigrationCloneError("Migration clone candidate has stale SQLite sidecars.")

    source_connection: sqlite3.Connection | None = None
    candidate_connection: sqlite3.Connection | None = None
    candidate_parent_fd: int | None = None
    created_candidate = False
    schema_version: int | None = None
    failure: BaseException | None = None
    try:
        # Re-check redirecting path boundaries immediately before either SQLite
        # open so an earlier validation is not the only traversal guard.
        _reject_link_boundary_path(source, label="Migration clone source")
        _reject_link_boundary_path(
            candidate.parent,
            label="Migration clone candidate parent",
        )
        source_connection = sqlite3.connect(
            f"{source.resolve(strict=True).as_uri()}?mode=ro",
            uri=True,
            timeout=5.0,
            autocommit=True,
        )
        source_connection.execute("PRAGMA query_only = ON")

        candidate_target: Path = candidate
        if os.name == "posix":
            candidate_parent_fd = _open_posix_directory(candidate.parent)
            _assert_posix_directory_current(candidate.parent, candidate_parent_fd)
            _reserve_posix_candidate(candidate, candidate_parent_fd)
            created_candidate = True
            candidate_target = _posix_dirfd_path(candidate_parent_fd, candidate.name)

        candidate_connection = sqlite3.connect(
            candidate_target,
            timeout=5.0,
            autocommit=True,
        )
        if os.name != "posix":
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
    except BaseException as exc:
        failure = exc
    finally:
        if candidate_connection is not None:
            candidate_connection.close()
        if source_connection is not None:
            source_connection.close()

    if failure is not None:
        if created_candidate:
            _remove_candidate_files(candidate, parent_fd=candidate_parent_fd)
        if candidate_parent_fd is not None:
            os.close(candidate_parent_fd)
        if isinstance(failure, MigrationCloneError):
            raise failure
        if isinstance(failure, (OSError, sqlite3.Error, TypeError, ValueError, IndexError)):
            raise MigrationCloneError("Migration clone could not be created safely.") from failure
        raise failure

    if schema_version is None:
        if created_candidate:
            _remove_candidate_files(candidate, parent_fd=candidate_parent_fd)
        if candidate_parent_fd is not None:
            os.close(candidate_parent_fd)
        raise MigrationCloneError("Migration clone schema version was not established.")

    try:
        if candidate_parent_fd is not None:
            _assert_posix_directory_current(candidate.parent, candidate_parent_fd)
            candidate_stat = _inspect_posix_candidate(candidate, candidate_parent_fd)
            os.fsync(candidate_parent_fd)
            _assert_posix_directory_current(candidate.parent, candidate_parent_fd)
            database_size = candidate_stat.st_size
        else:
            _reject_link_boundary_path(
                candidate.parent,
                label="Migration clone candidate parent",
            )
            if not candidate.is_file() or is_link_boundary(candidate):
                raise MigrationCloneError("Migration clone candidate is not a regular file.")
            _fsync_file(candidate)
            fsync_directory(candidate.parent)
            database_size = candidate.stat().st_size
    except (OSError, MigrationCloneError) as exc:
        if created_candidate:
            _remove_candidate_files(candidate, parent_fd=candidate_parent_fd)
        if isinstance(exc, MigrationCloneError):
            raise
        raise MigrationCloneError("Migration clone could not be durably published.") from exc
    finally:
        if candidate_parent_fd is not None:
            os.close(candidate_parent_fd)

    return MigrationCloneReport(
        source_db=source,
        candidate_db=candidate,
        schema_version=schema_version,
        database_size_bytes=database_size,
    )
