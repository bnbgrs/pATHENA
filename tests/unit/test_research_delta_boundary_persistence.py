from __future__ import annotations

import sqlite3
import uuid

from athena.common.ids import uuid_to_blob
from athena.research.delta_boundary import _delta_boundary_from_row
from athena.storage.database import SQLiteDatabase
from athena.storage.research_delta_migration import verify_schema_v41
from athena.storage.schema_contract import (
    RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
    RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
    SCHEMA_VERSION,
)


def test_fresh_database_reaches_research_delta_boundary_schema(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        connection = database.connection
        assert SCHEMA_VERSION == RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION == 41
        assert int(connection.execute("PRAGMA user_version").fetchone()[0]) == 41
        metadata = connection.execute(
            "SELECT schema_version, last_migration_id, minimum_reader_version "
            "FROM schema_metadata WHERE singleton_id = 1"
        ).fetchone()
        assert metadata is not None
        assert tuple(metadata) == (
            41,
            RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
            41,
        )
        columns = {
            str(row[1])
            for row in connection.execute(
                "PRAGMA table_info(research_delta_boundaries)"
            )
        }
        assert columns == {
            "scope_id",
            "base_scope_id",
            "lower_commit_seq",
            "created_at_us",
        }
        verify_schema_v41(connection)
    finally:
        database.stop()

    # Restart must verify the already-migrated schema rather than reapplying it.
    database.start()
    try:
        verify_schema_v41(database.connection)
        assert int(database.connection.execute("PRAGMA user_version").fetchone()[0]) == 41
    finally:
        database.stop()


def test_delta_boundary_row_mapping_preserves_exact_identity() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE boundary (
            scope_id BLOB NOT NULL,
            base_scope_id BLOB NOT NULL,
            lower_commit_seq INTEGER NOT NULL,
            created_at_us INTEGER NOT NULL
        )
        """
    )
    scope_id = uuid.uuid4()
    base_scope_id = uuid.uuid4()
    connection.execute(
        "INSERT INTO boundary VALUES (?, ?, ?, ?)",
        (uuid_to_blob(scope_id), uuid_to_blob(base_scope_id), 73, 101),
    )
    row = connection.execute("SELECT * FROM boundary").fetchone()
    assert row is not None

    record = _delta_boundary_from_row(row)

    assert record.scope_id == scope_id
    assert record.base_scope_id == base_scope_id
    assert record.lower_commit_seq == 73
    assert record.created_at_us == 101
