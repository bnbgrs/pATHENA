from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import athena.api.process as process_module
from athena.api.process import CoreApiProcessOwnershipError


def test_core_api_lock_rejects_symlink_lock_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(process_module.tempfile, "gettempdir", lambda: str(tmp_path))
    real = tmp_path / "real-locks"
    real.mkdir()
    lock_dir = tmp_path / process_module._LOCK_DIRECTORY_NAME
    try:
        lock_dir.symlink_to(real, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")

    with pytest.raises(CoreApiProcessOwnershipError, match="symlink ancestor"):
        process_module._CoreApiProcessLock.acquire(tmp_path / "local")


def test_core_api_lock_rejects_symlink_lock_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(process_module.tempfile, "gettempdir", lambda: str(tmp_path))
    local_root = tmp_path / "local"
    lock_path = process_module._ownership_lock_path(local_root)
    lock_path.parent.mkdir(parents=True)
    foreign = tmp_path / "foreign.lock"
    foreign.write_bytes(b"foreign")
    try:
        lock_path.symlink_to(foreign)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"file symlink unavailable: {exc}")

    with pytest.raises(CoreApiProcessOwnershipError, match="must not be a symlink"):
        process_module._CoreApiProcessLock.acquire(local_root)

    assert foreign.read_bytes() == b"foreign"


def test_core_api_lock_secures_existing_file_permissions_on_posix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX file-mode assertion")

    monkeypatch.setattr(process_module.tempfile, "gettempdir", lambda: str(tmp_path))
    local_root = tmp_path / "local"
    lock_path = process_module._ownership_lock_path(local_root)
    lock_path.parent.mkdir(parents=True)
    lock_path.write_bytes(b"\0")
    lock_path.chmod(0o666)

    lock = process_module._CoreApiProcessLock.acquire(local_root)
    try:
        assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600
    finally:
        lock.close()


def test_core_api_lock_close_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(process_module.tempfile, "gettempdir", lambda: str(tmp_path))
    lock = process_module._CoreApiProcessLock.acquire(tmp_path / "local")

    lock.close()
    lock.close()
