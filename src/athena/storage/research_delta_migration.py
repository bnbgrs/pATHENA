"""Schema v41 migration for durable Delta Research lower boundaries."""

from __future__ import annotations

import sqlite3

from athena.storage.schema_contract import (
    ATHENA_APPLICATION_ID,
    BLOB_FORMAT_VERSION,
    RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
    RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
    STORAGE_LAYOUT_VERSION,
    DatabaseCompatibilityError,
    _user_tables,
)
from athena.storage.schema_verification import _verify_schema_v39, _verify_schema_v40


def migrate_schema_v40_to_v41(connection: sqlite3.Connection) -> None:
    """Persist the exact prior ResearchScope and lower commit bound for Delta Research."""
    if connection.in_transaction:
        raise RuntimeError("Research Delta boundary migration requires no active transaction.")

    _verify_schema_v40(connection)

    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            CREATE TABLE research_delta_boundaries (
                scope_id BLOB(16) PRIMARY KEY
                    CHECK(length(scope_id) = 16),
                base_scope_id BLOB(16) NOT NULL
                    CHECK(length(base_scope_id) = 16),
                lower_commit_seq INTEGER NOT NULL
                    CHECK(lower_commit_seq >= 0),
                created_at_us INTEGER NOT NULL
                    CHECK(created_at_us >= 0),
                FOREIGN KEY(scope_id)
                    REFERENCES research_scopes(scope_id)
                    ON DELETE CASCADE,
                FOREIGN KEY(base_scope_id)
                    REFERENCES research_scopes(scope_id),
                CHECK(scope_id != base_scope_id)
            ) WITHOUT ROWID
            """
        )
        connection.execute(
            """
            CREATE INDEX idx_research_delta_boundaries_base
            ON research_delta_boundaries(base_scope_id, lower_commit_seq, scope_id)
            """
        )
        connection.execute(
            """
            UPDATE schema_metadata
            SET schema_version = ?,
                last_migration_id = ?,
                minimum_reader_version = ?
            WHERE singleton_id = 1
            """,
            (
                RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
                RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
                RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
            ),
        )
        connection.execute(
            f"PRAGMA user_version = {RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION}"
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.rollback()
        raise


def _verify_grounded_receipts_v40_compatible(connection: sqlite3.Connection) -> None:
    receipt_columns = {
        str(row[1])
        for row in connection.execute("PRAGMA table_info(grounded_response_receipts)")
    }
    if not {
        "operation_id",
        "chat_id",
        "processing_run_id",
        "payload_json",
        "payload_sha256",
        "format_version",
        "created_at_us",
    }.issubset(receipt_columns):
        raise DatabaseCompatibilityError(
            "ATHENA Grounded response receipt columns are incomplete."
        )

    receipt_indexes = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' "
            "AND name = 'idx_grounded_response_receipts_chat'"
        )
    }
    if receipt_indexes != {"idx_grounded_response_receipts_chat"}:
        raise DatabaseCompatibilityError(
            "ATHENA Grounded response receipt index is missing."
        )

    receipt_foreign_keys = {
        (str(row[3]), str(row[2]), str(row[4]), str(row[6]).upper())
        for row in connection.execute("PRAGMA foreign_key_list(grounded_response_receipts)")
    }
    if ("chat_id", "chats", "chat_id", "CASCADE") not in receipt_foreign_keys:
        raise DatabaseCompatibilityError(
            "ATHENA Grounded response receipt chat foreign key is missing."
        )

    invalid_receipts = connection.execute(
        """
        SELECT COUNT(*)
        FROM grounded_response_receipts
        WHERE length(operation_id) != 16
           OR length(chat_id) != 16
           OR length(processing_run_id) != 16
           OR length(payload_json) <= 1
           OR length(payload_sha256) != 64
           OR format_version != 1
           OR created_at_us < 0
        """
    ).fetchone()
    if invalid_receipts is None or int(invalid_receipts[0]) != 0:
        raise DatabaseCompatibilityError(
            "ATHENA Grounded response receipt rows are invalid."
        )


def verify_schema_v41(connection: sqlite3.Connection) -> None:
    """Verify v41 plus every inherited v40 durability contract without mutation."""
    application_id = int(connection.execute("PRAGMA application_id").fetchone()[0])
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if application_id != ATHENA_APPLICATION_ID:
        raise DatabaseCompatibilityError("ATHENA application_id verification failed.")
    if user_version != RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION:
        raise DatabaseCompatibilityError("ATHENA schema version verification failed.")

    metadata = connection.execute(
        "SELECT schema_version, storage_layout_version, blob_format_version, "
        "last_migration_id, minimum_reader_version "
        "FROM schema_metadata WHERE singleton_id = 1"
    ).fetchone()
    expected = (
        RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
        STORAGE_LAYOUT_VERSION,
        BLOB_FORMAT_VERSION,
        RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
        RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
    )
    if metadata is None or tuple(metadata) != expected:
        raise DatabaseCompatibilityError("ATHENA schema_metadata verification failed.")

    # v39 accepts the expected version/migration as parameters and therefore
    # verifies the full inherited schema without pretending this is still v39.
    _verify_schema_v39(
        connection,
        schema_version=RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION,
        migration_id=RESEARCH_DELTA_BOUNDARY_MIGRATION_ID,
    )

    required_tables = {"grounded_response_receipts", "research_delta_boundaries"}
    missing = required_tables.difference(_user_tables(connection))
    if missing:
        raise DatabaseCompatibilityError(
            "ATHENA v41 schema is incomplete: " + ", ".join(sorted(missing)) + "."
        )

    _verify_grounded_receipts_v40_compatible(connection)

    delta_columns = {
        str(row[1])
        for row in connection.execute("PRAGMA table_info(research_delta_boundaries)")
    }
    if delta_columns != {
        "scope_id",
        "base_scope_id",
        "lower_commit_seq",
        "created_at_us",
    }:
        raise DatabaseCompatibilityError(
            "ATHENA Research Delta boundary columns are incomplete."
        )

    indexes = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' "
            "AND name = 'idx_research_delta_boundaries_base'"
        )
    }
    if indexes != {"idx_research_delta_boundaries_base"}:
        raise DatabaseCompatibilityError(
            "ATHENA Research Delta boundary index is missing."
        )

    foreign_keys = {
        (str(row[3]), str(row[2]), str(row[4]), str(row[6]).upper())
        for row in connection.execute("PRAGMA foreign_key_list(research_delta_boundaries)")
    }
    if not {
        ("scope_id", "research_scopes", "scope_id", "CASCADE"),
        ("base_scope_id", "research_scopes", "scope_id", "NO ACTION"),
    }.issubset(foreign_keys):
        raise DatabaseCompatibilityError(
            "ATHENA Research Delta boundary foreign keys are incomplete."
        )

    invalid = connection.execute(
        """
        SELECT COUNT(*)
        FROM research_delta_boundaries AS boundary
        JOIN research_scopes AS delta_scope
          ON delta_scope.scope_id = boundary.scope_id
        JOIN research_scopes AS base_scope
          ON base_scope.scope_id = boundary.base_scope_id
        WHERE delta_scope.mode != 'delta'
           OR base_scope.state != 'completed'
           OR boundary.lower_commit_seq != base_scope.snapshot_commit_seq
           OR boundary.lower_commit_seq > delta_scope.snapshot_commit_seq
           OR boundary.created_at_us < 0
        """
    ).fetchone()
    if invalid is None or int(invalid[0]) != 0:
        raise DatabaseCompatibilityError(
            "ATHENA Research Delta boundary rows are inconsistent."
        )

    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise DatabaseCompatibilityError("ATHENA foreign-key verification failed.")
