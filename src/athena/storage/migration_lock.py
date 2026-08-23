"""Exclusive cross-process lock for blocking schema migrations."""

from __future__ import annotations

import importlib
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, cast

from athena.storage.durable_fs import is_link_boundary


class MigrationBusyError(RuntimeError):
    """Raised when migration ownership cannot be established safely."""


def _assert_safe_migration_root(path: Path) -> None:
    for candidate in (path, *path.parents):
        if is_link_boundary(candidate):
            raise MigrationBusyError(
                "Migration lock path contains a symlink, junction, or reparse-point ancestor."
            )
        if candidate.exists() and not candidate.is_dir():
            raise MigrationBusyError(
                "Migration lock path contains a non-directory ancestor."
            )


def _assert_handle_matches_path(lock_path: Path, handle: BinaryIO) -> None:
    try:
        path_stat = lock_path.stat(follow_symlinks=False)
        handle_stat = os.fstat(handle.fileno())
    except OSError as exc:
        raise MigrationBusyError("Migration lock identity cannot be verified.") from exc
    if is_link_boundary(lock_path) or not os.path.samestat(path_stat, handle_stat):
        raise MigrationBusyError("Migration lock pathname changed during acquisition.")


def _open_lock_file(lock_path: Path) -> BinaryIO:
    if is_link_boundary(lock_path):
        raise MigrationBusyError(
            "Migration lock must not be a symlink, junction, or reparse point."
        )
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise MigrationBusyError("Migration lock cannot be opened safely.") from exc
    try:
        handle = cast(BinaryIO, os.fdopen(descriptor, "r+b"))
    except BaseException:
        os.close(descriptor)
        raise
    try:
        _assert_handle_matches_path(lock_path, handle)
        if os.name == "posix":
            os.fchmod(handle.fileno(), 0o600)
    except OSError as exc:
        handle.close()
        raise MigrationBusyError("Migration lock permissions cannot be secured.") from exc
    except MigrationBusyError:
        handle.close()
        raise
    return handle


def _lock_windows(handle: BinaryIO) -> None:
    module = importlib.import_module("msvcrt")
    if os.fstat(handle.fileno()).st_size == 0:
        handle.seek(0)
        handle.write(b"\0")
        handle.flush()
        os.fsync(handle.fileno())
    handle.seek(0)
    try:
        module.locking(handle.fileno(), module.LK_NBLCK, 1)
    except OSError as exc:
        raise MigrationBusyError("Another process owns the migration lock.") from exc


def _unlock_windows(handle: BinaryIO) -> None:
    module = importlib.import_module("msvcrt")
    handle.seek(0)
    module.locking(handle.fileno(), module.LK_UNLCK, 1)


def _lock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")
    try:
        module.flock(handle.fileno(), module.LOCK_EX | module.LOCK_NB)
    except OSError as exc:
        raise MigrationBusyError("Another process owns the migration lock.") from exc


def _unlock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")
    module.flock(handle.fileno(), module.LOCK_UN)


def _lock(handle: BinaryIO) -> None:
    if os.name == "nt":
        _lock_windows(handle)
        return
    if os.name == "posix":
        _lock_posix(handle)
        return
    raise MigrationBusyError(
        f"Migration locking is unsupported on platform {os.name!r}."
    )


def _unlock(handle: BinaryIO) -> None:
    if os.name == "nt":
        _unlock_windows(handle)
        return
    if os.name == "posix":
        _unlock_posix(handle)
        return
    raise MigrationBusyError(
        f"Migration unlocking is unsupported on platform {os.name!r}."
    )


@contextmanager
def migration_lock(migration_root: Path) -> Iterator[None]:
    """Acquire the exclusive lock required for one blocking migration."""
    if not isinstance(migration_root, Path):
        raise TypeError("Migration root must be a pathlib.Path.")
    _assert_safe_migration_root(migration_root)
    if not migration_root.is_dir():
        raise MigrationBusyError("Migration root must be an existing directory.")

    lock_path = migration_root / ".athena-migration.lock"
    handle = _open_lock_file(lock_path)
    locked = False
    try:
        _lock(handle)
        _assert_handle_matches_path(lock_path, handle)
        locked = True
        yield
    finally:
        try:
            if locked:
                _unlock(handle)
        finally:
            handle.close()
