"""Schema v43 for durable per-chat UI metadata.

These flags are user interaction metadata. They are intentionally separate from
canonical Knowledge and from immutable chat-message revisions.
"""

from __future__ import annotations

import sqlite3

from athena.storage import schema_contract

_TABLE = "chat_preferences"
_COLUMNS = (
    "chat_id",
    "pinned_at_us",
    "favorited_at_us",
    "updated_at_us",
)


def _verify_compatible_existing_table(connection: sqlite3.Connection) -> None:
    tables = set(schema_contract._user_tables(connection))
    if _TABLE not in tables:
        return

    columns = tuple(
        str(row[1])
        for row in connection.execute(
            "PRAGMA table_info(chat_preferences)"
        ).fetchall()
    )
    if columns != _COLUMNS:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences partial schema is incompatible."
        )

    foreign_keys = {
        (str(row[2]), str(row[3]), str(row[4]))
        for row in connection.execute(
            "PRAGMA foreign_key_list(chat_preferences)"
        ).fetchall()
    }
    if ("chats", "chat_id", "chat_id") not in foreign_keys:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences foreign key is incompatible."
        )


def migrate_schema_v42_to_v43(connection: sqlite3.Connection) -> None:
    """Add durable Pin/Favorite state without rewriting chat payloads."""
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current != schema_contract.JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION:
        raise schema_contract.DatabaseCompatibilityError(
            "Chat preferences migration requires canonical schema v42."
        )

    _verify_compatible_existing_table(connection)

    connection.executescript(
        f"""
        BEGIN IMMEDIATE;

        CREATE TABLE IF NOT EXISTS chat_preferences (
            chat_id BLOB(16) PRIMARY KEY CHECK(length(chat_id) = 16),
            pinned_at_us INTEGER NULL CHECK(
                pinned_at_us IS NULL OR pinned_at_us >= 0
            ),
            favorited_at_us INTEGER NULL CHECK(
                favorited_at_us IS NULL OR favorited_at_us >= 0
            ),
            updated_at_us INTEGER NOT NULL CHECK(updated_at_us >= 0),
            CHECK(pinned_at_us IS NOT NULL OR favorited_at_us IS NOT NULL),
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
        ) WITHOUT ROWID;

        CREATE INDEX IF NOT EXISTS idx_chat_preferences_pinned
            ON chat_preferences(pinned_at_us DESC, chat_id)
            WHERE pinned_at_us IS NOT NULL;

        CREATE INDEX IF NOT EXISTS idx_chat_preferences_favorited
            ON chat_preferences(favorited_at_us DESC, chat_id)
            WHERE favorited_at_us IS NOT NULL;

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
    """Fail closed if v43 preference metadata or schema identity drifted."""
    user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if user_version != schema_contract.CHAT_PREFERENCES_SCHEMA_VERSION:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences schema version verification failed."
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
            "ATHENA chat-preferences schema_metadata verification failed."
        )

    if _TABLE not in set(schema_contract._user_tables(connection)):
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences table is missing."
        )

    columns = tuple(
        str(row[1])
        for row in connection.execute(
            "PRAGMA table_info(chat_preferences)"
        ).fetchall()
    )
    if columns != _COLUMNS:
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences schema is incomplete."
        )

    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise schema_contract.DatabaseCompatibilityError(
            "ATHENA chat-preferences foreign-key verification failed."
        )
