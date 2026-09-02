"""Cross-process serialization for one backup target."""

from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator, cast


class BackupTargetBusyError(RuntimeError):
    """Raised when another process owns the backup-target lock."""


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


def _assert_no_symlink_ancestor(path: Path) -> None:
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise BackupTargetBusyError(
                "Backup target path contains a symbolic-link ancestor."
            )


def _assert_handle_matches_path(lock_path: Path, handle: BinaryIO) -> None:
    try:
        path_stat = lock_path.stat(follow_symlinks=False)
        handle_stat = os.fstat(handle.fileno())
    except OSError as exc:
        raise BackupTargetBusyError(
            "Backup target lock identity cannot be verified."
        ) from exc
    if lock_path.is_symlink() or not os.path.samestat(path_stat, handle_stat):
        raise BackupTargetBusyError(
            "Backup target lock pathname changed during acquisition."
        )


def _open_lock_file(lock_path: Path) -> BinaryIO:
    if lock_path.is_symlink():
        raise BackupTargetBusyError(
            "Backup target lock must not be a symbolic link."
        )
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise BackupTargetBusyError(
            "Backup target lock cannot be opened safely."
        ) from exc

    try:
        handle = cast(BinaryIO, os.fdopen(descriptor, "r+b"))
    except BaseException:
        os.close(descriptor)
        raise

    try:
        _assert_handle_matches_path(lock_path, handle)
    except BackupTargetBusyError:
        handle.close()
        raise

    if os.name == "posix":
        try:
            os.fchmod(handle.fileno(), 0o600)
        except OSError as exc:
            handle.close()
            raise BackupTargetBusyError(
                "Backup target lock permissions cannot be secured."
            ) from exc
    return handle


@contextmanager
def backup_target_lock(target_root: Path) -> Iterator[None]:
    if not isinstance(target_root, Path):
        raise TypeError("Backup target root must be a pathlib.Path.")
    _assert_no_symlink_ancestor(target_root)
    if not target_root.is_dir():
        raise RuntimeError(
            f"Backup target is unavailable: {target_root}"
        )

    lock_path = target_root / ".athena-backup.lock"
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
