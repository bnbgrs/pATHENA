"""Composition root for pressure-aware writable ATHENA storage."""

from __future__ import annotations

from dataclasses import dataclass

from athena.storage.bootstrap import StorageBootstrapService
from athena.storage.disk_pressure import DiskPressureController
from athena.storage.paths import RuntimePaths
from athena.storage.pressure_database import PressureGuardedSQLiteDatabase


@dataclass(frozen=True, slots=True)
class StorageRuntime:
    """One shared disk-pressure authority for bootstrap and live transactions."""

    disk_pressure: DiskPressureController
    database: PressureGuardedSQLiteDatabase
    bootstrap: StorageBootstrapService

    def __post_init__(self) -> None:
        if not isinstance(self.disk_pressure, DiskPressureController):
            raise TypeError("StorageRuntime disk_pressure must be DiskPressureController.")
        if not isinstance(self.database, PressureGuardedSQLiteDatabase):
            raise TypeError(
                "StorageRuntime database must be PressureGuardedSQLiteDatabase."
            )
        if not isinstance(self.bootstrap, StorageBootstrapService):
            raise TypeError("StorageRuntime bootstrap must be StorageBootstrapService.")
        if self.database.disk_pressure is not self.disk_pressure:
            raise ValueError(
                "StorageRuntime database and bootstrap must share one disk-pressure controller."
            )
        if self.bootstrap.disk_pressure is not self.disk_pressure:
            raise ValueError(
                "StorageRuntime bootstrap and database must share one disk-pressure controller."
            )
        if self.bootstrap.database is not self.database:
            raise ValueError(
                "StorageRuntime bootstrap must own the same pressure-guarded database."
            )


def build_storage_runtime(paths: RuntimePaths) -> StorageRuntime:
    """Build the default writable storage runtime without starting any service."""
    if not isinstance(paths, RuntimePaths):
        raise TypeError("paths must be RuntimePaths.")

    pressure = DiskPressureController(paths.state_root)
    database = PressureGuardedSQLiteDatabase(
        paths.database_path,
        disk_pressure=pressure,
    )
    bootstrap = StorageBootstrapService(
        paths=paths,
        database=database,
        disk_pressure=pressure,
    )
    return StorageRuntime(
        disk_pressure=pressure,
        database=database,
        bootstrap=bootstrap,
    )
