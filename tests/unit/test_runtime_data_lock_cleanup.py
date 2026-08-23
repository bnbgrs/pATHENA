from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

from athena.lifecycle import runtime_lock
from athena.lifecycle.runtime_lock import RuntimeDataLockError, runtime_data_lock


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
class _Root:
    handle: _Handle
    key: str = "/state"

    def expanduser(self) -> _Root:
        return self

    def mkdir(self, *, parents: bool, exist_ok: bool) -> None:
        assert parents is True
        assert exist_ok is True

    def is_symlink(self) -> bool:
        return False

    def is_dir(self) -> bool:
        return True

    def resolve(self) -> Path:
        return Path(self.key)

    def __truediv__(self, name: str) -> _LockPath:
        assert name == ".athena-runtime-data.lock"
        return _LockPath(self.handle)


def _clear_thread_state() -> None:
    runtime_lock._THREAD_STATE.depths.clear()


def test_runtime_lock_acquire_failure_closes_handle_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    root = _Root(handle)
    unlock_calls = 0

    def fail_lock(_: Any) -> None:
        raise OSError("lock failed")

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(runtime_lock, "_lock_platform", fail_lock)
    monkeypatch.setattr(runtime_lock, "_unlock_platform", record_unlock)

    with pytest.raises(RuntimeDataLockError, match="cannot be acquired"):
        with runtime_data_lock(cast(Any, root)):
            raise AssertionError("unreachable")

    assert handle.closed is True
    assert unlock_calls == 0
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_unlock_failure_still_closes_handle_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    root = _Root(handle)
    monkeypatch.setattr(runtime_lock, "_lock_platform", lambda _: None)

    def fail_unlock(_: Any) -> None:
        raise OSError("unlock failed")

    monkeypatch.setattr(runtime_lock, "_unlock_platform", fail_unlock)

    with pytest.raises(RuntimeDataLockError, match="released cleanly"):
        with runtime_data_lock(cast(Any, root)):
            pass

    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_body_failure_unlocks_closes_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    root = _Root(handle)
    unlock_calls = 0
    monkeypatch.setattr(runtime_lock, "_lock_platform", lambda _: None)

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(runtime_lock, "_unlock_platform", record_unlock)

    with pytest.raises(RuntimeError, match="body failed"):
        with runtime_data_lock(cast(Any, root)):
            raise RuntimeError("body failed")

    assert unlock_calls == 1
    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_nested_scope_reuses_outer_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    root = _Root(handle)
    lock_calls = 0
    unlock_calls = 0

    def record_lock(_: Any) -> None:
        nonlocal lock_calls
        lock_calls += 1

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(runtime_lock, "_lock_platform", record_lock)
    monkeypatch.setattr(runtime_lock, "_unlock_platform", record_unlock)

    with runtime_data_lock(cast(Any, root)):
        assert len(runtime_lock._THREAD_STATE.depths) == 1
        with runtime_data_lock(cast(Any, root)):
            assert list(runtime_lock._THREAD_STATE.depths.values()) == [2]
        assert list(runtime_lock._THREAD_STATE.depths.values()) == [1]

    assert lock_calls == 1
    assert unlock_calls == 1
    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}
