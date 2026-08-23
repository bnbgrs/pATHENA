"""Cross-process serialization for physical ATHENA data mutation."""

from __future__ import annotations

import importlib
import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, cast


class RuntimeDataLockError(RuntimeError):
    """Runtime data mutation lock cannot be established safely."""


class _ThreadState(threading.local):
    def __init__(self) -> None:
        self.depths: dict[str, int] = {}


_LOCAL_LOCK = threading.RLock()
_THREAD_STATE = _ThreadState()


def _reject_symlink_ancestors(path: Path) -> None:
    cursor = path.parent
    while True:
        if cursor.is_symlink():
            raise RuntimeDataLockError(
                "ATHENA state root has a symbolic-link ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise RuntimeDataLockError(
                "ATHENA state root ancestor is not a directory."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _open_lock_file(path: Path) -> BinaryIO:
    if path.is_symlink():
        raise RuntimeDataLockError(
            "ATHENA runtime mutation lock file must not be a symbolic link."
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
        raise RuntimeDataLockError(
            "ATHENA runtime mutation lock file became a symbolic link while opening."
        )
    if os.name == "posix":
        try:
            os.fchmod(handle.fileno(), 0o600)
        except OSError as exc:
            handle.close()
            raise RuntimeDataLockError(
                "ATHENA runtime mutation lock file permissions cannot be secured."
            ) from exc
    return handle


def _lock_windows(handle: BinaryIO) -> None:
    module = importlib.import_module("msvcrt")
    if os.fstat(handle.fileno()).st_size == 0:
        handle.seek(0)
        handle.write(b"\0")
        handle.flush()
        os.fsync(handle.fileno())
    handle.seek(0)
    module.locking(handle.fileno(), module.LK_LOCK, 1)


def _unlock_windows(handle: BinaryIO) -> None:
    module = importlib.import_module("msvcrt")
    handle.seek(0)
    module.locking(handle.fileno(), module.LK_UNLCK, 1)


def _lock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")
    module.flock(handle.fileno(), module.LOCK_EX)


def _unlock_posix(handle: BinaryIO) -> None:
    module = importlib.import_module("fcntl")
    module.flock(handle.fileno(), module.LOCK_UN)


def _lock_platform(handle: BinaryIO) -> None:
    if os.name == "nt":
        _lock_windows(handle)
        return
    if os.name == "posix":
        _lock_posix(handle)
        return
    raise RuntimeDataLockError(
        f"ATHENA runtime mutation locking is unsupported on platform {os.name!r}."
    )


def _unlock_platform(handle: BinaryIO) -> None:
    if os.name == "nt":
        _unlock_windows(handle)
        return
    if os.name == "posix":
        _unlock_posix(handle)
        return
    raise RuntimeDataLockError(
        f"ATHENA runtime mutation unlocking is unsupported on platform {os.name!r}."
    )


@contextmanager
def runtime_data_lock(
    state_root: Path | None,
) -> Iterator[None]:
    """Serialize operations that may create, move, or delete Raw Archive bytes."""
    if state_root is None:
        yield
        return
    if not isinstance(state_root, Path):
        raise TypeError("ATHENA state root must be a pathlib.Path or None.")

    requested = state_root.expanduser()
    _reject_symlink_ancestors(requested)
    if requested.is_symlink():
        raise RuntimeDataLockError(
            "ATHENA state root is unavailable for runtime mutation locking."
        )

    try:
        requested.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeDataLockError(
            "ATHENA state root cannot be prepared for runtime mutation locking."
        ) from exc

    _reject_symlink_ancestors(requested)
    if requested.is_symlink() or not requested.is_dir():
        raise RuntimeDataLockError(
            "ATHENA state root is unavailable for runtime mutation locking."
        )

    try:
        root = requested.resolve(strict=True)
    except OSError as exc:
        raise RuntimeDataLockError(
            "ATHENA state root cannot be resolved for runtime mutation locking."
        ) from exc

    key = os.path.normcase(str(root))

    with _LOCAL_LOCK:
        depth = _THREAD_STATE.depths.get(key, 0)
        if depth > 0:
            _THREAD_STATE.depths[key] = depth + 1
            try:
                yield
            finally:
                remaining = _THREAD_STATE.depths[key] - 1
                if remaining:
                    _THREAD_STATE.depths[key] = remaining
                else:
                    _THREAD_STATE.depths.pop(key, None)
            return

        lock_path = root / ".athena-runtime-data.lock"
        try:
            handle = _open_lock_file(lock_path)
        except RuntimeDataLockError:
            raise
        except OSError as exc:
            raise RuntimeDataLockError(
                "ATHENA runtime mutation lock file cannot be opened."
            ) from exc

        locked = False
        try:
            try:
                _lock_platform(handle)
            except OSError as exc:
                raise RuntimeDataLockError(
                    "ATHENA runtime mutation lock cannot be acquired."
                ) from exc

            locked = True
            _THREAD_STATE.depths[key] = 1
            yield
        finally:
            _THREAD_STATE.depths.pop(key, None)
            try:
                if locked:
                    try:
                        _unlock_platform(handle)
                    except OSError as exc:
                        raise RuntimeDataLockError(
                            "ATHENA runtime mutation lock could not be released cleanly."
                        ) from exc
            finally:
                handle.close()
