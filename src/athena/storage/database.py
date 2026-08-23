"""SQLite lifecycle and explicit transaction control."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

from athena.common.time import utc_now_us
from athena.storage.connection_policy import (
    DEFAULT_BUSY_TIMEOUT_MS,
    apply_and_verify_connection_policy,
    validated_busy_timeout_ms,
)
from athena.storage.recovery import inspect_database_read_only
from athena.storage.schema import initialize_schema

_ReadResultT = TypeVar("_ReadResultT")
_WriteGate = Callable[[], None]


class DatabaseNotStartedError(RuntimeError):
    """Raised when database access is attempted before service startup."""


class DatabaseSnapshotChangedError(RuntimeError):
    """A stable read snapshot is stale before a guarded write."""


def _nonnegative_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")
    return value


@dataclass(frozen=True, slots=True)
class DatabaseReadSnapshot:
    data_version: int
    schema_version: int
    total_changes: int

    def __post_init__(self) -> None:
        _nonnegative_int(self.data_version, "Database snapshot data_version")
        _nonnegative_int(self.schema_version, "Database snapshot schema_version")
        _nonnegative_int(self.total_changes, "Database snapshot total_changes")


class SQLiteDatabase:
    """Local transactional ATHENA database service.

    The live database is intentionally local. Writes use explicit
    ``BEGIN IMMEDIATE`` transactions so later writer coordination can be added
    without changing repository semantics.
    """

    name = "sqlite-database"

    def __init__(
        self,
        path: Path,
        *,
        busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
    ) -> None:
        if not isinstance(path, Path):
            raise TypeError("SQLiteDatabase path must be a pathlib.Path.")
        self.path = path
        self.busy_timeout_ms = validated_busy_timeout_ms(busy_timeout_ms)
        self._connection: sqlite3.Connection | None = None
        self._noncritical_write_gate: _WriteGate | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            raise DatabaseNotStartedError("ATHENA database service is not started.")
        return self._connection

    def configure_noncritical_write_gate(self, gate: _WriteGate | None) -> None:
        """Bind the runtime gate checked before every canonical write transaction."""
        if gate is not None and not callable(gate):
            raise TypeError("SQLiteDatabase noncritical write gate must be callable or None.")
        if self._connection is not None:
            raise RuntimeError(
                "SQLiteDatabase noncritical write gate must be configured before startup."
            )
        self._noncritical_write_gate = gate

    def start(self) -> None:
        if self._connection is not None:
            return

        inspect_database_read_only(self.path)

        connection = sqlite3.connect(
            self.path,
            timeout=self.busy_timeout_ms / 1_000.0,
            autocommit=True,
        )
        connection.row_factory = sqlite3.Row

        try:
            initialize_schema(connection, created_at_us=utc_now_us())
            apply_and_verify_connection_policy(
                connection,
                busy_timeout_ms=self.busy_timeout_ms,
            )
        except Exception:
            connection.close()
            raise

        self._connection = connection

    def stop(self) -> None:
        if self._connection is None:
            return
        self._connection.close()
        self._connection = None

    @staticmethod
    def _ensure_no_active_transaction(connection: sqlite3.Connection) -> None:
        """Reject nested ATHENA write transactions."""
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be a sqlite3.Connection.")
        if connection.in_transaction:
            raise RuntimeError("Nested ATHENA write transactions are not supported.")

    @staticmethod
    def _rollback_if_active(connection: sqlite3.Connection) -> None:
        """Rollback only while SQLite still reports an active transaction."""
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be a sqlite3.Connection.")
        if connection.in_transaction:
            connection.execute("ROLLBACK")

    @staticmethod
    def _commit_active_transaction(connection: sqlite3.Connection) -> None:
        """Commit the transaction or fail if it ended unexpectedly."""
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be a sqlite3.Connection.")
        if not connection.in_transaction:
            raise RuntimeError(
                "ATHENA write transaction ended unexpectedly before commit."
            )
        connection.execute("COMMIT")

    @staticmethod
    def _read_snapshot_marker(
        connection: sqlite3.Connection,
    ) -> DatabaseReadSnapshot:
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be a sqlite3.Connection.")
        data_version = connection.execute("PRAGMA data_version").fetchone()
        schema_version = connection.execute("PRAGMA schema_version").fetchone()

        if data_version is None or schema_version is None:
            raise RuntimeError("ATHENA could not read the SQLite snapshot marker.")

        return DatabaseReadSnapshot(
            data_version=int(data_version[0]),
            schema_version=int(schema_version[0]),
            total_changes=int(connection.total_changes),
        )

    def stable_read(
        self,
        reader: Callable[[sqlite3.Connection], _ReadResultT],
        *,
        max_attempts: int = 3,
    ) -> tuple[_ReadResultT, DatabaseReadSnapshot]:
        """Run a multi-query read on one stable WAL snapshot.

        The callback is forced read-only with ``PRAGMA query_only``. If
        another connection commits while the read snapshot is open, retry
        rather than returning a result assembled from a stale boundary.
        """
        if not callable(reader):
            raise TypeError("Stable database read requires a callable reader.")
        if (
            isinstance(max_attempts, bool)
            or not isinstance(max_attempts, int)
            or max_attempts < 1
        ):
            raise ValueError(
                "Stable database read requires max_attempts to be an integer >= 1."
            )

        connection = self.connection
        self._ensure_no_active_transaction(connection)

        query_only_row = connection.execute("PRAGMA query_only").fetchone()
        if query_only_row is None:
            raise RuntimeError("ATHENA could not read SQLite query_only state.")
        previous_query_only = int(query_only_row[0])

        connection.execute("PRAGMA query_only = ON")
        try:
            for _attempt in range(max_attempts):
                self._ensure_no_active_transaction(connection)
                before = self._read_snapshot_marker(connection)

                connection.execute("BEGIN")
                try:
                    result = reader(connection)
                except BaseException:
                    self._rollback_if_active(connection)
                    raise

                if not connection.in_transaction:
                    raise RuntimeError(
                        "ATHENA stable read transaction ended unexpectedly before commit."
                    )

                try:
                    connection.execute("COMMIT")
                except BaseException:
                    self._rollback_if_active(connection)
                    raise

                after = self._read_snapshot_marker(connection)
                if before == after:
                    return result, after

            raise DatabaseSnapshotChangedError(
                "ATHENA database changed repeatedly during stable read."
            )
        finally:
            connection.execute("PRAGMA query_only = " + str(previous_query_only))

    def assert_snapshot_current(
        self,
        connection: sqlite3.Connection,
        snapshot: DatabaseReadSnapshot,
    ) -> None:
        """Fence a stable read immediately after BEGIN IMMEDIATE."""
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be a sqlite3.Connection.")
        if not isinstance(snapshot, DatabaseReadSnapshot):
            raise TypeError("snapshot must be a DatabaseReadSnapshot.")
        if connection is not self.connection:
            raise RuntimeError(
                "Database snapshot fence used with another connection."
            )
        if not connection.in_transaction:
            raise RuntimeError(
                "Database snapshot fence requires an active transaction."
            )

        current = self._read_snapshot_marker(connection)
        if current != snapshot:
            raise DatabaseSnapshotChangedError(
                "ATHENA database changed after stable dependency scan."
            )

    @contextmanager
    def write_transaction(self) -> Iterator[sqlite3.Connection]:
        """Yield one gated immediate transaction with rollback on failure."""
        connection = self.connection
        self._ensure_no_active_transaction(connection)

        gate = self._noncritical_write_gate
        if gate is not None:
            gate()

        connection.execute("BEGIN IMMEDIATE")
        try:
            yield connection
        except BaseException:
            self._rollback_if_active(connection)
            raise
        else:
            try:
                self._commit_active_transaction(connection)
            except BaseException:
                self._rollback_if_active(connection)
                raise