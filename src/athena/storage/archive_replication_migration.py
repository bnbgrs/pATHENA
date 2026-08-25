"""Restart-safe Raw Archive replication schema migration."""

from __future__ import annotations

import sqlite3

from athena.storage.schema_contract import (
    ARCHIVE_REPLICATION_MIGRATION_ID,
    ARCHIVE_REPLICATION_SCHEMA_VERSION,
    DatabaseCompatibilityError,
)

_OUTBOX_TABLE = "archive_replication_outbox"
_OUTBOX_INDEX = "idx_archive_replication_outbox_state"
_WATERMARK_TABLE = "archive_replication_watermark"
_OUTBOX_TRIGGER = "trg_blob_records_archive_replication_outbox"

_OUTBOX_TABLE_SQL = """
CREATE TABLE archive_replication_outbox (
    outbox_seq INTEGER PRIMARY KEY AUTOINCREMENT,
    blob_id BLOB(16) NOT NULL UNIQUE
        CHECK(length(blob_id) = 16),
    target_role TEXT NOT NULL
        CHECK(target_role = 'archive_root'),
    state TEXT NOT NULL
        CHECK(state IN ('pending', 'verified')),
    attempt_count INTEGER NOT NULL DEFAULT 0
        CHECK(attempt_count >= 0),
    created_at_us INTEGER NOT NULL,
    last_attempt_at_us INTEGER NULL,
    last_error_code TEXT NULL,
    last_error_detail TEXT NULL,
    verified_at_us INTEGER NULL,
    FOREIGN KEY(blob_id)
        REFERENCES blob_records(blob_id),
    CHECK(
        (state = 'pending' AND verified_at_us IS NULL)
        OR
        (state = 'verified' AND verified_at_us IS NOT NULL)
    )
)
"""

_OUTBOX_INDEX_SQL = """
CREATE INDEX idx_archive_replication_outbox_state
ON archive_replication_outbox(
    state,
    outbox_seq
)
"""

_WATERMARK_TABLE_SQL = """
CREATE TABLE archive_replication_watermark (
    singleton_id INTEGER PRIMARY KEY
        CHECK(singleton_id = 1),
    contiguous_verified_seq INTEGER NOT NULL
        CHECK(contiguous_verified_seq >= 0),
    updated_at_us INTEGER NOT NULL
)
"""

_OUTBOX_TRIGGER_SQL = """
CREATE TRIGGER trg_blob_records_archive_replication_outbox
AFTER INSERT ON blob_records
WHEN NEW.storage_area = 'spool'
BEGIN
    INSERT OR IGNORE INTO archive_replication_outbox (
        blob_id,
        target_role,
        state,
        attempt_count,
        created_at_us,
        last_attempt_at_us,
        last_error_code,
        last_error_detail,
        verified_at_us
    ) VALUES (
        NEW.blob_id,
        'archive_root',
        'pending',
        0,
        NEW.created_at_us,
        NULL,
        NULL,
        NULL,
        NULL
    );
END
"""


def _normalized_schema_sql(value: str) -> str:
    """Normalize formatting only; semantic drift must remain observable."""
    return " ".join(value.strip().rstrip(";").split()).casefold()


def _read_schema_object(
    connection: sqlite3.Connection,
    *,
    name: str,
) -> tuple[str, str] | None:
    row = connection.execute(
        """
        SELECT type, sql
        FROM sqlite_schema
        WHERE name = ?
        """,
        (name,),
    ).fetchone()
    if row is None:
        return None
    object_type = str(row[0])
    sql = row[1]
    if sql is None:
        raise DatabaseCompatibilityError(
            f"Archive replication object {name!r} has no durable schema SQL."
        )
    return object_type, str(sql)


def _require_compatible_or_missing(
    connection: sqlite3.Connection,
    *,
    name: str,
    object_type: str,
    expected_sql: str,
) -> bool:
    """Return True when the canonical object is absent, otherwise validate it."""
    existing = _read_schema_object(connection, name=name)
    if existing is None:
        return True

    existing_type, existing_sql = existing
    if existing_type != object_type:
        raise DatabaseCompatibilityError(
            f"Archive replication object {name!r} has incompatible type "
            f"{existing_type!r}."
        )
    if _normalized_schema_sql(existing_sql) != _normalized_schema_sql(expected_sql):
        raise DatabaseCompatibilityError(
            f"Archive replication object {name!r} has incompatible schema."
        )
    return False


def _validate_existing_partial_state(connection: sqlite3.Connection) -> dict[str, bool]:
    missing = {
        _OUTBOX_TABLE: _require_compatible_or_missing(
            connection,
            name=_OUTBOX_TABLE,
            object_type="table",
            expected_sql=_OUTBOX_TABLE_SQL,
        ),
        _WATERMARK_TABLE: _require_compatible_or_missing(
            connection,
            name=_WATERMARK_TABLE,
            object_type="table",
            expected_sql=_WATERMARK_TABLE_SQL,
        ),
        _OUTBOX_INDEX: _require_compatible_or_missing(
            connection,
            name=_OUTBOX_INDEX,
            object_type="index",
            expected_sql=_OUTBOX_INDEX_SQL,
        ),
        _OUTBOX_TRIGGER: _require_compatible_or_missing(
            connection,
            name=_OUTBOX_TRIGGER,
            object_type="trigger",
            expected_sql=_OUTBOX_TRIGGER_SQL,
        ),
    }

    if not missing[_OUTBOX_INDEX] and missing[_OUTBOX_TABLE]:
        raise DatabaseCompatibilityError(
            "Archive replication outbox index exists without its canonical table."
        )
    if not missing[_OUTBOX_TRIGGER] and missing[_OUTBOX_TABLE]:
        raise DatabaseCompatibilityError(
            "Archive replication trigger exists without its canonical outbox table."
        )

    if not missing[_OUTBOX_TABLE]:
        violations = connection.execute(
            f"PRAGMA foreign_key_check({_OUTBOX_TABLE})"
        ).fetchall()
        if violations:
            raise DatabaseCompatibilityError(
                "Archive replication outbox contains invalid foreign-key references."
            )

    return missing


def migrate_schema_v30_to_v31_restart_safe(connection: sqlite3.Connection) -> None:
    """Complete v30->v31 without destroying compatible partially-created state.

    A normal SQLite rollback of the historical migration is atomic, but databases
    can still arrive with v31 objects while durable version metadata remains v30
    (for example after historical preview/fixture tooling or manual recovery).
    Existing objects are therefore accepted only when their durable DDL matches
    the canonical v31 contract exactly. Incompatible objects fail closed before
    any schema-version advancement.
    """
    if connection.in_transaction:
        raise RuntimeError(
            "Archive replication migration requires no active transaction."
        )

    missing = _validate_existing_partial_state(connection)

    try:
        connection.execute("BEGIN IMMEDIATE")

        if missing[_OUTBOX_TABLE]:
            connection.execute(_OUTBOX_TABLE_SQL)
        if missing[_OUTBOX_INDEX]:
            connection.execute(_OUTBOX_INDEX_SQL)
        if missing[_WATERMARK_TABLE]:
            connection.execute(_WATERMARK_TABLE_SQL)
        connection.execute(
            """
            INSERT OR IGNORE INTO archive_replication_watermark (
                singleton_id,
                contiguous_verified_seq,
                updated_at_us
            ) VALUES (
                1,
                0,
                CAST(strftime('%s','now') AS INTEGER) * 1000000
            )
            """
        )
        if missing[_OUTBOX_TRIGGER]:
            connection.execute(_OUTBOX_TRIGGER_SQL)

        connection.execute(
            """
            INSERT OR IGNORE INTO archive_replication_outbox (
                blob_id,
                target_role,
                state,
                attempt_count,
                created_at_us,
                last_attempt_at_us,
                last_error_code,
                last_error_detail,
                verified_at_us
            )
            SELECT
                blob_id,
                'archive_root',
                'pending',
                0,
                created_at_us,
                NULL,
                NULL,
                NULL,
                NULL
            FROM blob_records
            WHERE storage_area = 'spool'
            ORDER BY created_at_us, blob_id
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
                ARCHIVE_REPLICATION_SCHEMA_VERSION,
                ARCHIVE_REPLICATION_MIGRATION_ID,
                ARCHIVE_REPLICATION_SCHEMA_VERSION,
            ),
        )
        connection.execute(
            f"PRAGMA user_version = {ARCHIVE_REPLICATION_SCHEMA_VERSION}"
        )
        connection.execute("COMMIT")
    except BaseException:
        connection.rollback()
        raise
