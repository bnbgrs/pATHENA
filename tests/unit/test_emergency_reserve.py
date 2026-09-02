from __future__ import annotations

import os
from pathlib import Path

import pytest

import athena.storage.emergency_reserve as reserve_module
from athena.storage.emergency_reserve import (
    EmergencyReserveError,
    EmergencyReserveService,
    EmergencyReserveStore,
    emergency_reserve_size_bytes,
)

_MIB = 1024 * 1024
_GIB = 1024 * _MIB


def test_emergency_reserve_size_uses_beta_floor() -> None:
    assert emergency_reserve_size_bytes(1 * _GIB) == 256 * _MIB


def test_emergency_reserve_size_uses_one_percent_in_midrange() -> None:
    volume = 50 * _GIB
    assert emergency_reserve_size_bytes(volume) == (volume + 99) // 100


def test_emergency_reserve_size_uses_beta_cap() -> None:
    assert emergency_reserve_size_bytes(500 * _GIB) == 1 * _GIB


def test_emergency_reserve_size_rounds_one_percent_up() -> None:
    volume = 25_600 * _MIB + 1
    expected_percent = (volume + 99) // 100
    assert expected_percent > 256 * _MIB
    assert emergency_reserve_size_bytes(volume) == expected_percent


@pytest.mark.parametrize("value", [True, False, -1, 1.5, "100", None])
def test_emergency_reserve_size_rejects_invalid_volume(value: object) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        emergency_reserve_size_bytes(value)  # type: ignore[arg-type]


def test_store_creates_small_physically_allocated_test_reserve(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)

    status = store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert status.path == state_root / "reserve" / "emergency.reserve"
    assert status.required_bytes == 4096
    assert status.file_size_bytes == 4096
    assert status.path.stat().st_size == 4096
    if status.allocated_bytes is not None:
        assert status.allocated_bytes >= 4096
    if os.name == "posix":
        assert status.path.stat().st_mode & 0o077 == 0


def test_store_reuses_matching_existing_reserve(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)

    first = store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    before = first.path.stat().st_ino if hasattr(first.path.stat(), "st_ino") else None
    second = store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert second.file_size_bytes == 4096
    after = second.path.stat().st_ino if hasattr(second.path.stat(), "st_ino") else None
    if before is not None and after is not None:
        assert after == before


def test_store_rejects_wrong_sized_existing_reserve(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve_root = state_root / "reserve"
    reserve_root.mkdir()
    path = reserve_root / "emergency.reserve"
    path.write_bytes(b"x" * 128)
    store = EmergencyReserveStore(state_root)

    with pytest.raises(EmergencyReserveError, match="exactly match"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert path.stat().st_size == 128


def test_store_releases_only_reserve_file(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    sibling = store.reserve_root / "keep.txt"
    sibling.write_text("keep", encoding="utf-8")

    released = store.release()

    assert released == 4096
    assert not store.path.exists()
    assert sibling.read_text(encoding="utf-8") == "keep"
    assert store.release() == 0


def test_store_rejects_symlink_reserve_directory(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    reserve_root = state_root / "reserve"
    try:
        reserve_root.symlink_to(outside, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")

    store = EmergencyReserveStore(state_root)

    with pytest.raises(EmergencyReserveError, match="symlink|junction|reparse"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert not (outside / "emergency.reserve").exists()


def test_store_rejects_simulated_reparse_state_root_before_creation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    original = reserve_module.is_link_boundary

    def simulate_reparse(path: Path) -> bool:
        return path == state_root or original(path)

    open_attempted = False
    original_open = reserve_module.os.open

    def track_open(*args: object, **kwargs: object) -> int:
        nonlocal open_attempted
        open_attempted = True
        return original_open(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(reserve_module, "is_link_boundary", simulate_reparse)
    monkeypatch.setattr(reserve_module.os, "open", track_open)

    with pytest.raises(EmergencyReserveError, match="reparse-point ancestor"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert open_attempted is False
    assert not store.reserve_root.exists()


def test_store_cleans_partial_file_when_allocation_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)

    def fail_allocation(
        _descriptor: int,
        *,
        size_bytes: int,
        chunk_bytes: int,
    ) -> None:
        assert size_bytes == 4096
        assert chunk_bytes == 1024
        raise OSError("simulated disk full")

    monkeypatch.setattr(reserve_module, "_write_allocated_bytes", fail_allocation)

    with pytest.raises(EmergencyReserveError, match="physically allocated"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert not store.path.exists()


def test_store_inspect_detects_underallocated_file_when_platform_reports_blocks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve_root = state_root / "reserve"
    reserve_root.mkdir()
    path = reserve_root / "emergency.reserve"
    path.write_bytes(b"x" * 4096)
    store = EmergencyReserveStore(state_root)

    if os.name == "posix":
        monkeypatch.setattr(
            reserve_module,
            "_allocated_bytes_from_stat",
            lambda _stat: 1024,
        )
    else:
        monkeypatch.setattr(reserve_module, "_allocated_bytes", lambda _path: 1024)

    with pytest.raises(EmergencyReserveError, match="sparse or under-allocated"):
        store.inspect(required_bytes=4096)


def test_posix_store_creation_does_not_publish_into_replaced_reserve_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve_root = state_root / "reserve"
    reserve_root.mkdir()
    displaced = state_root / "reserve-displaced"
    store = EmergencyReserveStore(state_root)
    real_open = os.open
    replaced = False

    def racing_open(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        nonlocal replaced
        if dir_fd is not None and not replaced:
            replaced = True
            reserve_root.rename(displaced)
            reserve_root.mkdir()
        if dir_fd is None:
            return real_open(path, flags, mode)
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(reserve_module.os, "open", racing_open)

    with pytest.raises(EmergencyReserveError, match="directory changed"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert not (reserve_root / "emergency.reserve").exists()
    assert not (displaced / "emergency.reserve").exists()


def test_posix_store_release_does_not_unlink_replacement_root_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX dir_fd identity regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    reserve_root = store.reserve_root
    displaced = state_root / "reserve-displaced"
    real_unlink = os.unlink
    replaced = False

    def racing_unlink(
        path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
        *,
        dir_fd: int | None = None,
    ) -> None:
        nonlocal replaced
        if dir_fd is not None and not replaced:
            replaced = True
            reserve_root.rename(displaced)
            reserve_root.mkdir()
            (reserve_root / "emergency.reserve").write_bytes(b"attacker")
        if dir_fd is None:
            real_unlink(path)
        else:
            real_unlink(path, dir_fd=dir_fd)

    monkeypatch.setattr(reserve_module.os, "unlink", racing_unlink)

    with pytest.raises(EmergencyReserveError, match="directory changed"):
        store.release()

    assert (reserve_root / "emergency.reserve").read_bytes() == b"attacker"
    assert not (displaced / "emergency.reserve").exists()


def test_service_uses_beta_volume_sizing_and_persists_on_stop(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    volume_size = 50 * _GIB
    service = EmergencyReserveService(
        state_root,
        volume_size_provider=lambda path: volume_size if path == state_root else 0,
        required_bytes_override=4096,
        write_chunk_bytes=1024,
    )

    assert service.required_bytes() == 4096
    service.start()
    assert service.status is not None
    assert service.status.required_bytes == 4096
    reserve_path = service.status.path

    service.stop()

    assert reserve_path.is_file()


def test_service_derives_required_bytes_from_volume_provider(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    observed: list[Path] = []

    def volume_size(path: Path) -> int:
        observed.append(path)
        return 50 * _GIB

    service = EmergencyReserveService(
        state_root,
        volume_size_provider=volume_size,
    )

    assert service.required_bytes() == emergency_reserve_size_bytes(50 * _GIB)
    assert observed == [state_root]


def test_service_override_avoids_volume_probe_for_targeted_tests(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    probed = False

    def fail_probe(_path: Path) -> int:
        nonlocal probed
        probed = True
        raise AssertionError("volume probe must not run when override is explicit")

    service = EmergencyReserveService(
        state_root,
        volume_size_provider=fail_probe,
        required_bytes_override=4096,
        write_chunk_bytes=1024,
    )

    service.start()

    assert probed is False
    assert service.status is not None
    assert service.status.required_bytes == 4096
