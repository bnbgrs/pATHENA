from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.runtime import RuntimeLayoutService, RuntimePathError


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlink unavailable: {exc}")


def test_ensure_directory_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)
    target = link / "state" / "spool"

    with pytest.raises(RuntimePathError, match="symlink ancestor"):
        RuntimeLayoutService._ensure_directory(target)

    assert not (real / "state").exists()


def test_verify_writable_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    child = real / "child"
    child.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(RuntimePathError, match="symlink ancestor"):
        RuntimeLayoutService._verify_writable(link / "child")


def test_runtime_path_helpers_reject_non_path() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        RuntimeLayoutService._ensure_directory("state")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="pathlib.Path"):
        RuntimeLayoutService._verify_writable("state")  # type: ignore[arg-type]
