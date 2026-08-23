from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from athena.backup.target_lock import BackupTargetBusyError, backup_target_lock


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlink unavailable: {exc}")


def test_backup_target_lock_rejects_symlink_target_root(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(RuntimeError, match="unavailable"):
        with backup_target_lock(link):
            raise AssertionError("unreachable")


def test_backup_target_lock_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    child = real / "child"
    child.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(BackupTargetBusyError, match="symbolic-link ancestor"):
        with backup_target_lock(link / "child"):
            raise AssertionError("unreachable")


def test_backup_target_lock_rejects_symlink_lock_file(tmp_path: Path) -> None:
    target_root = tmp_path / "backup"
    target_root.mkdir()
    target = tmp_path / "target.lock"
    target.write_bytes(b"unchanged")
    lock_path = target_root / ".athena-backup.lock"
    try:
        lock_path.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"File symlink unavailable: {exc}")

    with pytest.raises(BackupTargetBusyError, match="symbolic link"):
        with backup_target_lock(target_root):
            raise AssertionError("unreachable")

    assert target.read_bytes() == b"unchanged"


def test_backup_target_lock_file_has_owner_only_permissions_on_posix(
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX file-mode assertion")

    target_root = tmp_path / "backup"
    target_root.mkdir()
    lock_path = target_root / ".athena-backup.lock"

    with backup_target_lock(target_root):
        assert lock_path.exists()
        assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600
