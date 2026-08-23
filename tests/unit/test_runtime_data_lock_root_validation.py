from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from athena.lifecycle.runtime_lock import RuntimeDataLockError, runtime_data_lock


def test_runtime_data_lock_allows_explicit_none() -> None:
    entered = False
    with runtime_data_lock(None):
        entered = True
    assert entered is True


@pytest.mark.parametrize("value", [True, False, 1, 1.5, "state", object()])
def test_runtime_data_lock_rejects_non_path_root(value: Any) -> None:
    with pytest.raises(TypeError):
        with runtime_data_lock(value):  # type: ignore[arg-type]
            raise AssertionError("invalid root must never enter lock body")


def test_runtime_data_lock_wraps_root_mkdir_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "state"
    original_mkdir = Path.mkdir

    def failing_mkdir(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if path == root:
            raise PermissionError("denied")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", failing_mkdir)

    with pytest.raises(RuntimeDataLockError, match="cannot be prepared"):
        with runtime_data_lock(root):
            raise AssertionError("failed root preparation must never enter lock body")


def test_runtime_data_lock_rejects_symlink_root(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable in this environment")

    with pytest.raises(RuntimeDataLockError, match="unavailable"):
        with runtime_data_lock(link):
            raise AssertionError("symlink root must never enter lock body")


def test_runtime_data_lock_accepts_real_directory(tmp_path: Path) -> None:
    root = tmp_path / "state"
    entered = False

    with runtime_data_lock(root):
        entered = True
        assert (root / ".athena-runtime-data.lock").is_file()

    assert entered is True
