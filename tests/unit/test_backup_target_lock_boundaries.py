from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import BinaryIO

import pytest

from athena.backup import target_lock as target_lock_module
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

    with pytest.raises(BackupTargetBusyError, match="symbolic-link ancestor"):
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


def test_backup_target_lock_rejects_path_replacement_during_acquisition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX pathname replacement assertion")

    target_root = tmp_path / "backup"
    target_root.mkdir()
    lock_path = target_root / ".athena-backup.lock"
    displaced_path = target_root / ".athena-backup.displaced"

    def replace_path(_handle: BinaryIO) -> None:
        lock_path.rename(displaced_path)
        lock_path.write_bytes(b"replacement")

    monkeypatch.setattr(target_lock_module, "_lock", replace_path)

    with pytest.raises(BackupTargetBusyError, match="pathname changed"):
        with backup_target_lock(target_root):
            raise AssertionError("unreachable")
