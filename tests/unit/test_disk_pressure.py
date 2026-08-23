from __future__ import annotations

import pytest

from athena.storage.disk_pressure import (
    DiskPressureState,
    assess_disk_pressure,
    disk_pressure_thresholds,
)

_GIB = 1024 * 1024 * 1024


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

    assert assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.warning_free_bytes,
    ).state is DiskPressureState.NORMAL
    assert assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.critical_free_bytes,
    ).state is DiskPressureState.WARNING
    assert assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.emergency_free_bytes,
    ).state is DiskPressureState.CRITICAL


def test_one_byte_below_each_threshold_enters_next_state() -> None:
    total = 100 * _GIB
    thresholds = disk_pressure_thresholds(total)

    assert assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.warning_free_bytes - 1,
    ).state is DiskPressureState.WARNING
    assert assess_disk_pressure(
        total_bytes=total,
        free_bytes=thresholds.critical_free_bytes - 1,
    ).state is DiskPressureState.CRITICAL
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
