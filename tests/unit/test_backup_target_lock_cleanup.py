from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from athena.backup import target_lock
from athena.backup.target_lock import BackupTargetBusyError, backup_target_lock


@dataclass
class _Handle:
    closed: bool = False

    def close(self) -> None:
        self.closed = True


def _available_target(tmp_path: Path) -> Path:
    target = tmp_path / "backup-target"
    target.mkdir()
    return target


def test_lock_failure_still_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = _Handle()
    target = _available_target(tmp_path)
    unlock_calls = 0

    def fail_lock(_: Any) -> None:
        raise BackupTargetBusyError("busy")

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(target_lock, "_open_lock_file", lambda _: handle)
    monkeypatch.setattr(target_lock, "_lock", fail_lock)
    monkeypatch.setattr(target_lock, "_unlock", record_unlock)

    with pytest.raises(BackupTargetBusyError, match="busy"):
        with backup_target_lock(target):
            raise AssertionError("unreachable")

    assert handle.closed is True
    assert unlock_calls == 0


def test_unlock_failure_still_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = _Handle()
    target = _available_target(tmp_path)

    monkeypatch.setattr(target_lock, "_open_lock_file", lambda _: handle)
    monkeypatch.setattr(target_lock, "_lock", lambda _: None)

    def fail_unlock(_: Any) -> None:
        raise OSError("unlock failed")

    monkeypatch.setattr(target_lock, "_unlock", fail_unlock)

    with pytest.raises(OSError, match="unlock failed"):
        with backup_target_lock(target):
            pass

    assert handle.closed is True


def test_body_failure_unlocks_and_closes_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = _Handle()
    target = _available_target(tmp_path)
    unlock_calls = 0

    monkeypatch.setattr(target_lock, "_open_lock_file", lambda _: handle)
    monkeypatch.setattr(target_lock, "_lock", lambda _: None)

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(target_lock, "_unlock", record_unlock)

    with pytest.raises(RuntimeError, match="body failed"):
        with backup_target_lock(target):
            raise RuntimeError("body failed")

    assert unlock_calls == 1
    assert handle.closed is True


def test_unavailable_target_never_opens_lock_handle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    handle = _Handle()
    target = tmp_path / "missing-backup-target"
    open_calls = 0

    def record_open(_: Path) -> _Handle:
        nonlocal open_calls
        open_calls += 1
        return handle

    monkeypatch.setattr(target_lock, "_open_lock_file", record_open)

    with pytest.raises(RuntimeError, match="unavailable"):
        with backup_target_lock(target):
            pass

    assert open_calls == 0
    assert handle.closed is False
