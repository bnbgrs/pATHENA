"""Fail-closed locality checks for ATHENA's active SQLite state root."""

from __future__ import annotations

import os
from pathlib import Path, PureWindowsPath
from typing import Callable

_UNKNOWN_WINDOWS_DRIVE = 0
_NO_ROOT_WINDOWS_DRIVE = 1
_REMOTE_WINDOWS_DRIVE = 4
_REMOTE_POSIX_FILESYSTEMS = frozenset(
    {
        "9p",
        "afs",
        "ceph",
        "cifs",
        "davfs",
        "fuse.sshfs",
        "glusterfs",
        "lustre",
        "nfs",
        "nfs4",
        "smb3",
        "sshfs",
    }
)


class ActiveStateLocalityError(RuntimeError):
    """Raised when the live database state root is not proven local enough."""


def _windows_unc_root(path: Path) -> bool:
    value = str(path)
    if value.startswith(("\\\\", "//")):
        return True
    windows = PureWindowsPath(value)
    return bool(windows.drive.startswith("\\\\"))


def _windows_drive_type(root: str) -> int:
    import ctypes

    function = ctypes.windll.kernel32.GetDriveTypeW  # type: ignore[attr-defined]
    function.argtypes = [ctypes.c_wchar_p]
    function.restype = ctypes.c_uint
    return int(function(root))


def _windows_drive_root(path: Path) -> str | None:
    windows = PureWindowsPath(str(path))
    if not windows.drive or windows.drive.startswith("\\\\"):
        return None
    return f"{windows.drive}\\"


def _decode_mountinfo_path(value: str) -> str:
    return (
        value.replace("\\040", " ")
        .replace("\\011", "\t")
        .replace("\\012", "\n")
        .replace("\\134", "\\")
    )


def _linux_mount_filesystem(path: Path, mountinfo_text: str) -> str | None:
    candidate = path.absolute()
    best_length = -1
    best_filesystem: str | None = None

    for line in mountinfo_text.splitlines():
        fields = line.split()
        try:
            separator = fields.index("-")
        except ValueError:
            continue
        if separator < 6 or separator + 1 >= len(fields):
            continue

        mount_point = Path(_decode_mountinfo_path(fields[4]))
        try:
            candidate.relative_to(mount_point)
        except ValueError:
            continue

        mount_length = len(str(mount_point))
        if mount_length > best_length:
            best_length = mount_length
            best_filesystem = fields[separator + 1].casefold()

    return best_filesystem


def assert_active_state_root_local(
    path: Path,
    *,
    _platform_name: str | None = None,
    _windows_drive_type_fn: Callable[[str], int] | None = None,
    _linux_mountinfo_text: str | None = None,
) -> None:
    """Reject a detectably network-backed root before live SQLite is opened."""
    if not isinstance(path, Path):
        raise TypeError("ATHENA active state root must be a pathlib.Path.")

    platform_name = os.name if _platform_name is None else _platform_name
    if platform_name == "nt":
        if _windows_unc_root(path):
            raise ActiveStateLocalityError(
                "ATHENA active state root must not use a UNC/network path."
            )
        root = _windows_drive_root(path)
        if root is None:
            raise ActiveStateLocalityError(
                "ATHENA could not establish a local Windows drive for active state."
            )
        drive_type_fn = _windows_drive_type_fn or _windows_drive_type
        try:
            drive_type = drive_type_fn(root)
        except OSError as exc:
            raise ActiveStateLocalityError(
                "ATHENA could not verify that the active state drive is local."
            ) from exc
        if drive_type == _REMOTE_WINDOWS_DRIVE:
            raise ActiveStateLocalityError(
                "ATHENA active state root must not use a mapped network drive."
            )
        if drive_type in {_UNKNOWN_WINDOWS_DRIVE, _NO_ROOT_WINDOWS_DRIVE}:
            raise ActiveStateLocalityError(
                "ATHENA could not verify that the active state drive is local."
            )
        return

    if platform_name != "posix":
        return

    mountinfo_text = _linux_mountinfo_text
    if mountinfo_text is None:
        mountinfo = Path("/proc/self/mountinfo")
        if not mountinfo.is_file():
            return
        try:
            mountinfo_text = mountinfo.read_text(encoding="utf-8")
        except OSError:
            return

    filesystem = _linux_mount_filesystem(path, mountinfo_text)
    if filesystem in _REMOTE_POSIX_FILESYSTEMS:
        raise ActiveStateLocalityError(
            "ATHENA active state root must not use a network filesystem "
            f"({filesystem})."
        )
