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


def test_windows_replace_binds_source_and_destination_parent_handles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source.partial"
    destination = tmp_path / "destination.bin"
    source.write_bytes(b"payload")
    opened: list[tuple[Path, int, bool, bool]] = []
    renamed: list[tuple[int, int, str, bool]] = []
    closed: list[int] = []

    def open_bound(
        path: Path,
        *,
        access: int,
        require_directory: bool,
        write_through: bool = False,
    ) -> int:
        opened.append((Path(path), access, require_directory, write_through))
        return 101 if Path(path) == source else 202

    def rename_relative(
        source_handle: int,
        destination_parent_handle: int,
        destination_name: str,
        *,
        replace_existing: bool,
    ) -> None:
        renamed.append(
            (
                source_handle,
                destination_parent_handle,
                destination_name,
                replace_existing,
            )
        )

    monkeypatch.setattr(durable_fs, "_windows_open_bound_handle", open_bound)
    monkeypatch.setattr(durable_fs, "_windows_rename_relative", rename_relative)
    monkeypatch.setattr(durable_fs, "_windows_close_handle", closed.append)

    durable_fs._windows_replace_write_through(source, destination)

    assert opened == [
        (
            source,
            durable_fs._DELETE | durable_fs._FILE_READ_ATTRIBUTES,
            False,
            True,
        ),
        (tmp_path, durable_fs._FILE_READ_ATTRIBUTES, True, False),
    ]
    assert renamed == [(101, 202, "destination.bin", True)]
    assert closed == [202, 101]


def test_windows_bound_delete_uses_exclusive_bound_handles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "emergency.reserve"
    target.write_bytes(b"x" * 4096)
    opened: list[tuple[Path, int, bool, bool, int]] = []
    marked: list[int] = []
    closed: list[int] = []

    def open_bound(
        path: Path,
        *,
        access: int,
        require_directory: bool,
        write_through: bool = False,
        share_mode: int = (
            durable_fs._FILE_SHARE_READ
            | durable_fs._FILE_SHARE_WRITE
            | durable_fs._FILE_SHARE_DELETE
        ),
    ) -> int:
        opened.append(
            (Path(path), access, require_directory, write_through, share_mode)
        )
        return 202 if Path(path) == tmp_path else 101

    def mark_delete(handle: int) -> None:
        marked.append(handle)
        target.unlink()

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(durable_fs, "_windows_open_bound_handle", open_bound)
    monkeypatch.setattr(
        durable_fs,
        "_windows_bound_file_size_and_links",
        lambda handle: (4096, 1) if handle == 101 else (_ for _ in ()).throw(
            AssertionError("unexpected handle")
        ),
    )
    monkeypatch.setattr(durable_fs, "_windows_mark_file_delete", mark_delete)
    monkeypatch.setattr(durable_fs, "_windows_close_handle", closed.append)

    released = durable_fs.windows_delete_bound_file(target)

    assert released == 4096
    assert opened == [
        (
            tmp_path,
            durable_fs._FILE_READ_ATTRIBUTES,
            True,
            False,
            durable_fs._FILE_SHARE_READ | durable_fs._FILE_SHARE_WRITE,
        ),
        (
            target,
            durable_fs._DELETE | durable_fs._FILE_READ_ATTRIBUTES,
            False,
            True,
            0,
        ),
    ]
    assert marked == [101]
    assert closed == [101, 202]
    assert not target.exists()


def test_windows_bound_delete_fails_closed_on_leaf_substitution_seam(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "emergency.reserve"
    target.write_bytes(b"trusted")
    displaced = tmp_path / "expected.reserve"
    closed: list[int] = []

    def open_bound(
        path: Path,
        *,
        access: int,
        require_directory: bool,
        write_through: bool = False,
        share_mode: int = (
            durable_fs._FILE_SHARE_READ
            | durable_fs._FILE_SHARE_WRITE
            | durable_fs._FILE_SHARE_DELETE
        ),
    ) -> int:
        return 202 if Path(path) == tmp_path else 101

    def race_then_delete_bound(_handle: int) -> None:
        target.rename(displaced)
        target.write_bytes(b"attacker")
        displaced.unlink()

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(durable_fs, "_windows_open_bound_handle", open_bound)
    monkeypatch.setattr(
        durable_fs,
        "_windows_bound_file_size_and_links",
        lambda _handle: (len(b"trusted"), 1),
    )
    monkeypatch.setattr(
        durable_fs,
        "_windows_mark_file_delete",
        race_then_delete_bound,
    )
    monkeypatch.setattr(durable_fs, "_windows_close_handle", closed.append)

    with pytest.raises(OSError, match="pathname still exists"):
        durable_fs.windows_delete_bound_file(target)

    assert target.read_bytes() == b"attacker"
    assert not displaced.exists()
    assert closed == [101, 202]


def test_windows_bound_delete_rejects_additional_hard_links(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "emergency.reserve"
    target.write_bytes(b"trusted")
    marked = False
    closed: list[int] = []

    def open_bound(
        path: Path,
        *,
        access: int,
        require_directory: bool,
        write_through: bool = False,
        share_mode: int = (
            durable_fs._FILE_SHARE_READ
            | durable_fs._FILE_SHARE_WRITE
            | durable_fs._FILE_SHARE_DELETE
        ),
    ) -> int:
        return 202 if Path(path) == tmp_path else 101

    def mark_delete(_handle: int) -> None:
        nonlocal marked
        marked = True

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(durable_fs, "_windows_open_bound_handle", open_bound)
    monkeypatch.setattr(
        durable_fs,
        "_windows_bound_file_size_and_links",
        lambda _handle: (len(b"trusted"), 2),
    )
    monkeypatch.setattr(durable_fs, "_windows_mark_file_delete", mark_delete)
    monkeypatch.setattr(durable_fs, "_windows_close_handle", closed.append)

    with pytest.raises(OSError, match="additional hard links"):
        durable_fs.windows_delete_bound_file(target)

    assert marked is False
    assert target.read_bytes() == b"trusted"
    assert closed == [101, 202]


@pytest.mark.skipif(os.name != "nt", reason="Windows HANDLE-bound delete behavior")
def test_windows_bound_delete_blocks_leaf_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "emergency.reserve"
    target.write_bytes(b"trusted reserve")
    displaced = tmp_path / "expected.reserve"
    real_mark_delete = durable_fs._windows_mark_file_delete
    replacement_blocked = False

    def race_then_delete(handle: int) -> None:
        nonlocal replacement_blocked
        try:
            target.rename(displaced)
        except OSError:
            replacement_blocked = True
        else:
            raise AssertionError(
                "exclusive bound reserve HANDLE allowed pathname replacement"
            )
        real_mark_delete(handle)

    monkeypatch.setattr(durable_fs, "_windows_mark_file_delete", race_then_delete)

    released = durable_fs.windows_delete_bound_file(target)

    assert replacement_blocked is True
    assert released == len(b"trusted reserve")
    assert not target.exists()
    assert not displaced.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows HANDLE-bound rename behavior")
def test_windows_handle_bound_replace_cannot_redirect_to_replaced_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_parent = tmp_path / "source-parent"
    destination_parent = tmp_path / "destination-parent"
    source_parent.mkdir()
    destination_parent.mkdir()
    source = source_parent / "payload.partial"
    destination = destination_parent / "payload.bin"
    source.write_bytes(b"trusted")

    displaced_parent = tmp_path / "destination-parent-original"
    real_rename_relative = durable_fs._windows_rename_relative

    def race_then_rename(
        source_handle: int,
        destination_parent_handle: int,
        destination_name: str,
        *,
        replace_existing: bool,
    ) -> None:
        destination_parent.rename(displaced_parent)
        destination_parent.mkdir()
        (destination_parent / destination_name).write_bytes(b"attacker")
        real_rename_relative(
            source_handle,
            destination_parent_handle,
            destination_name,
            replace_existing=replace_existing,
        )

    monkeypatch.setattr(durable_fs, "_windows_rename_relative", race_then_rename)

    durable_fs._windows_replace_write_through(source, destination)

    assert not source.exists()
    assert (displaced_parent / destination.name).read_bytes() == b"trusted"
    assert destination.read_bytes() == b"attacker"


@pytest.mark.skipif(os.name != "nt", reason="Windows HANDLE-bound rename behavior")
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
    reason="Windows HANDLE-bound durable directory creation",
)
def test_windows_durable_mkdir_creates_nested_tree(tmp_path: Path) -> None:
    target = tmp_path / "first" / "second" / "third"
    durable_fs.durable_mkdir(target, parents=True, exist_ok=True)
    assert target.is_dir()
    durable_fs.durable_mkdir(target, parents=True, exist_ok=True)

def test_durable_publish_new_bytes_never_replaces_existing_history(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "commit.json"

    durable_fs.durable_publish_new_bytes(destination, b"first")

    assert destination.read_bytes() == b"first"
    with pytest.raises(FileExistsError):
        durable_fs.durable_publish_new_bytes(destination, b"second")
    assert destination.read_bytes() == b"first"


def test_durable_publish_new_bytes_rejects_symlink_destination(
    tmp_path: Path,
) -> None:
    target = tmp_path / "real.json"
    target.write_bytes(b"trusted")
    destination = tmp_path / "commit.json"
    try:
        destination.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"file symlink unavailable: {exc}")

    with pytest.raises(FileExistsError, match="symlink or reparse point"):
        durable_fs.durable_publish_new_bytes(destination, b"attacker")

    assert target.read_bytes() == b"trusted"


def test_windows_new_file_route_uses_no_replace_write_through(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "commit.json"
    called: list[tuple[Path, Path]] = []

    def publish(source: Path, target: Path) -> None:
        called.append((Path(source), Path(target)))

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(
        durable_fs,
        "_windows_publish_new_write_through",
        publish,
    )

    durable_fs.durable_publish_new_bytes(destination, b"payload")

    assert len(called) == 1
    source, target = called[0]
    assert source.parent == tmp_path
    assert source.name.startswith(".commit.json.")
    assert source.name.endswith(".partial")
    assert target == destination
    assert not source.exists()
    assert not destination.exists()


def test_windows_publish_new_binds_handles_without_replace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "commit.partial"
    destination = tmp_path / "commit.json"
    source.write_bytes(b"payload")
    opened: list[tuple[Path, int, bool, bool]] = []
    renamed: list[tuple[int, int, str, bool]] = []
    closed: list[int] = []

    def open_bound(
        path: Path,
        *,
        access: int,
        require_directory: bool,
        write_through: bool = False,
    ) -> int:
        opened.append((Path(path), access, require_directory, write_through))
        return 101 if Path(path) == source else 202

    def rename_relative(
        source_handle: int,
        destination_parent_handle: int,
        destination_name: str,
        *,
        replace_existing: bool,
    ) -> None:
        renamed.append(
            (
                source_handle,
                destination_parent_handle,
                destination_name,
                replace_existing,
            )
        )

    monkeypatch.setattr(durable_fs, "_windows_open_bound_handle", open_bound)
    monkeypatch.setattr(durable_fs, "_windows_rename_relative", rename_relative)
    monkeypatch.setattr(durable_fs, "_windows_close_handle", closed.append)

    durable_fs._windows_publish_new_write_through(source, destination)

    assert opened == [
        (
            source,
            durable_fs._DELETE | durable_fs._FILE_READ_ATTRIBUTES,
            False,
            True,
        ),
        (tmp_path, durable_fs._FILE_READ_ATTRIBUTES, True, False),
    ]
    assert renamed == [(101, 202, "commit.json", False)]
    assert closed == [202, 101]

