from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import BinaryIO

import pytest

from athena.lifecycle import runtime_lock as runtime_lock_module
from athena.lifecycle.runtime_lock import RuntimeDataLockError, runtime_data_lock


def test_runtime_data_lock_file_has_owner_only_permissions_on_posix(
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX file-mode assertion")

    state_root = tmp_path / "state"
    state_root.mkdir()
    lock_path = state_root / ".athena-runtime-data.lock"
    lock_path.write_bytes(b"")
    lock_path.chmod(0o666)

    with runtime_data_lock(state_root):
        assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600


def test_runtime_data_lock_rejects_path_replacement_during_acquisition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX pathname replacement assertion")

    state_root = tmp_path / "state"
    state_root.mkdir()
    lock_path = state_root / ".athena-runtime-data.lock"
    displaced_path = state_root / ".athena-runtime-data.displaced"

    def replace_path(_handle: BinaryIO) -> None:
        lock_path.rename(displaced_path)
        lock_path.write_bytes(b"replacement")

    monkeypatch.setattr(runtime_lock_module, "_lock_platform", replace_path)

    with pytest.raises(RuntimeDataLockError, match="pathname changed"):
        with runtime_data_lock(state_root):
            raise AssertionError("unreachable")
