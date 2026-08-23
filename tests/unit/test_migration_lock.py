from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import athena.storage.migration_lock as migration_lock_module
from athena.storage.migration_lock import MigrationBusyError, migration_lock


def test_migration_lock_acquires_and_releases(tmp_path: Path) -> None:
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    lock_path = root / ".athena-migration.lock"

    with migration_lock(root):
        assert lock_path.is_file()
        if os.name == "posix":
            assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600

    with migration_lock(root):
        assert lock_path.is_file()


def test_migration_lock_rejects_symlink_root(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "migration"
    try:
        link.symlink_to(real, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")

    with pytest.raises(MigrationBusyError, match="symlink|junction|reparse"):
        with migration_lock(link.absolute()):
            raise AssertionError("unreachable")


def test_migration_lock_rejects_reparse_root_before_open(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    original = migration_lock_module.is_link_boundary

    def simulate_reparse(path: Path) -> bool:
        return path == root or original(path)

    open_attempted = False
    original_open = migration_lock_module.os.open

    def track_open(*args: object, **kwargs: object) -> int:
        nonlocal open_attempted
        open_attempted = True
        return original_open(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(migration_lock_module, "is_link_boundary", simulate_reparse)
    monkeypatch.setattr(migration_lock_module.os, "open", track_open)

    with pytest.raises(MigrationBusyError, match="reparse-point ancestor"):
        with migration_lock(root):
            raise AssertionError("unreachable")

    assert open_attempted is False


def test_migration_lock_rejects_symlink_lock_file(tmp_path: Path) -> None:
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    target = tmp_path / "target.lock"
    target.write_bytes(b"unchanged")
    lock_path = root / ".athena-migration.lock"
    try:
        lock_path.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"file symlink unavailable: {exc}")

    with pytest.raises(MigrationBusyError, match="symlink|junction|reparse"):
        with migration_lock(root):
            raise AssertionError("unreachable")

    assert target.read_bytes() == b"unchanged"


def test_migration_lock_rejects_path_replacement_after_lock(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = (tmp_path / "migration").absolute()
    root.mkdir()
    real_assert = migration_lock_module._assert_handle_matches_path
    calls = 0

    def fail_second_identity_check(path: Path, handle: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise MigrationBusyError("Migration lock pathname changed during acquisition.")
        real_assert(path, handle)  # type: ignore[arg-type]

    monkeypatch.setattr(
        migration_lock_module,
        "_assert_handle_matches_path",
        fail_second_identity_check,
    )

    entered = False
    with pytest.raises(MigrationBusyError, match="pathname changed"):
        with migration_lock(root):
            entered = True

    assert entered is False
    assert calls == 2


def test_migration_lock_rejects_missing_root(tmp_path: Path) -> None:
    root = (tmp_path / "missing").absolute()

    with pytest.raises(MigrationBusyError, match="existing directory"):
        with migration_lock(root):
            raise AssertionError("unreachable")
