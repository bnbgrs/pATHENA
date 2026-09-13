from __future__ import annotations

import sqlite3
from pathlib import Path

from athena.storage.schema import SCHEMA_VERSION, initialize_schema


def test_reinitializing_current_schema_does_not_reapply_column_migrations(
    tmp_path: Path,
) -> None:
    database = (tmp_path / "athena.db").absolute()
    connection = sqlite3.connect(database, autocommit=True)
    connection.row_factory = sqlite3.Row
    try:
        initialize_schema(connection, created_at_us=1)
        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION

        initialize_schema(connection, created_at_us=2)

        assert connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    finally:
        connection.close()
