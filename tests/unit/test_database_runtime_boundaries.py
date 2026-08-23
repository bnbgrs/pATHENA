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
