from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from athena.storage.disk_pressure import (
    DiskPressureController,
    DiskPressureState,
    DiskPressureWriteBlockedError,
    assess_disk_pressure,
    disk_pressure_thresholds,
)
from athena.storage.emergency_reserve import EmergencyReserveStatus

_GIB = 1024 * 1024 * 1024


@dataclass
class _ReserveStub:
    released_bytes: int
    release_calls: int = 0
    ensure_calls: int = 0

    def release(self) -> int:
        self.release_calls += 1
        return self.released_bytes

    def ensure(
        self,
        *,
        required_bytes: int,
        write_chunk_bytes: int,
    ) -> EmergencyReserveStatus:
        self.ensure_calls += 1
        return EmergencyReserveStatus(
            path=Path("/tmp/emergency.reserve"),
            required_bytes=required_bytes,
            file_size_bytes=required_bytes,
            allocated_bytes=required_bytes,
        )


def test_small_volume_uses_absolute_beta_threshold_floors() -> None:
    thresholds = disk_pressure_thresholds(100 * _GIB)
    assert thresholds.warning_free_bytes == 10 * _GIB
    assert thresholds.critical_free_bytes == 5 * _GIB
    assert thresholds.emergency_free_bytes == 2 * _GIB


def test_large_volume_uses_percentage_thresholds() -> None:
    thresholds = disk_pressure_thresholds(2_000 * _GIB)
    assert thresholds.warning_free_bytes == 100 * _GIB
    assert thresholds.critical_free_bytes == 40 * _GIB
    assert thresholds.emergency_free_bytes == 20 * _GIB


def test_percentage_thresholds_round_up_without_float_conversion() -> None:
    total = 2_000 * _GIB + 1
    thresholds = disk_pressure_thresholds(total)
    assert thresholds.warning_free_bytes == (total * 5 + 99) // 100
    assert thresholds.critical_free_bytes == (total * 2 + 99) // 100
    assert thresholds.emergency_free_bytes == (total + 99) // 100


def test_exact_threshold_equality_stays_in_less_severe_state() -> None:
    total = 100 * _GIB
    thresholds = disk_pressure_thresholds(total)
    assert (
        assess_disk_pressure(
            total_bytes=total,
            free_bytes=thresholds.warning_free_bytes,
        ).state
        is DiskPressureState.NORMAL
    )
    assert (
        assess_disk_pressure(
            total_bytes=total,
            free_bytes=thresholds.critical_free_bytes,
        ).state
        is DiskPressureState.WARNING
    )
    assert (
        assess_disk_pressure(
            total_bytes=total,
            free_bytes=thresholds.emergency_free_bytes,
        ).state
        is DiskPressureState.CRITICAL
    )


def test_one_byte_below_each_threshold_enters_next_state() -> None:
    total = 100 * _GIB
    thresholds = disk_pressure_thresholds(total)
    assert (
        assess_disk_pressure(
            total_bytes=total,
            free_bytes=thresholds.warning_free_bytes - 1,
        ).state
        is DiskPressureState.WARNING
    )
    assert (
        assess_disk_pressure(
            total_bytes=total,
            free_bytes=thresholds.critical_free_bytes - 1,
        ).state
        is DiskPressureState.CRITICAL
    )
    emergency = assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.emergency_free_bytes - 1,
    )
    assert emergency.state is DiskPressureState.EMERGENCY
    assert emergency.release_emergency_reserve is True
    assert emergency.allow_noncritical_writes is False
    assert emergency.read_only_safe_mode_available is True


def test_non_emergency_states_keep_reserve_and_noncritical_writes() -> None:
    total = 100 * _GIB
    for free in (100 * _GIB, 9 * _GIB, 4 * _GIB):
        assessment = assess_disk_pressure(total_bytes=total, free_bytes=free)
        assert assessment.state is not DiskPressureState.EMERGENCY
        assert assessment.release_emergency_reserve is False
        assert assessment.allow_noncritical_writes is True
        assert assessment.read_only_safe_mode_available is False


@pytest.mark.parametrize("value", [True, False, -1, 1.5, "1", None])
def test_disk_pressure_rejects_invalid_total(value: object) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        disk_pressure_thresholds(value)  # type: ignore[arg-type]


def test_disk_pressure_rejects_free_space_larger_than_volume() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        assess_disk_pressure(total_bytes=10, free_bytes=11)


def test_disk_pressure_handles_huge_integer_volume_without_float_conversion() -> None:
    total = 10**400
    thresholds = disk_pressure_thresholds(total)
    assert thresholds.warning_free_bytes == (total * 5 + 99) // 100
    assert thresholds.critical_free_bytes == (total * 2 + 99) // 100
    assert thresholds.emergency_free_bytes == (total + 99) // 100


def test_controller_does_not_release_reserve_before_emergency(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=4096)
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 4 * _GIB),
    )
    result = controller.check()
    assert result.before_release.state is DiskPressureState.CRITICAL
    assert result.after_release is result.before_release
    assert result.released_reserve_bytes == 0
    assert reserve.release_calls == 0
    assert controller.read_only_safe_mode is False


def test_controller_releases_reserve_once_at_emergency_and_reassesses(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    readings = iter([(100 * _GIB, 1 * _GIB), (100 * _GIB, 2 * _GIB)])
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: next(readings),
    )
    result = controller.check()
    assert result.before_release.state is DiskPressureState.EMERGENCY
    assert result.released_reserve_bytes == 1 * _GIB
    assert result.after_release.state is DiskPressureState.CRITICAL
    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True


def test_controller_does_not_fake_space_recovery_when_reserve_is_absent(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=0)
    usage_calls = 0

    def usage(_path: Path) -> tuple[int, int]:
        nonlocal usage_calls
        usage_calls += 1
        return 100 * _GIB, 1 * _GIB

    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=usage,
    )
    result = controller.check()
    assert result.before_release.state is DiskPressureState.EMERGENCY
    assert result.after_release is result.before_release
    assert result.released_reserve_bytes == 0
    assert usage_calls == 1
    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True


def test_controller_refuses_reserve_reprovision_while_emergency(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=0)
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 1 * _GIB),
    )
    result = controller.ensure_reserve_if_safe(write_chunk_bytes=1024)
    assert result.assessment.state is DiskPressureState.EMERGENCY
    assert result.provisioned is False
    assert result.status is None
    assert result.required_bytes == 1 * _GIB
    assert reserve.ensure_calls == 0


def test_controller_provisions_reserve_outside_emergency(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=0)
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: (100 * _GIB, 20 * _GIB),
    )
    result = controller.ensure_reserve_if_safe(write_chunk_bytes=1024)
    assert result.assessment.state is DiskPressureState.NORMAL
    assert result.provisioned is True
    assert result.status is not None
    assert result.required_bytes == 1 * _GIB
    assert result.status.required_bytes == 1 * _GIB
    assert reserve.ensure_calls == 1


def test_write_gate_allows_non_emergency_state(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    controller = DiskPressureController(
        state_root,
        disk_usage_provider=lambda _path: (100 * _GIB, 4 * _GIB),
    )
    controller.assert_noncritical_write_allowed()
    assert controller.read_only_safe_mode is False


def test_write_gate_releases_reserve_and_blocks_emergency_state(tmp_path: Path) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    readings = iter([(100 * _GIB, 1 * _GIB), (100 * _GIB, 2 * _GIB)])
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: next(readings),
    )

    with pytest.raises(DiskPressureWriteBlockedError, match="EMERGENCY"):
        controller.assert_noncritical_write_allowed()

    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True


def test_write_gate_stays_blocked_after_reserve_release_improves_space(
    tmp_path: Path,
) -> None:
    state_root = (tmp_path / "state").absolute()
    state_root.mkdir()
    reserve = _ReserveStub(released_bytes=1 * _GIB)
    readings = iter([(100 * _GIB, 1 * _GIB), (100 * _GIB, 4 * _GIB)])
    controller = DiskPressureController(
        state_root,
        reserve_store=reserve,  # type: ignore[arg-type]
        disk_usage_provider=lambda _path: next(readings),
    )

    with pytest.raises(DiskPressureWriteBlockedError):
        controller.assert_noncritical_write_allowed()
    with pytest.raises(DiskPressureWriteBlockedError, match="latched read-only"):
        controller.assert_noncritical_write_allowed()

    assert reserve.release_calls == 1
    assert controller.read_only_safe_mode is True
