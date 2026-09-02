from __future__ import annotations

import sqlite3

import pytest

from athena.storage.archive_replication_migration import (
    migrate_schema_v30_to_v31_restart_safe,
)
from athena.storage.schema_contract import (
    ARCHIVE_REPLICATION_MIGRATION_ID,
    ARCHIVE_REPLICATION_SCHEMA_VERSION,
    DatabaseCompatibilityError,
)


def _v30_fixture() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:", autocommit=True)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE schema_metadata (
            singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
            schema_epoch INTEGER NOT NULL,
            schema_version INTEGER NOT NULL,
            storage_layout_version INTEGER NOT NULL,
            blob_format_version INTEGER NOT NULL,
            created_at_us INTEGER NOT NULL,
            last_migration_id TEXT NULL,
            minimum_reader_version INTEGER NOT NULL
        );
        INSERT INTO schema_metadata VALUES (1, 1, 30, 1, 1, 1, 'v30-fixture', 30);

        CREATE TABLE entity_registry (
            entity_id BLOB(16) PRIMARY KEY
        ) WITHOUT ROWID;

        CREATE TABLE blob_records (
            blob_id BLOB(16) PRIMARY KEY CHECK(length(blob_id) = 16),
            byte_length INTEGER NOT NULL CHECK(byte_length >= 0),
            media_type TEXT NULL,
            storage_area TEXT NOT NULL CHECK(storage_area IN ('archive', 'spool')),
            storage_locator TEXT NOT NULL CHECK(length(storage_locator) > 0),
            integrity_sha256 BLOB(32) NOT NULL CHECK(length(integrity_sha256) = 32),
            encryption_state TEXT NOT NULL CHECK(encryption_state IN ('none')),
            created_at_us INTEGER NOT NULL,
            verified_at_us INTEGER NOT NULL,
            UNIQUE(integrity_sha256, byte_length, encryption_state),
            UNIQUE(storage_area, storage_locator),
            FOREIGN KEY(blob_id) REFERENCES entity_registry(entity_id)
        ) WITHOUT ROWID;

        PRAGMA user_version = 30;
        """
    )
    return connection


def _insert_spool_blob(connection: sqlite3.Connection, marker: int) -> bytes:
    blob_id = marker.to_bytes(16, "big")
    connection.execute(
        "INSERT INTO entity_registry(entity_id) VALUES (?)",
        (blob_id,),
    )
    connection.execute(
        """
        INSERT INTO blob_records (
            blob_id, byte_length, media_type, storage_area, storage_locator,
            integrity_sha256, encryption_state, created_at_us, verified_at_us
        ) VALUES (?, 7, 'text/plain', 'spool', ?, ?, 'none', ?, ?)
        """,
        (
            blob_id,
            f"spool/{marker}",
            bytes([marker % 251]) * 32,
            marker,
            marker,
        ),
    )
    return blob_id


def _version_state(connection: sqlite3.Connection) -> tuple[int, int, str | None, int]:
    metadata = connection.execute(
        """
        SELECT schema_version, last_migration_id, minimum_reader_version
        FROM schema_metadata
        WHERE singleton_id = 1
        """
    ).fetchone()
    assert metadata is not None
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    return int(metadata[0]), user_version, metadata[1], int(metadata[2])


def test_archive_replication_migration_fresh_v30_state() -> None:
    connection = _v30_fixture()
    blob_id = _insert_spool_blob(connection, 11)

    migrate_schema_v30_to_v31_restart_safe(connection)

    assert _version_state(connection) == (
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
        ARCHIVE_REPLICATION_MIGRATION_ID,
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
    )
    outbox = connection.execute(
        """
        SELECT blob_id, target_role, state, attempt_count
        FROM archive_replication_outbox
        """
    ).fetchall()
    assert outbox == [(blob_id, "archive_root", "pending", 0)]
    assert connection.execute(
        "SELECT contiguous_verified_seq FROM archive_replication_watermark"
    ).fetchone() == (0,)


def test_archive_replication_migration_resumes_compatible_partial_state() -> None:
    connection = _v30_fixture()
    first_blob = _insert_spool_blob(connection, 21)
    migrate_schema_v30_to_v31_restart_safe(connection)

    connection.execute(
        "UPDATE archive_replication_watermark SET contiguous_verified_seq = 7"
    )
    connection.execute(
        """
        UPDATE schema_metadata
        SET schema_version = 30,
            last_migration_id = 'interrupted-preview',
            minimum_reader_version = 30
        WHERE singleton_id = 1
        """
    )
    connection.execute("PRAGMA user_version = 30")
    second_blob = _insert_spool_blob(connection, 22)

    migrate_schema_v30_to_v31_restart_safe(connection)
    migrate_schema_v30_to_v31_restart_safe(connection)

    rows = connection.execute(
        "SELECT blob_id FROM archive_replication_outbox ORDER BY blob_id"
    ).fetchall()
    assert rows == [(first_blob,), (second_blob,)]
    assert connection.execute(
        "SELECT contiguous_verified_seq FROM archive_replication_watermark"
    ).fetchone() == (7,)
    assert _version_state(connection) == (
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
        ARCHIVE_REPLICATION_MIGRATION_ID,
        ARCHIVE_REPLICATION_SCHEMA_VERSION,
    )


def test_archive_replication_migration_rejects_incompatible_existing_outbox() -> None:
    connection = _v30_fixture()
    connection.execute(
        """
        CREATE TABLE archive_replication_outbox (
            archive_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "INSERT INTO archive_replication_outbox VALUES ('keep-me', 'payload')"
    )

    with pytest.raises(
        DatabaseCompatibilityError,
        match="archive_replication_outbox.*incompatible schema",
    ):
        migrate_schema_v30_to_v31_restart_safe(connection)

    assert connection.execute(
        "SELECT archive_id, payload FROM archive_replication_outbox"
    ).fetchall() == [("keep-me", "payload")]
    assert _version_state(connection) == (30, 30, "v30-fixture", 30)
    assert connection.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_schema
        WHERE name IN (
            'archive_replication_watermark',
            'idx_archive_replication_outbox_state',
            'trg_blob_records_archive_replication_outbox'
        )
        """
    ).fetchone() == (0,)
