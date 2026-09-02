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


def test_posix_durable_write_bytes_does_not_write_payload_after_parent_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    destination = parent / "state.json"
    destination.write_bytes(b"old")
    displaced = tmp_path / "displaced"

    real_open = os.open
    replaced_parent = False

    def racing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced_parent
        if dir_fd is not None and not replaced_parent:
            replaced_parent = True
            parent.rename(displaced)
            parent.mkdir()
            (parent / "state.json").write_bytes(b"attacker")
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(durable_fs.os, "open", racing_open)

    with pytest.raises(OSError, match="changed during durable filesystem mutation"):
        durable_fs.durable_write_bytes(destination, b"trusted")

    assert (parent / "state.json").read_bytes() == b"attacker"
    assert (displaced / "state.json").read_bytes() == b"old"
    assert not tuple(displaced.glob("*.partial"))
    assert not tuple(displaced.glob(".*.partial"))


def test_posix_durable_write_bytes_replaces_existing_file(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    destination = parent / "state.json"
    destination.write_bytes(b"old")

    durable_fs.durable_write_bytes(destination, b"new")

    assert destination.read_bytes() == b"new"


def test_posix_durable_mkdir_does_not_create_inside_replaced_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    destination = parent / "trusted-child"
    displaced = tmp_path / "displaced"

    real_mkdir = os.mkdir
    replaced_parent = False

    def racing_mkdir(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> None:
        nonlocal replaced_parent
        if dir_fd is not None and not replaced_parent:
            replaced_parent = True
            parent.rename(displaced)
            parent.mkdir()
        if dir_fd is None:
            real_mkdir(path, mode)
        else:
            real_mkdir(path, mode, dir_fd=dir_fd)

    monkeypatch.setattr(durable_fs.os, "mkdir", racing_mkdir)

    with pytest.raises(OSError, match="changed during durable filesystem mutation"):
        durable_fs.durable_mkdir(destination)

    assert not (parent / "trusted-child").exists()
    assert (displaced / "trusted-child").is_dir()


def test_posix_durable_mkdir_preserves_nested_creation(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    destination = tmp_path / "one" / "two" / "three"

    durable_fs.durable_mkdir(destination, parents=True)

    assert destination.is_dir()
