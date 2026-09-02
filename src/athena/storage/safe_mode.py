"""Controlled read-only storage safe mode for EMERGENCY disk pressure."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from athena.storage.disk_pressure import (
    DiskPressureCheckResult,
    DiskPressureController,
    DiskPressureState,
)
from athena.storage.read_only_database import ReadOnlySQLiteDatabase


class StorageSafeModeError(RuntimeError):
    """Raised when read-only safe mode cannot be entered deterministically."""


@dataclass(frozen=True, slots=True)
class StorageSafeModeStatus:
    pressure: DiskPressureCheckResult
    reserve_released_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.pressure, DiskPressureCheckResult):
            raise TypeError("Safe-mode pressure must be DiskPressureCheckResult.")
        if (
            isinstance(self.reserve_released_bytes, bool)
            or not isinstance(self.reserve_released_bytes, int)
            or self.reserve_released_bytes < 0
        ):
            raise ValueError("Safe-mode reserve_released_bytes must be non-negative integer.")
        if self.reserve_released_bytes != self.pressure.released_reserve_bytes:
            raise ValueError("Safe-mode reserve release must match pressure check result.")


class StorageSafeModeService:
    """Release reserve when needed and expose only read-only canonical SQLite."""

    name = "storage-safe-mode"

    def __init__(
        self,
        *,
        database_path: Path,
        disk_pressure: DiskPressureController,
    ) -> None:
        if not isinstance(database_path, Path):
            raise TypeError("Safe-mode database_path must be pathlib.Path.")
        if not database_path.is_absolute():
            raise ValueError("Safe-mode database_path must be absolute.")
        if not isinstance(disk_pressure, DiskPressureController):
            raise TypeError("Safe-mode disk_pressure must be DiskPressureController.")
        self.database = ReadOnlySQLiteDatabase(database_path)
        self.disk_pressure = disk_pressure
        self.status: StorageSafeModeStatus | None = None
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        pressure = self.disk_pressure.check()
        if pressure.before_release.state is not DiskPressureState.EMERGENCY:
            raise StorageSafeModeError(
                "Storage safe mode is reserved for EMERGENCY disk pressure."
            )

        # The pressure check already releases the reserve if present. Never
        # provision it while entering safe mode; the reclaimed bytes are for
        # controlled recovery only.
        self.database.start()
        self.status = StorageSafeModeStatus(
            pressure=pressure,
            reserve_released_bytes=pressure.released_reserve_bytes,
        )
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        self.database.stop()
        self._started = False
