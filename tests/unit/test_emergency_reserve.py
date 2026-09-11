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
    assert status.allocated_bytes is not None
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


def test_store_releases_capacity_and_keeps_only_empty_owned_stub(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    sibling = store.reserve_root / "keep.txt"
    sibling.write_text("keep", encoding="utf-8")

    released = store.release()

    assert released == 4096
    assert store.path.is_file()
    assert store.path.stat().st_size == 0
    assert sibling.read_text(encoding="utf-8") == "keep"
    assert store.release() == 0


def test_store_reprovisions_empty_released_stub(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    assert store.release() == 4096
    assert store.path.stat().st_size == 0

    status = store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert status.file_size_bytes == 4096
    assert status.allocated_bytes is not None
    assert status.allocated_bytes >= 4096


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


def test_store_reclaims_partial_allocation_to_empty_stub_when_allocation_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)

    def fail_allocation(
        descriptor: int,
        *,
        size_bytes: int,
        chunk_bytes: int,
    ) -> None:
        assert size_bytes == 4096
        assert chunk_bytes == 1024
        os.write(descriptor, b"x" * 1024)
        raise OSError("simulated disk full")

    monkeypatch.setattr(reserve_module, "_write_allocated_bytes", fail_allocation)

    with pytest.raises(EmergencyReserveError, match="physically allocated"):
        store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    assert store.path.is_file()
    assert store.path.stat().st_size == 0


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


def test_store_inspect_fails_closed_when_physical_allocation_is_unknown(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)

    if os.name == "posix":
        monkeypatch.setattr(reserve_module, "_allocated_bytes_from_stat", lambda _stat: None)
    else:
        monkeypatch.setattr(reserve_module, "_allocated_bytes", lambda _path: None)

    with pytest.raises(EmergencyReserveError, match="cannot be attested"):
        store.inspect(required_bytes=4096)


def test_posix_store_rejects_hardlinked_reserve_ownership(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX hardlink ownership regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    alias = tmp_path / "reserve-hardlink"
    os.link(store.path, alias)

    with pytest.raises(EmergencyReserveError, match="exactly one hard link"):
        store.inspect(required_bytes=4096)
    with pytest.raises(EmergencyReserveError, match="exactly one hard link"):
        store.release()

    assert store.path.stat().st_size == 4096
    assert alias.stat().st_size == 4096


def test_posix_store_detects_hardlink_inserted_during_release(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX hardlink insertion regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    alias = tmp_path / "reserve-racing-hardlink"
    real_ftruncate = reserve_module.os.ftruncate
    inserted = False

    def racing_ftruncate(descriptor: int, length: int) -> None:
        nonlocal inserted
        if length == 0 and not inserted:
            inserted = True
            os.link(store.path, alias)
        real_ftruncate(descriptor, length)

    monkeypatch.setattr(reserve_module.os, "ftruncate", racing_ftruncate)

    with pytest.raises(EmergencyReserveError, match="exactly one hard link"):
        store.release()

    assert inserted is True
    assert store.path.stat().st_size == 0
    assert alias.stat().st_size == 0


def test_posix_release_reclaims_capacity_with_preopened_second_descriptor(
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX open-descriptor reclamation regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    held = os.open(store.path, os.O_RDONLY)
    try:
        released = store.release()
        held_stat = os.fstat(held)

        assert released == 4096
        assert held_stat.st_size == 0
        allocated = reserve_module._allocated_bytes_from_stat(held_stat)
        assert allocated == 0
        assert store.path.stat().st_size == 0
    finally:
        os.close(held)


def test_posix_release_does_not_touch_same_parent_path_replacement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.name != "posix":
        pytest.skip("POSIX same-parent substitution regression")

    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    store = EmergencyReserveStore(state_root)
    store.ensure(required_bytes=4096, write_chunk_bytes=1024)
    displaced = store.reserve_root / "displaced.reserve"
    real_ftruncate = reserve_module.os.ftruncate
    replaced = False

    def racing_ftruncate(descriptor: int, length: int) -> None:
        nonlocal replaced
        if length == 0 and not replaced:
            replaced = True
            store.path.rename(displaced)
            store.path.write_bytes(b"attacker")
        real_ftruncate(descriptor, length)

    monkeypatch.setattr(reserve_module.os, "ftruncate", racing_ftruncate)

    with pytest.raises(EmergencyReserveError, match="pathname changed"):
        store.release()

    assert replaced is True
    assert store.path.read_bytes() == b"attacker"
    assert displaced.stat().st_size == 0


def test_posix_store_creation_does_not_allocate_into_replaced_reserve_root(
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
    displaced_reserve = displaced / "emergency.reserve"
    assert displaced_reserve.is_file()
    assert displaced_reserve.stat().st_size == 0


def test_posix_store_release_does_not_touch_replacement_root_file(
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
    real_ftruncate = reserve_module.os.ftruncate
    replaced = False

    def racing_ftruncate(descriptor: int, length: int) -> None:
        nonlocal replaced
        if length == 0 and not replaced:
            replaced = True
            reserve_root.rename(displaced)
            reserve_root.mkdir()
            (reserve_root / "emergency.reserve").write_bytes(b"attacker")
        real_ftruncate(descriptor, length)

    monkeypatch.setattr(reserve_module.os, "ftruncate", racing_ftruncate)

    with pytest.raises(EmergencyReserveError, match="directory changed"):
        store.release()

    assert (reserve_root / "emergency.reserve").read_bytes() == b"attacker"
    assert (displaced / "emergency.reserve").stat().st_size == 0


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
