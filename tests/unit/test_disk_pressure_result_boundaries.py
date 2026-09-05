from __future__ import annotations

import pytest

from athena.storage.disk_pressure import (
    DiskPressureCheckResult,
    DiskPressureState,
    assess_disk_pressure,
)

_GIB = 1024 * 1024 * 1024


def test_disk_pressure_check_result_rejects_release_before_emergency() -> None:
    before = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=20 * _GIB)
    after = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=21 * _GIB)
    assert before.state is DiskPressureState.NORMAL

    with pytest.raises(ValueError, match="reserve release requires an EMERGENCY before state"):
        DiskPressureCheckResult(
            before_release=before,
            released_reserve_bytes=1 * _GIB,
            after_release=after,
        )


def test_disk_pressure_check_result_allows_release_from_emergency() -> None:
    before = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=1 * _GIB)
    after = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=2 * _GIB)
    assert before.state is DiskPressureState.EMERGENCY
    assert after.state is DiskPressureState.CRITICAL

    result = DiskPressureCheckResult(
        before_release=before,
        released_reserve_bytes=1 * _GIB,
        after_release=after,
    )

    assert result.released_reserve_bytes == 1 * _GIB


def test_disk_pressure_check_result_rejects_release_larger_than_volume() -> None:
    before = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=1 * _GIB)
    after = assess_disk_pressure(total_bytes=100 * _GIB, free_bytes=2 * _GIB)
    assert before.state is DiskPressureState.EMERGENCY

    with pytest.raises(ValueError, match="released reserve bytes must not exceed volume size"):
        DiskPressureCheckResult(
            before_release=before,
            released_reserve_bytes=101 * _GIB,
            after_release=after,
        )
