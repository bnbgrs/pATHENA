from __future__ import annotations

from pathlib import Path

import pytest

from athena.lifecycle.runtime_lock import RuntimeDataLockError, runtime_data_lock


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlink unavailable: {exc}")


def test_runtime_data_lock_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(RuntimeDataLockError, match="symbolic-link ancestor"):
        with runtime_data_lock(link / "state"):
            raise AssertionError("unreachable")

    assert not (real / "state").exists()


def test_runtime_data_lock_rejects_symlink_lock_file(tmp_path: Path) -> None:
    state = tmp_path / "state"
    state.mkdir()
    target = tmp_path / "target.lock"
    target.write_bytes(b"do-not-touch")
    lock_path = state / ".athena-runtime-data.lock"
    try:
        lock_path.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"File symlink unavailable: {exc}")

    with pytest.raises(RuntimeDataLockError, match="symbolic link"):
        with runtime_data_lock(state):
            raise AssertionError("unreachable")

    assert target.read_bytes() == b"do-not-touch"


def test_runtime_data_lock_rejects_non_path() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        with runtime_data_lock("state"):  # type: ignore[arg-type]
            raise AssertionError("unreachable")
