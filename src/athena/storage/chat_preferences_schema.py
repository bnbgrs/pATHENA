"""Schema v43 for durable per-chat user preferences."""

from __future__ import annotations

import sqlite3

from athena.storage import schema_contract

_COLUMNS = ("chat_id", "pinned", "updated_at_us", "updated_by_actor_id")


def migrate_schema_v42_to_v43(connection: sqlite3.Connection) -> None:
    """Add canonical chat preferences without rewriting chat payloads."""
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current != schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION:
        raise schema_contract.DatabaseCompatibilityError(
            "Chat preferences migration requires canonical schema v42."
        )

    existing = set(schema_contract._user_tables(connection))
    if "chat_preferences" in existing:
        columns = tuple(
            str(row[1])
            for row in connection.execute("PRAGMA table_info(chat_preferences)").fetchall()
        )
        if columns != _COLUMNS:
            raise schema_contract.DatabaseCompatibilityError(
                "Existing chat preferences state has an incompatible schema."
            )

    connection.executescript(
        f"""
        BEGIN IMMEDIATE;

        CREATE TABLE IF NOT EXISTS chat_preferences (
            chat_id BLOB(16) PRIMARY KEY CHECK(length(chat_id) = 16),
            pinned INTEGER NOT NULL DEFAULT 0 CHECK(pinned IN (0, 1)),
            updated_at_us INTEGER NOT NULL CHECK(updated_at_us >= 0),
            updated_by_actor_id BLOB(16) NOT NULL CHECK(length(updated_by_actor_id) = 16),
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE RESTRICT,
            FOREIGN KEY(updated_by_actor_id) REFERENCES actors(actor_id) ON DELETE RESTRICT
        ) WITHOUT ROWID;

        CREATE INDEX IF NOT EXISTS idx_chat_preferences_pinned
            ON chat_preferences(pinned DESC, updated_at_us DESC, chat_id);

        UPDATE schema_metadata
        SET schema_version = {schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION},
            last_migration_id = '{schema_contract.CHAT_PREFERENCES_MIGRATION_ID}',
            minimum_reader_version = {schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION}
        WHERE singleton_id = 1;

        PRAGMA user_version = {schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION};
        COMMIT;
        """
    )


def verify_schema_v43(connection: sqlite3.Connection) -> None:
    """Fail closed if durable chat preference storage drifted."""
    if int(connection.execute("PRAGMA user_version").fetchone()[0]) != (
        schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION
    ):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences schema version verification failed."
        )

    metadata = connection.execute(
        """
        SELECT schema_version, storage_layout_version, blob_format_version,
               last_migration_id, minimum_reader_version
        FROM schema_metadata
        WHERE singleton_id = 1
        """
    ).fetchone()
    expected = (
        schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION,
        schema_contract.STORAGE_LAYOUT_VERSION,
        schema_contract.BLOB_FORMAT_VERSION,
        schema_contract.CHAT_PREFERENCES_MIGRATION_ID,
        schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION,
    )
    if metadata is None or tuple(metadata) != expected:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences schema_metadata verification failed."
        )

    if "chat_preferences" not in schema_contract._user_tables(connection):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences table is missing."
        )

    columns = tuple(
        str(row[1])
        for row in connection.execute("PRAGMA table_info(chat_preferences)").fetchall()
    )
    if columns != _COLUMNS:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences schema is incomplete."
        )

    foreign_keys = {
        (str(row[2]), str(row[3]), str(row[4]))
        for row in connection.execute("PRAGMA foreign_key_list(chat_preferences)").fetchall()
    }
    if not {
        ("chats", "chat_id", "chat_id"),
        ("actors", "updated_by_actor_id", "actor_id"),
    }.issubset(foreign_keys):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences foreign keys are incomplete."
        )

    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat preferences foreign-key verification failed."
        )
