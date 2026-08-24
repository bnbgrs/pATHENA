from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.runtime import RuntimeLayoutService, RuntimePathError


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable in this environment")


def test_ensure_directory_rejects_existing_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "state"
    _symlink_directory(link, target)

    with pytest.raises(RuntimePathError, match="must not be a symlink"):
        RuntimeLayoutService._ensure_directory(link)


def test_verify_writable_rejects_symlink_before_probe(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "state"
    _symlink_directory(link, target)

    with pytest.raises(RuntimePathError, match="safe directory"):
        RuntimeLayoutService._verify_writable(link)

    assert list(target.glob(".athena-write-probe-*")) == []


def test_real_runtime_directory_is_created_and_writable(tmp_path: Path) -> None:
    directory = tmp_path / "state" / "spool"

    RuntimeLayoutService._ensure_directory(directory)
    RuntimeLayoutService._verify_writable(directory)

    assert directory.is_dir()
    assert not directory.is_symlink()
    assert list(directory.glob(".athena-write-probe-*")) == []
