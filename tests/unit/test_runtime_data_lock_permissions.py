from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from athena.lifecycle.runtime_lock import runtime_data_lock


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
