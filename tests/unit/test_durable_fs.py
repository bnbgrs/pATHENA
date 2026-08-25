from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

import athena.storage.durable_fs as durable_fs


def _directory_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")


def test_posix_replace_syncs_both_changed_parent_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_parent = tmp_path / "source"
    destination_parent = tmp_path / "destination"
    source_parent.mkdir()
    destination_parent.mkdir()
    source = source_parent / "payload.partial"
    destination = destination_parent / "payload.bin"
    source.write_bytes(b"durable payload")
    events: list[str] = []
    real_replace = os.replace
    real_fsync = os.fsync

    def tracked_replace(
        old: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        new: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        events.append("replace")
        real_replace(
            old,
            new,
            src_dir_fd=src_dir_fd,
            dst_dir_fd=dst_dir_fd,
        )

    def tracked_fsync(descriptor: int) -> None:
        events.append("fsync")
        real_fsync(descriptor)

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: False)
    monkeypatch.setattr(durable_fs.os, "replace", tracked_replace)
    monkeypatch.setattr(durable_fs.os, "fsync", tracked_fsync)

    durable_fs.durable_replace(source, destination)

    assert destination.read_bytes() == b"durable payload"
    assert not source.exists()
    assert events == ["replace", "fsync", "fsync"]


def test_posix_same_directory_replace_syncs_parent_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "payload.partial"
    destination = tmp_path / "payload.bin"
    source.write_bytes(b"new")
    destination.write_bytes(b"old")
    real_fsync = os.fsync
    sync_count = 0

    def tracked_fsync(descriptor: int) -> None:
        nonlocal sync_count
        sync_count += 1
        real_fsync(descriptor)

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: False)
    monkeypatch.setattr(durable_fs.os, "fsync", tracked_fsync)

    durable_fs.durable_replace(source, destination)

    assert destination.read_bytes() == b"new"
    assert sync_count == 1


def test_replace_rejects_symlink_source(tmp_path: Path) -> None:
    target = tmp_path / "real"
    target.write_bytes(b"data")
    source = tmp_path / "source"
    source.symlink_to(target)
    with pytest.raises(OSError, match="source is a symlink"):
        durable_fs.durable_replace(source, tmp_path / "destination")
    assert target.read_bytes() == b"data"


def test_replace_rejects_symlink_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"new")
    target = tmp_path / "real"
    target.write_bytes(b"old")
    destination = tmp_path / "destination"
    destination.symlink_to(target)
    with pytest.raises(OSError, match="destination is a symlink"):
        durable_fs.durable_replace(source, destination)
    assert source.read_bytes() == b"new"
    assert target.read_bytes() == b"old"


def test_replace_rejects_symlink_destination_ancestor(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"new")
    real = tmp_path / "real"
    real.mkdir()
    child = real / "child"
    child.mkdir()
    link = tmp_path / "link"
    _directory_symlink(link, real)

    with pytest.raises(NotADirectoryError, match="symlink ancestor"):
        durable_fs.durable_replace(source, link / "child" / "destination")

    assert source.read_bytes() == b"new"
    assert not (child / "destination").exists()


def test_windows_reparse_attribute_is_link_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    monkeypatch.setattr(durable_fs.os, "name", "nt")
    monkeypatch.setattr(Path, "is_symlink", lambda _self: False)
    if hasattr(Path, "is_junction"):
        monkeypatch.setattr(Path, "is_junction", lambda _self: False)
    monkeypatch.setattr(
        durable_fs.os,
        "lstat",
        lambda _path: SimpleNamespace(
            st_file_attributes=durable_fs._FILE_ATTRIBUTE_REPARSE_POINT
        ),
    )

    assert durable_fs._is_link_boundary(candidate)


def test_replace_rejects_reparse_destination_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    source.write_bytes(b"new")
    destination = tmp_path / "destination"
    real_boundary = durable_fs.is_link_boundary

    def simulated_boundary(path: Path) -> bool:
        if Path(path) == destination:
            return True
        return real_boundary(Path(path))

    monkeypatch.setattr(durable_fs, "is_link_boundary", simulated_boundary)

    with pytest.raises(OSError, match="destination is a symlink or reparse point"):
        durable_fs.durable_replace(source, destination)

    assert source.read_bytes() == b"new"
    assert not destination.exists()


def test_fsync_directory_rejects_symlink(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _directory_symlink(link, real)
    with pytest.raises(NotADirectoryError, match="unsafe"):
        durable_fs.fsync_directory(link)


def test_fsync_directory_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    child = real / "child"
    child.mkdir()
    link = tmp_path / "link"
    _directory_symlink(link, real)

    with pytest.raises(NotADirectoryError, match="symlink ancestor"):
        durable_fs.fsync_directory(link / "child")


def test_durable_mkdir_rejects_existing_non_directory(tmp_path: Path) -> None:
    target = tmp_path / "not-a-directory"
    target.write_text("file", encoding="utf-8")
    with pytest.raises(FileExistsError):
        durable_fs.durable_mkdir(target, parents=True, exist_ok=True)


def test_durable_mkdir_rejects_existing_directory_beneath_symlink_ancestor(
    tmp_path: Path,
) -> None:
    real = tmp_path / "real"
    real.mkdir()
    child = real / "child"
    child.mkdir()
    link = tmp_path / "link"
    _directory_symlink(link, real)

    with pytest.raises(NotADirectoryError, match="symlink ancestor"):
        durable_fs.durable_mkdir(link / "child", parents=True, exist_ok=True)


def test_posix_durable_mkdir_syncs_each_new_parent_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "one" / "two" / "three"
    real_fsync = os.fsync
    sync_count = 0

    def tracked_fsync(descriptor: int) -> None:
        nonlocal sync_count
        sync_count += 1
        real_fsync(descriptor)

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: False)
    monkeypatch.setattr(durable_fs.os, "fsync", tracked_fsync)

    durable_fs.durable_mkdir(target, parents=True, exist_ok=True)

    assert target.is_dir()
    assert sync_count == 3


def test_windows_route_uses_write_through_primitive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.partial"
    destination = tmp_path / "destination.bin"
    source.write_bytes(b"x")
    called: list[tuple[Path, Path]] = []
    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(
        durable_fs,
        "_windows_replace_write_through",
        lambda old, new: called.append((Path(old), Path(new))),
    )
    durable_fs.durable_replace(source, destination)
    assert called == [(source, destination)]


@pytest.mark.skipif(os.name != "nt", reason="Windows MoveFileExW behavior")
def test_windows_write_through_replaces_existing_file(tmp_path: Path) -> None:
    source = tmp_path / "source.partial"
    destination = tmp_path / "destination.bin"
    source.write_bytes(b"replacement")
    destination.write_bytes(b"old")
    durable_fs.durable_replace(source, destination)
    assert not source.exists()
    assert destination.read_bytes() == b"replacement"


@pytest.mark.skipif(
    os.name != "nt",
    reason="Windows MoveFileExW durable directory creation",
)
def test_windows_durable_mkdir_creates_nested_tree(tmp_path: Path) -> None:
    target = tmp_path / "first" / "second" / "third"
    durable_fs.durable_mkdir(target, parents=True, exist_ok=True)
    assert target.is_dir()
    durable_fs.durable_mkdir(target, parents=True, exist_ok=True)
