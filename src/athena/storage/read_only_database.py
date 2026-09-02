"""Read-only SQLite service for controlled low-space recovery."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from athena.storage.recovery import inspect_database_read_only


class ReadOnlyDatabaseError(RuntimeError):
    """Raised when ATHENA cannot establish a trusted read-only database service."""


class ReadOnlySQLiteDatabase:
    """Open the canonical ATHENA database without any schema or writer mutation."""

    name = "sqlite-database-read-only"

    def __init__(self, path: Path) -> None:
        if not isinstance(path, Path):
            raise TypeError("ReadOnlySQLiteDatabase path must be a pathlib.Path.")
        self.path = path
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise ReadOnlyDatabaseError("ATHENA read-only database service is not started.")
        return self._connection

    def start(self) -> None:
        if self._connection is not None:
            return

        report = inspect_database_read_only(self.path)
        if not report.exists:
            raise ReadOnlyDatabaseError(
                "ATHENA read-only safe mode requires an existing canonical database."
            )

        try:
            connection = sqlite3.connect(
                f"{report.path.resolve(strict=True).as_uri()}?mode=ro",
                uri=True,
                timeout=5.0,
                autocommit=True,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only = ON")
            query_only = connection.execute("PRAGMA query_only").fetchone()
            if query_only is None or int(query_only[0]) != 1:
                raise ReadOnlyDatabaseError(
                    "ATHENA read-only database could not enable query_only mode."
                )
        except ReadOnlyDatabaseError:
            if "connection" in locals():
                connection.close()
            raise
        except (OSError, sqlite3.Error, TypeError, ValueError, IndexError) as exc:
            if "connection" in locals():
                connection.close()
            raise ReadOnlyDatabaseError(
                "ATHENA database could not be opened in read-only safe mode."
            ) from exc

        self._connection = connection

    def stop(self) -> None:
        if self._connection is None:
            return
        self._connection.close()
        self._connection = None
