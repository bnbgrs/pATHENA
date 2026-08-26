"""Read-only storage health telemetry for local Core and desktop surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from athena.common.time import utc_now_us
from athena.storage.database import DatabaseNotStartedError, SQLiteDatabase

StorageHealthStatus = Literal["available", "unavailable", "error"]
_ALLOWED_STORAGE_HEALTH_STATUSES = frozenset({"available", "unavailable", "error"})


@dataclass(frozen=True, slots=True)
class StorageHealthSnapshot:
    """Truthful point-in-time facts about the live SQLite storage service."""

    status: StorageHealthStatus
    database_open: bool
    database_path: str | None
    database_size_bytes: int | None
    wal_size_bytes: int | None
    observed_at_us: int
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.status not in _ALLOWED_STORAGE_HEALTH_STATUSES:
            raise ValueError("Storage health status is invalid.")
        if self.observed_at_us <= 0:
            raise ValueError("Storage health observation time must be positive.")
        if self.database_size_bytes is not None and self.database_size_bytes < 0:
            raise ValueError("Storage health database size cannot be negative.")
        if self.wal_size_bytes is not None and self.wal_size_bytes < 0:
            raise ValueError("Storage health WAL size cannot be negative.")

        if self.status == "available":
            if not self.database_open:
                raise ValueError("Available storage health requires an open database.")
            if self.database_path is None:
                raise ValueError("Available storage health requires a database path.")
            if self.database_size_bytes is None or self.wal_size_bytes is None:
                raise ValueError("Available storage health requires measured sizes.")
            if self.detail is not None:
                raise ValueError("Available storage health cannot carry an error detail.")
            return

        if self.database_size_bytes is not None or self.wal_size_bytes is not None:
            raise ValueError(
                "Non-available storage health cannot expose partial measured sizes."
            )

        if self.status == "unavailable":
            if self.database_open:
                raise ValueError("Unavailable storage health cannot report an open database.")
            if self.detail is None:
                raise ValueError("Unavailable storage health requires a detail.")
            return

        if not self.database_open:
            raise ValueError("Storage health errors require a live database boundary.")
        if self.detail is None:
            raise ValueError("Storage health errors require a detail.")


class StorageHealthService:
    """Observe SQLite availability and filesystem-backed size facts without mutation."""

    def __init__(self, database: SQLiteDatabase) -> None:
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("StorageHealthService requires SQLiteDatabase.")
        self._database = database

    def snapshot(self) -> StorageHealthSnapshot:
        observed_at_us = utc_now_us()
        database_path = self._database.path

        try:
            self._database.connection
        except DatabaseNotStartedError:
            return StorageHealthSnapshot(
                status="unavailable",
                database_open=False,
                database_path=str(database_path),
                database_size_bytes=None,
                wal_size_bytes=None,
                observed_at_us=observed_at_us,
                detail="SQLite database service is not started.",
            )

        try:
            database_size_bytes = _file_size(database_path)
            wal_size_bytes = _optional_file_size(_wal_path(database_path))
        except OSError as exc:
            return StorageHealthSnapshot(
                status="error",
                database_open=True,
                database_path=str(database_path),
                database_size_bytes=None,
                wal_size_bytes=None,
                observed_at_us=observed_at_us,
                detail=f"Storage telemetry read failed: {type(exc).__name__}.",
            )

        return StorageHealthSnapshot(
            status="available",
            database_open=True,
            database_path=str(database_path),
            database_size_bytes=database_size_bytes,
            wal_size_bytes=wal_size_bytes,
            observed_at_us=observed_at_us,
            detail=None,
        )


def _wal_path(database_path: Path) -> Path:
    return database_path.with_name(database_path.name + "-wal")


def _file_size(path: Path) -> int:
    return path.stat().st_size


def _optional_file_size(path: Path) -> int:
    try:
        return _file_size(path)
    except FileNotFoundError:
        return 0
