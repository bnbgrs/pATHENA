"""Cross-process ownership lock for long-lived scheduler lanes."""

from __future__ import annotations

import importlib
import os
from collections.abc import Callable
from pathlib import Path
from typing import BinaryIO, cast


class SchedulerLaneOwnershipError(RuntimeError):
    """Raised when a long-lived scheduler lane already has a process owner."""


def _reject_symlink_ancestors(path: Path, *, lane_name: str) -> None:
    cursor = path.parent
    while True:
        if cursor.is_symlink():
            raise SchedulerLaneOwnershipError(
                f"Scheduler {lane_name} lane lock has a symlink ancestor."
            )
        if cursor.exists() and not cursor.is_dir():
            raise SchedulerLaneOwnershipError(
                f"Scheduler {lane_name} lane lock ancestor is not a directory."
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def _assert_handle_matches_path(
    path: Path,
    handle: BinaryIO,
    *,
    lane_name: str,
) -> None:
    """Fail closed if the pathname was swapped after the lock file was opened."""
    try:
        path_stat = path.stat(follow_symlinks=False)
        handle_stat = os.fstat(handle.fileno())
    except OSError as exc:
        raise SchedulerLaneOwnershipError(
            f"Scheduler {lane_name} lane lock identity cannot be verified."
        ) from exc
    if path.is_symlink() or not os.path.samestat(path_stat, handle_stat):
        raise SchedulerLaneOwnershipError(
            f"Scheduler {lane_name} lane lock pathname changed during acquisition."
        )


class SchedulerLaneProcessLock:
    """Hold one OS-released advisory lock for a scheduler process lifetime."""

    def __init__(
        self,
        *,
        path: Path,
        handle: BinaryIO,
    ) -> None:
        if not isinstance(path, Path):
            raise TypeError("Scheduler lane lock path must be a pathlib.Path value.")
        if not hasattr(handle, "fileno") or not hasattr(handle, "close"):
            raise TypeError("Scheduler lane lock handle must be a binary file handle.")
        self.path = path
        self._handle: BinaryIO | None = handle

    @classmethod
    def acquire(
        cls,
        path: Path,
        *,
        lane_name: str,
    ) -> SchedulerLaneProcessLock:
        if not isinstance(path, Path):
            raise ValueError("Scheduler lane lock path must be a pathlib.Path value.")
        if not isinstance(lane_name, str):
            raise ValueError("Scheduler lane name must be text.")
        normalized_lane = lane_name.strip()
        if not normalized_lane:
            raise ValueError("Scheduler lane name must not be empty.")
        if os.name not in {"nt", "posix"}:
            raise SchedulerLaneOwnershipError(
                f"Scheduler {normalized_lane} lane locking is unsupported "
                f"on platform {os.name!r}."
            )

        _reject_symlink_ancestors(path, lane_name=normalized_lane)
        if path.is_symlink():
            raise SchedulerLaneOwnershipError(
                f"Scheduler {normalized_lane} lane lock must not be a symlink."
            )

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            _reject_symlink_ancestors(path, lane_name=normalized_lane)
            if path.is_symlink():
                raise SchedulerLaneOwnershipError(
                    f"Scheduler {normalized_lane} lane lock must not be a symlink."
                )
            handle = _open_lock_file(path)
        except SchedulerLaneOwnershipError:
            raise
        except OSError as exc:
            raise SchedulerLaneOwnershipError(
                f"Scheduler {normalized_lane} lane lock cannot be opened."
            ) from exc

        try:
            _assert_handle_matches_path(
                path,
                handle,
                lane_name=normalized_lane,
            )
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
                os.fsync(handle.fileno())
            if os.name == "posix":
                os.fchmod(handle.fileno(), 0o600)
            handle.seek(0)
        except SchedulerLaneOwnershipError:
            handle.close()
            raise
        except OSError as exc:
            handle.close()
            raise SchedulerLaneOwnershipError(
                f"Scheduler {normalized_lane} lane lock cannot be initialized."
            ) from exc

        try:
            _lock_nonblocking(handle)
            _assert_handle_matches_path(
                path,
                handle,
                lane_name=normalized_lane,
            )
        except SchedulerLaneOwnershipError:
            handle.close()
            raise
        except OSError as exc:
            handle.close()
            raise SchedulerLaneOwnershipError(
                f"Scheduler {normalized_lane} lane already has a live process owner."
            ) from exc

        return cls(path=path, handle=handle)

    def close(self) -> None:
        """Release process ownership by closing the locked file handle."""
        handle = self._handle
        if handle is None:
            return
        self._handle = None
        handle.close()


def _open_lock_file(path: Path) -> BinaryIO:
    flags = os.O_RDWR | os.O_CREAT
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags | nofollow, 0o600)
    try:
        return cast(BinaryIO, os.fdopen(descriptor, "r+b"))
    except BaseException:
        os.close(descriptor)
        raise


def _lock_nonblocking(handle: BinaryIO) -> None:
    if os.name == "nt":
        msvcrt = importlib.import_module("msvcrt")
        locking = cast(
            Callable[[int, int, int], object],
            vars(msvcrt)["locking"],
        )
        mode = cast(int, vars(msvcrt)["LK_NBLCK"])
        locking(handle.fileno(), mode, 1)
        return

    if os.name == "posix":
        fcntl = importlib.import_module("fcntl")
        flock = cast(
            Callable[[int, int], object],
            vars(fcntl)["flock"],
        )
        exclusive = cast(int, vars(fcntl)["LOCK_EX"])
        nonblocking = cast(int, vars(fcntl)["LOCK_NB"])
        flock(handle.fileno(), exclusive | nonblocking)
        return

    raise OSError(
        f"Unsupported platform for scheduler lane locking: {os.name!r}."
    )
