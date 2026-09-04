from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from athena.lifecycle import runtime_lock
from athena.lifecycle.runtime_lock import RuntimeDataLockError, runtime_data_lock


@dataclass
class _Handle:
    closed: bool = False

    def close(self) -> None:
        self.closed = True


def _clear_thread_state() -> None:
    runtime_lock._THREAD_STATE.depths.clear()


def _fake_open(
    monkeypatch: pytest.MonkeyPatch,
    handle: _Handle,
) -> None:
    def open_handle(path: Path) -> _Handle:
        assert path.name == ".athena-runtime-data.lock"
        return handle

    # These cleanup tests isolate lock lifecycle behavior from the separately
    # covered pathname/handle-identity boundary. Production still uses the
    # hardened os.open/fstat path in _open_lock_file.
    monkeypatch.setattr(runtime_lock, "_open_lock_file", open_handle)
    monkeypatch.setattr(runtime_lock, "_assert_handle_matches_path", lambda *_: None)


def test_runtime_lock_acquire_failure_closes_handle_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    _fake_open(monkeypatch, handle)
    unlock_calls = 0

    def fail_lock(_: Any) -> None:
        raise OSError("lock failed")

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(runtime_lock, "_lock_platform", fail_lock)
    monkeypatch.setattr(runtime_lock, "_unlock_platform", record_unlock)

    with pytest.raises(RuntimeDataLockError, match="cannot be acquired"):
        with runtime_data_lock(tmp_path):
            raise AssertionError("unreachable")

    assert handle.closed is True
    assert unlock_calls == 0
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_unlock_failure_still_closes_handle_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    _fake_open(monkeypatch, handle)
    monkeypatch.setattr(runtime_lock, "_lock_platform", lambda _: None)

    def fail_unlock(_: Any) -> None:
        raise OSError("unlock failed")

    monkeypatch.setattr(runtime_lock, "_unlock_platform", fail_unlock)

    with pytest.raises(RuntimeDataLockError, match="released cleanly"):
        with runtime_data_lock(tmp_path):
            pass

    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_body_failure_unlocks_closes_and_clears_depth(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    _fake_open(monkeypatch, handle)
    unlock_calls = 0
    monkeypatch.setattr(runtime_lock, "_lock_platform", lambda _: None)

    def record_unlock(_: Any) -> None:
        nonlocal unlock_calls
        unlock_calls += 1

    monkeypatch.setattr(runtime_lock, "_unlock_platform", record_unlock)

    with pytest.raises(RuntimeError, match="body failed"):
        with runtime_data_lock(tmp_path):
            raise RuntimeError("body failed")

    assert unlock_calls == 1
    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_nested_scope_reuses_outer_lock(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _clear_thread_state()
    handle = _Handle()
    _fake_open(monkeypatch, handle)
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

    with runtime_data_lock(tmp_path):
        assert len(runtime_lock._THREAD_STATE.depths) == 1
        with runtime_data_lock(tmp_path):
            assert list(runtime_lock._THREAD_STATE.depths.values()) == [2]
        assert list(runtime_lock._THREAD_STATE.depths.values()) == [1]

    assert lock_calls == 1
    assert unlock_calls == 1
    assert handle.closed is True
    assert runtime_lock._THREAD_STATE.depths == {}


def test_runtime_lock_rejects_non_path_before_filesystem() -> None:
    _clear_thread_state()

    with pytest.raises(TypeError, match="pathlib.Path"):
        with runtime_data_lock("/tmp/state"):  # type: ignore[arg-type]
            pass

    assert runtime_lock._THREAD_STATE.depths == {}
