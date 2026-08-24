from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import pytest

from athena.backup import target_lock
from athena.backup.target_lock import BackupTargetBusyError, backup_target_lock


@dataclass
class _Handle:
    closed: bool = False

    def close(self) -> None:
        self.closed = True


@dataclass
class _LockPath:
    handle: _Handle

    def open(self, mode: str) -> _Handle:
        assert mode == "a+b"
        return self.handle


@dataclass
class _TargetRoot:
    handle: _Handle
    available: bool = True

    def is_dir(self) -> bool:
        return self.available

    def __truediv__(self, name: str) -> _LockPath:
        assert name == ".athena-backup.lock"
        return _LockPath(self.handle)


def test_lock_failure_still_closes_handle(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = _Handle()
    target = _TargetRoot(handle)
    unlock_calls = 0

    def fail_lock(_: Any) -> None:
        raise BackupTargetBusyError("busy")

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(target_lock, "_lock", fail_lock)
    monkeypatch.setattr(target_lock, "_unlock", record_unlock)

    with pytest.raises(BackupTargetBusyError, match="busy"):
        with backup_target_lock(cast(Any, target)):
            raise AssertionError("unreachable")

    assert handle.closed is True
    assert unlock_calls == 0


def test_unlock_failure_still_closes_handle(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = _Handle()
    target = _TargetRoot(handle)

    monkeypatch.setattr(target_lock, "_lock", lambda _: None)

    def fail_unlock(_: Any) -> None:
        raise OSError("unlock failed")

    monkeypatch.setattr(target_lock, "_unlock", fail_unlock)

    with pytest.raises(OSError, match="unlock failed"):
        with backup_target_lock(cast(Any, target)):
            pass

    assert handle.closed is True


def test_body_failure_unlocks_and_closes_handle(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = _Handle()
    target = _TargetRoot(handle)
    unlock_calls = 0

    monkeypatch.setattr(target_lock, "_lock", lambda _: None)

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(target_lock, "_unlock", record_unlock)

    with pytest.raises(RuntimeError, match="body failed"):
        with backup_target_lock(cast(Any, target)):
            raise RuntimeError("body failed")

    assert unlock_calls == 1
    assert handle.closed is True


def test_unavailable_target_never_opens_lock_handle(monkeypatch: pytest.MonkeyPatch) -> None:
    handle = _Handle()
    target = _TargetRoot(handle, available=False)
    lock_calls = 0

    def record_lock(_: Any) -> None:
        nonlocal lock_calls
        lock_calls += 1

    monkeypatch.setattr(target_lock, "_lock", record_lock)

    with pytest.raises(RuntimeError, match="unavailable"):
        with backup_target_lock(cast(Any, target)):
            pass

    assert lock_calls == 0
    assert handle.closed is False
