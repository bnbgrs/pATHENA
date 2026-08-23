from __future__ import annotations

from pathlib import Path

import pytest

from athena.backup.target_lock import BackupTargetBusyError, backup_target_lock


def test_backup_target_lock_rejects_non_path_before_filesystem_access() -> None:
    with pytest.raises(TypeError):
        with backup_target_lock("not-a-path"):  # type: ignore[arg-type]
            raise AssertionError("invalid target must never enter lock body")


def test_backup_target_lock_rejects_missing_target(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(RuntimeError, match="unavailable"):
        with backup_target_lock(missing):
            raise AssertionError("missing target must never enter lock body")


def test_backup_target_lock_wraps_lockfile_open_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "backup"
    target.mkdir()
    original_open = Path.open

    def failing_open(path: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if path.name == ".athena-backup.lock":
            raise PermissionError("denied")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)

    with pytest.raises(BackupTargetBusyError, match="cannot be opened safely"):
        with backup_target_lock(target):
            raise AssertionError("failed lock open must never enter lock body")


def test_backup_target_lock_enters_and_releases_normally(tmp_path: Path) -> None:
    target = tmp_path / "backup"
    target.mkdir()

    entered = False
    with backup_target_lock(target):
        entered = True
        assert (target / ".athena-backup.lock").is_file()

    assert entered is True
