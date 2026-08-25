"""Read-only storage health telemetry for local Core and desktop surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from athena.common.time import utc_now_us
from athena.storage.database import DatabaseNotStartedError, SQLiteDatabase

StorageHealthStatus = Literal["available", "unavailable", "error"]


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
