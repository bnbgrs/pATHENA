"""Durable, explicitly non-canonical journal for interrupted Grounded output."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptRepository,
)
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PARTIAL_OUTPUT_EXTENSION_VERSION = 1


class GroundedPartialOutputError(RuntimeError):
    """A partial-output journal cannot be read or extended safely."""


@dataclass(frozen=True, slots=True)
class GroundedPartialOutput:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    content: str
    delta_count: int
    updated_at_us: int


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_partial_outputs (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    content TEXT NOT NULL CHECK(length(content) > 0),
    delta_count INTEGER NOT NULL CHECK(delta_count > 0),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    updated_at_us INTEGER NOT NULL CHECK(updated_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES grounded_provider_attempts(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""
_COLUMNS = (
    "operation_id",
    "chat_id",
    "content",
    "delta_count",
    "extension_schema_version",
    "updated_at_us",
)


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


class GroundedPartialOutputRepository:
    """Journal raw provider deltas without presenting them as a completed answer.

    Entries are recovery evidence only. They are never canonical ChatMessages and
    must never bypass grounding validation or provider-result finalization.
    """

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        GroundedProviderAttemptRepository(database)
        with database.write_transaction() as connection:
            connection.execute(_CREATE_SQL)
        schema = database.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("grounded_partial_outputs",),
        ).fetchone()
        columns = database.connection.execute(
            "PRAGMA table_info(grounded_partial_outputs)"
        ).fetchall()
        if (
            schema is None
            or schema["sql"] is None
            or _normalized_schema_sql(str(schema["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
            or tuple(str(row["name"]) for row in columns) != _COLUMNS
        ):
            raise GroundedPartialOutputError(
                "grounded_partial_outputs has an incompatible extension definition."
            )

    def load(self, operation_id: uuid.UUID) -> GroundedPartialOutput | None:
        row = self.database.connection.execute(
            """
            SELECT p.operation_id, p.chat_id, p.content, p.delta_count, p.updated_at_us,
                   a.chat_id AS attempt_chat_id
            FROM grounded_partial_outputs AS p
            LEFT JOIN grounded_provider_attempts AS a
              ON a.operation_id = p.operation_id
            WHERE p.operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        if (
            row["attempt_chat_id"] is None
            or bytes(row["chat_id"]) != bytes(row["attempt_chat_id"])
        ):
            raise GroundedPartialOutputError(
                "Partial provider output no longer matches its durable attempt."
            )
        return GroundedPartialOutput(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            content=str(row["content"]),
            delta_count=int(row["delta_count"]),
            updated_at_us=int(row["updated_at_us"]),
        )

    def append_delta(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        delta: str,
    ) -> GroundedPartialOutput:
        if not isinstance(delta, str):
            raise TypeError("Grounded partial output delta must be text.")
        if not delta:
            raise ValueError("Grounded partial output delta must not be empty.")
        now_us = utc_now_us()
        with self.database.write_transaction() as connection:
            attempt = connection.execute(
                """
                SELECT chat_id
                FROM grounded_provider_attempts
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if (
                attempt is None
                or uuid_from_blob(bytes(attempt["chat_id"])) != chat_id
            ):
                raise GroundedPartialOutputError(
                    "Partial output requires its matching durable provider attempt."
                )
            completed = connection.execute(
                """
                SELECT 1
                FROM grounded_provider_results
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if completed is not None:
                raise GroundedPartialOutputError(
                    "Completed provider output cannot accept more partial deltas."
                )
            connection.execute(
                """
                INSERT INTO grounded_partial_outputs (
                    operation_id,
                    chat_id,
                    content,
                    delta_count,
                    extension_schema_version,
                    updated_at_us
                ) VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(operation_id) DO UPDATE SET
                    content = grounded_partial_outputs.content || excluded.content,
                    delta_count = grounded_partial_outputs.delta_count + 1,
                    updated_at_us = excluded.updated_at_us
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    delta,
                    GROUNDED_PARTIAL_OUTPUT_EXTENSION_VERSION,
                    now_us,
                ),
            )
        stored = self.load(operation_id)
        if stored is None:
            raise GroundedPartialOutputError(
                "Partial provider output disappeared after commit."
            )
        return stored
