"""Crash-durable filesystem publication primitives."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

_MOVEFILE_REPLACE_EXISTING = 0x00000001
_MOVEFILE_WRITE_THROUGH = 0x00000008
_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400


def is_link_boundary(path: Path) -> bool:
    """Return whether *path* can redirect filesystem traversal.

    This is the shared storage trust-boundary predicate for symlinks, Windows
    junctions, and other Windows reparse points. Callers performing durable or
    security-sensitive path traversal should use this instead of ``is_symlink``.
    """
    if not isinstance(path, Path):
        raise TypeError("Filesystem boundary path must be a pathlib.Path.")
    if path.is_symlink():
        return True

    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        return True

    if os.name != "nt":
        return False

    try:
        stat_result = os.lstat(path)
    except OSError:
        return False

    attributes = int(getattr(stat_result, "st_file_attributes", 0))
    return bool(attributes & _FILE_ATTRIBUTE_REPARSE_POINT)


def _is_link_boundary(path: Path) -> bool:
    """Backward-compatible private alias for the shared boundary predicate."""
    return is_link_boundary(path)


def _assert_real_directory(path: Path, *, label: str) -> None:
    """Reject missing, non-directory, or link-backed directory boundaries."""
    if is_link_boundary(path) or not path.is_dir():
        raise NotADirectoryError(f"{label} is unsafe: {path}")

    cursor = path.parent
    while True:
        if is_link_boundary(cursor):
            raise NotADirectoryError(
                f"{label} has a symlink ancestor or reparse-point ancestor: {cursor}"
            )
        if cursor.exists() and not cursor.is_dir():
            raise NotADirectoryError(
                f"{label} has a non-directory ancestor: {cursor}"
            )
        parent = cursor.parent
        if parent == cursor:
            return
        cursor = parent


def durable_replace(source: Path, destination: Path) -> None:
    """Atomically publish *source* and flush every changed directory entry."""
    source_path = Path(source)
    destination_path = Path(destination)
    source_parent = source_path.parent
    destination_parent = destination_path.parent

    _assert_real_directory(source_parent, label="Durable replace source parent")
    _assert_real_directory(destination_parent, label="Durable replace destination parent")

    if is_link_boundary(source_path):
        raise OSError(
            f"Durable replace source is a symlink or reparse point: {source_path}"
        )
    if is_link_boundary(destination_path):
        raise OSError(
            f"Durable replace destination is a symlink or reparse point: {destination_path}"
        )

    if _is_windows():
        _windows_replace_write_through(source_path, destination_path)
        return

    os.replace(source_path, destination_path)
    fsync_directory(destination_parent)
    if source_parent != destination_parent:
        fsync_directory(source_parent)


def durable_mkdir(path: Path, *, parents: bool = False, exist_ok: bool = False) -> None:
    """Create a directory and durably publish every newly created entry."""
    directory = Path(path)
    if is_link_boundary(directory):
        raise FileExistsError(
            f"Durable directory path is a symlink or reparse point: {directory}"
        )
    if directory.exists():
        if not directory.is_dir():
            raise FileExistsError(f"Durable directory path is not a directory: {directory}")
        _assert_real_directory(directory, label="Durable directory")
        if exist_ok:
            return
        raise FileExistsError(f"Durable directory already exists: {directory}")
    if not parents:
        _durable_create_one_directory(directory, exist_ok=exist_ok)
        return

    missing: list[Path] = []
    cursor = directory
    while not cursor.exists():
        if is_link_boundary(cursor):
            raise FileExistsError(
                f"Durable directory ancestor is a symlink or reparse point: {cursor}"
            )
        missing.append(cursor)
        parent = cursor.parent
        if parent == cursor:
            raise FileNotFoundError(f"No existing ancestor for durable directory: {directory}")
        cursor = parent
    _assert_real_directory(cursor, label="Durable directory ancestor")
    for item in reversed(missing):
        _durable_create_one_directory(item, exist_ok=(exist_ok if item == directory else True))


def _durable_create_one_directory(directory: Path, *, exist_ok: bool) -> None:
    parent = directory.parent
    _assert_real_directory(parent, label="Durable directory parent")
    if _is_windows():
        _windows_durable_create_directory(directory, exist_ok=exist_ok)
        return
    try:
        directory.mkdir(parents=False, exist_ok=False)
    except FileExistsError:
        if exist_ok and directory.is_dir() and not is_link_boundary(directory):
            _assert_real_directory(directory, label="Durable directory")
            return
        raise
    fsync_directory(parent)


def _windows_durable_create_directory(directory: Path, *, exist_ok: bool) -> None:
    staging = directory.with_name(f".{directory.name}.{secrets.token_hex(8)}.mkdir-partial")
    staging.mkdir(parents=False, exist_ok=False)
    try:
        try:
            _windows_replace_write_through(staging, directory)
        except OSError:
            if exist_ok and directory.is_dir() and not is_link_boundary(directory):
                _assert_real_directory(directory, label="Durable directory")
                return
            raise
    finally:
        try:
            staging.rmdir()
        except FileNotFoundError:
            pass


def fsync_directory(path: Path) -> None:
    """Synchronize one real directory entry set on POSIX."""
    directory = Path(path)
    _assert_real_directory(directory, label="fsync directory")
    if _is_windows():
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    flags |= nofollow
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _is_windows() -> bool:
    return os.name == "nt"


def _windows_api_path(path: Path) -> str:
    value = str(path.absolute())
    if value.startswith("\\\\?\\"):
        return value
    if value.startswith("\\\\"):
        return "\\\\?\\UNC\\" + value[2:]
    return "\\\\?\\" + value


def _windows_replace_write_through(source: Path, destination: Path) -> None:
    import ctypes
    from ctypes import wintypes

    win_dll = vars(ctypes)["WinDLL"]
    get_last_error = vars(ctypes)["get_last_error"]
    source_is_directory = source.is_dir()
    if source_is_directory and destination.exists():
        raise FileExistsError(f"Durable directory destination already exists: {destination}")
    kernel32 = win_dll("kernel32", use_last_error=True)
    move_file_ex = kernel32.MoveFileExW
    move_file_ex.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD)
    move_file_ex.restype = wintypes.BOOL
    flags = _MOVEFILE_WRITE_THROUGH
    if not source_is_directory:
        flags |= _MOVEFILE_REPLACE_EXISTING
    succeeded = move_file_ex(_windows_api_path(source), _windows_api_path(destination), flags)
    if succeeded:
        return
    error = get_last_error()
    raise OSError(error, f"MoveFileExW durable publication failed with Windows error {error}.", str(destination))
