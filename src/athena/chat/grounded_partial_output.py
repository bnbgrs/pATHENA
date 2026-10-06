"""Durable raw provider-stream checkpoints for interrupted Grounded chat."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PARTIAL_OUTPUT_EXTENSION_VERSION = 1

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_partial_output_chunks (
    operation_id BLOB(16) NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    attempt_no INTEGER NOT NULL CHECK(attempt_no >= 0),
    chunk_no INTEGER NOT NULL CHECK(chunk_no >= 0),
    content TEXT NOT NULL CHECK(length(content) > 0),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    PRIMARY KEY(operation_id, attempt_no, chunk_no),
    FOREIGN KEY(operation_id)
        REFERENCES grounded_provider_attempts(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


@dataclass(frozen=True, slots=True)
class GroundedPartialOutput:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    attempt_no: int
    content: str
    chunk_count: int


class GroundedPartialOutputError(RuntimeError):
    """Persisted provider-stream checkpoint is inconsistent."""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


class GroundedPartialOutputRepository:
    """Append provider deltas after the durable provider-attempt boundary."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_CREATE_SQL)
        schema = self.database.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("grounded_partial_output_chunks",),
        ).fetchone()
        if (
            schema is None
            or schema["sql"] is None
            or _normalized_schema_sql(str(schema["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
        ):
            raise GroundedPartialOutputError(
                "grounded_partial_output_chunks has an incompatible definition."
            )

    def append(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        attempt_no: int,
        content: str,
    ) -> None:
        if isinstance(attempt_no, bool) or not isinstance(attempt_no, int) or attempt_no < 0:
            raise ValueError("Grounded partial-output attempt_no must be non-negative.")
        if not isinstance(content, str) or not content:
            raise ValueError("Grounded partial-output chunk must be non-empty text.")

        operation_blob = uuid_to_blob(operation_id)
        chat_blob = uuid_to_blob(chat_id)
        with self.database.write_transaction() as connection:
            attempt = connection.execute(
                """
                SELECT a.chat_id, o.chat_id AS operation_chat_id, o.mode
                FROM grounded_provider_attempts AS a
                JOIN chat_send_operations AS o
                  ON o.operation_id = a.operation_id
                WHERE a.operation_id = ?
                """,
                (operation_blob,),
            ).fetchone()
            if (
                attempt is None
                or bytes(attempt["chat_id"]) != chat_blob
                or bytes(attempt["operation_chat_id"]) != chat_blob
                or str(attempt["mode"]) != "grounded"
            ):
                raise GroundedPartialOutputError(
                    "Partial output requires the matching durable Grounded provider attempt."
                )

            next_row = connection.execute(
                """
                SELECT COALESCE(MAX(chunk_no) + 1, 0) AS next_chunk_no
                FROM grounded_partial_output_chunks
                WHERE operation_id = ? AND attempt_no = ?
                """,
                (operation_blob, attempt_no),
            ).fetchone()
            if next_row is None:
                raise GroundedPartialOutputError(
                    "Could not allocate the next partial-output chunk identity."
                )
            connection.execute(
                """
                INSERT INTO grounded_partial_output_chunks (
                    operation_id,
                    chat_id,
                    attempt_no,
                    chunk_no,
                    content,
                    created_at_us,
                    extension_schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operation_blob,
                    chat_blob,
                    attempt_no,
                    int(next_row["next_chunk_no"]),
                    content,
                    utc_now_us(),
                    GROUNDED_PARTIAL_OUTPUT_EXTENSION_VERSION,
                ),
            )

    def load_latest(
        self,
        operation_id: uuid.UUID,
    ) -> GroundedPartialOutput | None:
        operation_blob = uuid_to_blob(operation_id)
        latest = self.database.connection.execute(
            """
            SELECT MAX(attempt_no) AS attempt_no
            FROM grounded_partial_output_chunks
            WHERE operation_id = ?
            """,
            (operation_blob,),
        ).fetchone()
        if latest is None or latest["attempt_no"] is None:
            return None
        attempt_no = int(latest["attempt_no"])
        rows = self.database.connection.execute(
            """
            SELECT chat_id, chunk_no, content
            FROM grounded_partial_output_chunks
            WHERE operation_id = ? AND attempt_no = ?
            ORDER BY chunk_no ASC
            """,
            (operation_blob, attempt_no),
        ).fetchall()
        if not rows:
            return None
        chat_id = uuid_from_blob(bytes(rows[0]["chat_id"]))
        expected_chunk = 0
        parts: list[str] = []
        for row in rows:
            if uuid_from_blob(bytes(row["chat_id"])) != chat_id:
                raise GroundedPartialOutputError(
                    "Partial-output chunks disagree on chat identity."
                )
            if int(row["chunk_no"]) != expected_chunk:
                raise GroundedPartialOutputError(
                    "Partial-output chunk sequence is not contiguous."
                )
            parts.append(str(row["content"]))
            expected_chunk += 1
        return GroundedPartialOutput(
            operation_id=operation_id,
            chat_id=chat_id,
            attempt_no=attempt_no,
            content="".join(parts),
            chunk_count=len(parts),
        )
