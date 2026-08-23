from __future__ import annotations

from pathlib import Path

import pytest

from athena.storage.database import DatabaseReadSnapshot, SQLiteDatabase


def test_database_requires_path_object() -> None:
    with pytest.raises(TypeError, match="pathlib.Path"):
        SQLiteDatabase("athena.db")  # type: ignore[arg-type]


def test_database_snapshot_rejects_bool_and_negative_values() -> None:
    with pytest.raises(TypeError, match="data_version"):
        DatabaseReadSnapshot(
            data_version=True,  # type: ignore[arg-type]
            schema_version=1,
            total_changes=0,
        )
    with pytest.raises(ValueError, match="total_changes"):
        DatabaseReadSnapshot(
            data_version=1,
            schema_version=1,
            total_changes=-1,
        )


def test_stable_read_rejects_non_callable_before_connection_access(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    with pytest.raises(TypeError, match="callable reader"):
        database.stable_read(None)  # type: ignore[arg-type]


def test_stable_read_rejects_invalid_attempt_count(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        with pytest.raises(ValueError, match="max_attempts"):
            database.stable_read(lambda _connection: None, max_attempts=True)
        with pytest.raises(ValueError, match="max_attempts"):
            database.stable_read(lambda _connection: None, max_attempts=0)
    finally:
        database.stop()


def test_stable_read_rejects_nested_transaction(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        connection = database.connection
        connection.execute("BEGIN")
        try:
            with pytest.raises(RuntimeError, match="Nested ATHENA write transactions"):
                database.stable_read(lambda _connection: None)
        finally:
            connection.execute("ROLLBACK")
    finally:
        database.stop()


def test_stable_read_rolls_back_reader_exception_and_restores_query_only(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        connection = database.connection
        before = int(connection.execute("PRAGMA query_only").fetchone()[0])

        def fail(_connection: object) -> None:
            raise LookupError("reader failed")

        with pytest.raises(LookupError, match="reader failed"):
            database.stable_read(fail)  # type: ignore[arg-type]

        assert not connection.in_transaction
        assert int(connection.execute("PRAGMA query_only").fetchone()[0]) == before
    finally:
        database.stop()


def test_stable_read_returns_result_and_current_snapshot(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        result, snapshot = database.stable_read(
            lambda connection: int(connection.execute("SELECT 7").fetchone()[0])
        )
        assert result == 7
        assert isinstance(snapshot, DatabaseReadSnapshot)
        with database.write_transaction() as connection:
            database.assert_snapshot_current(connection, snapshot)
    finally:
        database.stop()


def test_assert_snapshot_rejects_wrong_snapshot_type(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        with database.write_transaction() as connection:
            with pytest.raises(TypeError, match="DatabaseReadSnapshot"):
                database.assert_snapshot_current(
                    connection,
                    object(),  # type: ignore[arg-type]
                )
    finally:
        database.stop()
