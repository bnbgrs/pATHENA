"""Deterministic disk-pressure policy for ATHENA's active state volume."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from athena.storage.emergency_reserve import (
    EmergencyReserveStatus,
    EmergencyReserveStore,
    emergency_reserve_size_bytes,
)

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


class DiskPressureWriteBlockedError(RuntimeError):
    """Raised when a noncritical write is forbidden by disk-pressure policy."""


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer.")
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
        if free < self.thresholds.emergency_free_bytes:
            expected_state = DiskPressureState.EMERGENCY
        elif free < self.thresholds.critical_free_bytes:
            expected_state = DiskPressureState.CRITICAL
        elif free < self.thresholds.warning_free_bytes:
            expected_state = DiskPressureState.WARNING
        else:
            expected_state = DiskPressureState.NORMAL
        if self.state is not expected_state:
            raise ValueError(
                "Disk pressure state must match free bytes and thresholds."
            )

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


@dataclass(frozen=True, slots=True)
class DiskPressureCheckResult:
    before_release: DiskPressureAssessment
    released_reserve_bytes: int
    after_release: DiskPressureAssessment

    def __post_init__(self) -> None:
        if not isinstance(self.before_release, DiskPressureAssessment):
            raise TypeError("Disk pressure before_release must be DiskPressureAssessment.")
        released = _nonnegative_int(
            self.released_reserve_bytes,
            "Disk pressure released_reserve_bytes",
        )
        if not isinstance(self.after_release, DiskPressureAssessment):
            raise TypeError("Disk pressure after_release must be DiskPressureAssessment.")
        if self.after_release.total_bytes != self.before_release.total_bytes:
            raise ValueError("Disk pressure volume size changed during one check.")
        if self.after_release.thresholds != self.before_release.thresholds:
            raise ValueError("Disk pressure thresholds changed during one check.")
        if released > self.before_release.total_bytes:
            raise ValueError("Disk pressure released reserve bytes must not exceed volume size.")
        if released > 0 and self.before_release.state is not DiskPressureState.EMERGENCY:
            raise ValueError(
                "Disk pressure reserve release requires an EMERGENCY before state."
            )
        if released == 0 and self.after_release != self.before_release:
            raise ValueError(
                "Disk pressure state cannot change without a reserve release in one check."
            )


@dataclass(frozen=True, slots=True)
class EmergencyReserveProvisionResult:
    assessment: DiskPressureAssessment
    required_bytes: int
    provisioned_bytes: int
    status: EmergencyReserveStatus | None

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, DiskPressureAssessment):
            raise TypeError("Reserve provision assessment must be DiskPressureAssessment.")
        required = _positive_int(self.required_bytes, "Reserve provision required_bytes")
        provisioned = _nonnegative_int(
            self.provisioned_bytes,
            "Reserve provision provisioned_bytes",
        )
        if provisioned > required:
            raise ValueError("Reserve provisioned bytes must not exceed required bytes.")
        if provisioned > self.assessment.free_bytes:
            raise ValueError("Reserve provisioned bytes must not exceed assessed free bytes.")
        safe_allocation = max(
            0,
            self.assessment.free_bytes - self.assessment.thresholds.emergency_free_bytes,
        )
        if provisioned > safe_allocation:
            raise ValueError(
                "Reserve provisioned bytes must not create EMERGENCY disk pressure."
            )
        if self.status is not None and not isinstance(self.status, EmergencyReserveStatus):
            raise TypeError("Reserve provision status must be EmergencyReserveStatus or None.")
        if self.status is None:
            if provisioned != 0:
                raise ValueError("Missing reserve status requires zero provisioned bytes.")
        elif self.status.required_bytes != provisioned:
            raise ValueError("Reserve status size must match provisioned bytes.")
        if self.assessment.state is DiskPressureState.EMERGENCY and self.status is not None:
            raise ValueError("Emergency disk pressure must not provision a reserve.")

    @property
    def provisioned(self) -> bool:
        return self.status is not None

    @property
    def downsized(self) -> bool:
        return 0 < self.provisioned_bytes < self.required_bytes


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


DiskUsageProvider = Callable[[Path], tuple[int, int]]


def _default_disk_usage(path: Path) -> tuple[int, int]:
    usage = shutil.disk_usage(path)
    return int(usage.total), int(usage.free)


class DiskPressureController:
    """Control reserve allocation/release around Beta disk-pressure boundaries.

    The controller never deletes canonical data. It releases only the physical
    reserve at EMERGENCY and refuses to recreate that reserve while the volume
    remains in EMERGENCY, preserving the space gained for controlled recovery.
    Once runtime EMERGENCY is observed, noncritical writes remain latched off for
    the lifetime of this controller. A controlled restart performs a fresh
    bootstrap assessment before writable operation can resume.
    """

    def __init__(
        self,
        state_root: Path,
        *,
        reserve_store: EmergencyReserveStore | None = None,
        disk_usage_provider: DiskUsageProvider | None = None,
    ) -> None:
        if not isinstance(state_root, Path):
            raise TypeError("Disk pressure state_root must be a pathlib.Path.")
        root = state_root.expanduser()
        if not root.is_absolute():
            raise ValueError("Disk pressure state_root must be absolute.")
        self.state_root = root
        self.reserve_store = reserve_store or EmergencyReserveStore(root)
        self._disk_usage_provider = disk_usage_provider or _default_disk_usage
        self._read_only_safe_mode = False

    @property
    def read_only_safe_mode(self) -> bool:
        """Whether runtime EMERGENCY has latched noncritical writes off."""
        return self._read_only_safe_mode

    def _assessment(self) -> DiskPressureAssessment:
        try:
            total, free = self._disk_usage_provider(self.state_root)
        except OSError as exc:
            raise RuntimeError("Disk pressure volume usage could not be determined.") from exc
        return assess_disk_pressure(total_bytes=total, free_bytes=free)

    def assert_noncritical_write_allowed(self) -> None:
        """Gate canonical writes and latch safe mode on the first EMERGENCY."""
        if self._read_only_safe_mode:
            raise DiskPressureWriteBlockedError(
                "ATHENA noncritical writes are blocked by latched read-only safe mode."
            )

        self.check()
        if self._read_only_safe_mode:
            raise DiskPressureWriteBlockedError(
                "ATHENA noncritical writes are blocked while disk pressure is EMERGENCY."
            )

    def ensure_reserve_if_safe(
        self,
        *,
        write_chunk_bytes: int = 4 * _MIB,
    ) -> EmergencyReserveProvisionResult:
        """Provision as much reserve as possible without creating EMERGENCY pressure.

        The Beta reserve target remains the normal sizing policy. Before allocation,
        however, the controller projects free space after the physical write. If the
        full reserve would cross below the strict EMERGENCY threshold, allocation is
        downsized to leave free space exactly at that threshold. If no byte can be
        allocated safely, provisioning is refused rather than creating an immediate
        reserve-release/read-only cycle.
        """
        chunk_bytes = _positive_int(
            write_chunk_bytes,
            "Reserve provision write_chunk_bytes",
        )
        assessment = self._assessment()
        required = emergency_reserve_size_bytes(assessment.total_bytes)
        if assessment.state is DiskPressureState.EMERGENCY:
            return EmergencyReserveProvisionResult(
                assessment=assessment,
                required_bytes=required,
                provisioned_bytes=0,
                status=None,
            )

        safe_allocation = max(
            0,
            assessment.free_bytes - assessment.thresholds.emergency_free_bytes,
        )
        provisioned = min(required, safe_allocation)
        if provisioned == 0:
            return EmergencyReserveProvisionResult(
                assessment=assessment,
                required_bytes=required,
                provisioned_bytes=0,
                status=None,
            )

        status = self.reserve_store.ensure(
            required_bytes=provisioned,
            write_chunk_bytes=chunk_bytes,
        )
        return EmergencyReserveProvisionResult(
            assessment=assessment,
            required_bytes=required,
            provisioned_bytes=provisioned,
            status=status,
        )

    def check(self) -> DiskPressureCheckResult:
        """Assess pressure, latch safe mode, and release only the emergency reserve."""
        before = self._assessment()
        if before.state is DiskPressureState.EMERGENCY:
            self._read_only_safe_mode = True
        if not before.release_emergency_reserve:
            return DiskPressureCheckResult(
                before_release=before,
                released_reserve_bytes=0,
                after_release=before,
            )

        released = self.reserve_store.release()
        if released == 0:
            return DiskPressureCheckResult(
                before_release=before,
                released_reserve_bytes=0,
                after_release=before,
            )

        after = self._assessment()
        return DiskPressureCheckResult(
            before_release=before,
            released_reserve_bytes=released,
            after_release=after,
        )
