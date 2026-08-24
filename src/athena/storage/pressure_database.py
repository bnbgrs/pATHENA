"""Disk-pressure-aware SQLite transaction boundary."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from athena.storage.database import SQLiteDatabase
from athena.storage.disk_pressure import DiskPressureController


class PressureGuardedSQLiteDatabase(SQLiteDatabase):
    """Block ordinary writes at EMERGENCY while retaining explicit recovery writes."""

    def __init__(
        self,
        path: Path,
        *,
        disk_pressure: DiskPressureController,
    ) -> None:
        if not isinstance(disk_pressure, DiskPressureController):
            raise TypeError("disk_pressure must be DiskPressureController.")
        super().__init__(path)
        self.disk_pressure = disk_pressure

    @contextmanager
    def write_transaction(self) -> Iterator[sqlite3.Connection]:
        """Apply the current noncritical-write pressure gate before BEGIN IMMEDIATE."""
        self.disk_pressure.assert_noncritical_write_allowed()
        with super().write_transaction() as connection:
            yield connection

    @contextmanager
    def critical_write_transaction(self) -> Iterator[sqlite3.Connection]:
        """Explicit recovery-only write path that bypasses the noncritical gate.

        Callers must opt in deliberately. This does not alter transaction,
        rollback, or commit semantics inherited from ``SQLiteDatabase``.
        """
        with super().write_transaction() as connection:
            yield connection
