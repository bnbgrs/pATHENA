from __future__ import annotations

import os
from pathlib import Path

import pytest

import athena.storage.durable_fs as durable_fs


def test_posix_durable_unlink_deletes_and_syncs_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "lease.json"
    target.write_bytes(b"lease")
    real_fsync = os.fsync
    sync_count = 0

    def tracked_fsync(descriptor: int) -> None:
        nonlocal sync_count
        sync_count += 1
        real_fsync(descriptor)

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: False)
    monkeypatch.setattr(durable_fs.os, "fsync", tracked_fsync)

    durable_fs.durable_unlink(target)

    assert not target.exists()
    assert sync_count == 1


def test_posix_durable_unlink_stays_bound_during_parent_replacement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    parent = tmp_path / "parent"
    parent.mkdir()
    target = parent / "lease.json"
    target.write_bytes(b"trusted")
    displaced = tmp_path / "displaced"
    real_unlink = os.unlink
    replaced_parent = False

    def racing_unlink(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        dir_fd: int | None = None,
    ) -> None:
        nonlocal replaced_parent
        if dir_fd is not None and not replaced_parent:
            replaced_parent = True
            parent.rename(displaced)
            parent.mkdir()
            (parent / "lease.json").write_bytes(b"attacker")
        if dir_fd is None:
            real_unlink(path)
        else:
            real_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: False)
    monkeypatch.setattr(durable_fs.os, "unlink", racing_unlink)

    with pytest.raises(OSError, match="changed during durable filesystem mutation"):
        durable_fs.durable_unlink(target)

    assert (parent / "lease.json").read_bytes() == b"attacker"
    assert not (displaced / "lease.json").exists()


def test_durable_unlink_missing_ok_preserves_idempotence(tmp_path: Path) -> None:
    durable_fs.durable_unlink(tmp_path / "missing.json", missing_ok=True)


def test_durable_unlink_rejects_non_boolean_missing_ok(tmp_path: Path) -> None:
    target = tmp_path / "lease.json"
    target.write_bytes(b"lease")

    with pytest.raises(ValueError, match="missing_ok"):
        durable_fs.durable_unlink(target, missing_ok=1)  # type: ignore[arg-type]

    assert target.exists()


def test_windows_durable_unlink_routes_to_handle_bound_primitive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "lease.json"
    target.write_bytes(b"lease")
    calls: list[Path] = []

    monkeypatch.setattr(durable_fs, "_is_windows", lambda: True)
    monkeypatch.setattr(
        durable_fs,
        "_windows_unlink_bound",
        lambda path: calls.append(Path(path)),
    )

    durable_fs.durable_unlink(target)

    assert calls == [target]


@pytest.mark.skipif(os.name != "nt", reason="Windows HANDLE-bound delete behavior")
def test_windows_durable_unlink_deletes_real_file(tmp_path: Path) -> None:
    target = tmp_path / "lease.json"
    target.write_bytes(b"lease")

    durable_fs.durable_unlink(target)

    assert not target.exists()
