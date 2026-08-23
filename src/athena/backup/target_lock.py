"""Cross-process serialization for one backup target."""

from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator, cast


class BackupTargetBusyError(RuntimeError):
    """Raised when another process owns the backup-target lock."""


def _reject_symlink_ancestors(path: Path) -> None:
    cursor = path.parent
    while True:
        if cursor.is_symlink():
            raise BackupTargetBusyError(
                "Backup target has a symbolic-link ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise BackupTargetBusyError(
                "Backup target ancestor is not a directory."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _open_lock_file(path: Path) -> BinaryIO:
    if path.is_symlink():
        raise BackupTargetBusyError(
            "Backup target lock must not be a symbolic link."
        )
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        handle = cast(BinaryIO, os.fdopen(descriptor, "r+b"))
    except BaseException:
        os.close(descriptor)
        raise
    if path.is_symlink():
        handle.close()
        raise BackupTargetBusyError(
            "Backup target lock became a symbolic link while opening."
        )
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
        module.locking(
            handle.fileno(),
            module.LK_NBLCK,
            1,
        )
    except OSError as exc:
        raise BackupTargetBusyError(
            "Backup target is busy in another process."
        ) from exc


def _unlock_windows(handle: BinaryIO) -> None:
    module = importlib.import_module("msvcrt")
    handle.seek(0)
    module.locking(
        handle.fileno(),
        module.LK_UNLCK,
        1,
    )


def _lock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")

    try:
        module.flock(
            handle.fileno(),
            module.LOCK_EX | module.LOCK_NB,
        )
    except OSError as exc:
        raise BackupTargetBusyError(
            "Backup target is busy in another process."
        ) from exc


def _unlock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")
    module.flock(
        handle.fileno(),
        module.LOCK_UN,
    )


def _lock(handle: BinaryIO) -> None:
    if os.name == "nt":
        _lock_windows(handle)
        return
    if os.name == "posix":
        _lock_posix(handle)
        return
    raise BackupTargetBusyError(
        f"Backup target locking is unsupported on platform {os.name!r}."
    )


def _unlock(handle: BinaryIO) -> None:
    if os.name == "nt":
        _unlock_windows(handle)
        return
    if os.name == "posix":
        _unlock_posix(handle)
        return
    raise BackupTargetBusyError(
        f"Backup target unlocking is unsupported on platform {os.name!r}."
    )


@contextmanager
def backup_target_lock(target_root: Path) -> Iterator[None]:
    if not isinstance(target_root, Path):
        raise TypeError("Backup target root must be a pathlib.Path.")
    _reject_symlink_ancestors(target_root)
    if target_root.is_symlink() or not target_root.is_dir():
        raise RuntimeError(
            f"Backup target is unavailable: {target_root}"
        )

    lock_path = target_root / ".athena-backup.lock"
    try:
        handle = _open_lock_file(lock_path)
    except BackupTargetBusyError:
        raise
    except OSError as exc:
        raise BackupTargetBusyError(
            "Backup target lock cannot be opened safely."
        ) from exc

    locked = False

    try:
        _lock(handle)
        locked = True
        yield
    finally:
        try:
            if locked:
                _unlock(handle)
        finally:
            handle.close()
