from __future__ import annotations

import os
from pathlib import Path

import pytest

import athena.storage.durable_fs as durable_fs


def test_posix_durable_replace_stays_bound_to_open_parent_on_path_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    source = parent / "source"
    destination = parent / "destination"
    source.write_bytes(b"trusted")

    displaced = tmp_path / "displaced"
    real_replace = os.replace
    replaced_parent = False

    def racing_replace(
        src: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        dst: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        nonlocal replaced_parent
        if not replaced_parent:
            replaced_parent = True
            parent.rename(displaced)
            parent.mkdir()
            (parent / "source").write_bytes(b"attacker")
        real_replace(
            src,
            dst,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
        )

    monkeypatch.setattr(durable_fs.os, "replace", racing_replace)

    with pytest.raises(OSError, match="changed during durable filesystem mutation"):
        durable_fs.durable_replace(source, destination)

    assert (parent / "source").read_bytes() == b"attacker"
    assert not (parent / "destination").exists()
    assert not (displaced / "source").exists()
    assert (displaced / "destination").read_bytes() == b"trusted"


def test_posix_durable_replace_preserves_normal_atomic_publication(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    source = parent / "source"
    destination = parent / "destination"
    source.write_bytes(b"new")
    destination.write_bytes(b"old")

    durable_fs.durable_replace(source, destination)

    assert not source.exists()
    assert destination.read_bytes() == b"new"
