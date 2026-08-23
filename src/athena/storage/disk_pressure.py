"""Deterministic disk-pressure policy for ATHENA's active state volume."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

_MIB = 1024 * 1024
_GIB = 1024 * _MIB

_WARNING_MIN_BYTES = 10 * _GIB
_CRITICAL_MIN_BYTES = 5 * _GIB
_EMERGENCY_MIN_BYTES = 2 * _GIB


class DiskPressureState(IntEnum):
    NORMAL = 0
    WARNING = 1
    CRITICAL = 2
    EMERGENCY = 3


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _percent_ceiling(value: int, percent: int) -> int:
    return (value * percent + 99) // 100


@dataclass(frozen=True, slots=True)
class DiskPressureThresholds:
    warning_free_bytes: int
    critical_free_bytes: int
    emergency_free_bytes: int

    def __post_init__(self) -> None:
        warning = _nonnegative_int(
            self.warning_free_bytes,
            "Disk pressure warning_free_bytes",
        )
        critical = _nonnegative_int(
            self.critical_free_bytes,
            "Disk pressure critical_free_bytes",
        )
        emergency = _nonnegative_int(
            self.emergency_free_bytes,
            "Disk pressure emergency_free_bytes",
        )
        if not warning >= critical >= emergency:
            raise ValueError(
                "Disk pressure thresholds must satisfy warning >= critical >= emergency."
            )


@dataclass(frozen=True, slots=True)
class DiskPressureAssessment:
    total_bytes: int
    free_bytes: int
    state: DiskPressureState
    thresholds: DiskPressureThresholds

    def __post_init__(self) -> None:
        total = _nonnegative_int(self.total_bytes, "Disk pressure total_bytes")
        free = _nonnegative_int(self.free_bytes, "Disk pressure free_bytes")
        if free > total:
            raise ValueError("Disk pressure free_bytes must not exceed total_bytes.")
        if not isinstance(self.state, DiskPressureState):
            raise TypeError("Disk pressure state must be DiskPressureState.")
        if not isinstance(self.thresholds, DiskPressureThresholds):
            raise TypeError("Disk pressure thresholds must be DiskPressureThresholds.")

    @property
    def release_emergency_reserve(self) -> bool:
        """The reserve is released only at the Beta EMERGENCY boundary."""
        return self.state is DiskPressureState.EMERGENCY

    @property
    def allow_noncritical_writes(self) -> bool:
        return self.state < DiskPressureState.EMERGENCY

    @property
    def read_only_safe_mode_available(self) -> bool:
        return self.state is DiskPressureState.EMERGENCY


def disk_pressure_thresholds(total_bytes: int) -> DiskPressureThresholds:
    """Return Beta-03 thresholds using conservative integer percentage ceilings."""
    total = _nonnegative_int(total_bytes, "Disk pressure total_bytes")
    return DiskPressureThresholds(
        warning_free_bytes=max(_WARNING_MIN_BYTES, _percent_ceiling(total, 5)),
        critical_free_bytes=max(_CRITICAL_MIN_BYTES, _percent_ceiling(total, 2)),
        emergency_free_bytes=max(_EMERGENCY_MIN_BYTES, _percent_ceiling(total, 1)),
    )


def assess_disk_pressure(
    *,
    total_bytes: int,
    free_bytes: int,
) -> DiskPressureAssessment:
    """Classify current free space without side effects or hidden hysteresis."""
    total = _nonnegative_int(total_bytes, "Disk pressure total_bytes")
    free = _nonnegative_int(free_bytes, "Disk pressure free_bytes")
    if free > total:
        raise ValueError("Disk pressure free_bytes must not exceed total_bytes.")
    thresholds = disk_pressure_thresholds(total)

    # Beta wording uses strict "free < threshold" boundaries. Exact equality
    # therefore remains in the less severe state.
    if free < thresholds.emergency_free_bytes:
        state = DiskPressureState.EMERGENCY
    elif free < thresholds.critical_free_bytes:
        state = DiskPressureState.CRITICAL
    elif free < thresholds.warning_free_bytes:
        state = DiskPressureState.WARNING
    else:
        state = DiskPressureState.NORMAL

    return DiskPressureAssessment(
        total_bytes=total,
        free_bytes=free,
        state=state,
        thresholds=thresholds,
    )
