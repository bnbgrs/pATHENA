from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import pytest

import athena.storage.emergency_reserve as reserve_module
from athena.storage.emergency_reserve import EmergencyReserveStore


def test_concurrent_creator_waits_for_growing_reserve(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    first_chunk_written = threading.Event()
    required = 64 * 1024

    def slow_allocate(
        descriptor: int,
        *,
        size_bytes: int,
        chunk_bytes: int,
    ) -> None:
        assert size_bytes == required
        payload = b"x" * min(chunk_bytes, 4096)
        remaining = size_bytes
        first = True
        while remaining:
            current = payload if remaining >= len(payload) else payload[:remaining]
            os.write(descriptor, current)
            remaining -= len(current)
            if first:
                first = False
                first_chunk_written.set()
            time.sleep(0.01)

    monkeypatch.setattr(reserve_module, "_write_allocated_bytes", slow_allocate)
    creator = EmergencyReserveStore(state_root)
    waiter = EmergencyReserveStore(state_root)
    creator_result: list[object] = []
    creator_error: list[BaseException] = []

    def create() -> None:
        try:
            creator_result.append(
                creator.ensure(required_bytes=required, write_chunk_bytes=4096)
            )
        except BaseException as exc:  # pragma: no cover - assertion surfaces the exception
            creator_error.append(exc)

    thread = threading.Thread(target=create)
    thread.start()
    assert first_chunk_written.wait(timeout=5)

    waited = waiter.ensure(required_bytes=required, write_chunk_bytes=4096)
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert creator_error == []
    assert len(creator_result) == 1
    assert waited.file_size_bytes == required
    assert waiter.path.stat().st_size == required


def test_lost_nonposix_exclusive_create_never_unlinks_winner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve_root = state_root / "reserve"
    reserve_root.mkdir()
    store = EmergencyReserveStore(state_root)
    required = 4096
    real_open = reserve_module.os.open
    raced = False

    monkeypatch.setattr(reserve_module.os, "name", "nt")

    def racing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *args: object,
        **kwargs: object,
    ) -> int:
        nonlocal raced
        if Path(path) == store.path and not raced:
            raced = True
            winner = real_open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(winner, b"w" * required)
                os.fsync(winner)
            finally:
                os.close(winner)
            raise FileExistsError("simulated concurrent winner")
        return real_open(path, flags, mode, *args, **kwargs)

    monkeypatch.setattr(reserve_module.os, "open", racing_open)

    status = store.ensure(required_bytes=required, write_chunk_bytes=1024)

    assert raced is True
    assert status.file_size_bytes == required
    assert store.path.read_bytes() == b"w" * required


def test_reserve_root_creation_race_accepts_only_safe_winner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    real_mkdir = reserve_module.durable_mkdir
    raced = False

    def racing_mkdir(path: Path, *, parents: bool = False, exist_ok: bool = False) -> None:
        nonlocal raced
        if path == store.reserve_root and not raced:
            raced = True
            path.mkdir()
            raise FileExistsError("simulated concurrent directory creator")
        real_mkdir(path, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(reserve_module, "durable_mkdir", racing_mkdir)

    status = store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert raced is True
    assert status.file_size_bytes == 4096
    assert store.reserve_root.is_dir()
