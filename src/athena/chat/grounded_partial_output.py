"""Durable raw provider-stream checkpoints for interrupted Grounded chat."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PARTIAL_OUTPUT_EXTENSION_VERSION = 1
GROUNDED_PARTIAL_CONTINUATION_EXTENSION_VERSION = 1
CONTINUATION_STRATEGY_ID = "persisted-prefix-suffix-v1"

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

_CREATE_CONTINUATION_SQL = """
CREATE TABLE IF NOT EXISTS grounded_partial_continuations (
    operation_id BLOB(16) NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    attempt_no INTEGER NOT NULL CHECK(attempt_no >= 1),
    processing_run_id BLOB(16) NOT NULL CHECK(length(processing_run_id) = 16),
    context_package_request_id BLOB(16) NOT NULL CHECK(length(context_package_request_id) = 16),
    prefix_content_sha256 TEXT NOT NULL CHECK(length(prefix_content_sha256) = 64),
    prefix_length INTEGER NOT NULL CHECK(prefix_length > 0),
    strategy_id TEXT NOT NULL CHECK(length(strategy_id) > 0),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    PRIMARY KEY(operation_id, attempt_no),
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


@dataclass(frozen=True, slots=True)
class GroundedPartialContinuation:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    attempt_no: int
    processing_run_id: uuid.UUID
    context_package_request_id: uuid.UUID
    prefix_content_sha256: str
    prefix_length: int
    strategy_id: str
    created_at_us: int


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
            connection.execute(_CREATE_CONTINUATION_SQL)
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
        continuation_schema = self.database.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("grounded_partial_continuations",),
        ).fetchone()
        if (
            continuation_schema is None
            or continuation_schema["sql"] is None
            or _normalized_schema_sql(str(continuation_schema["sql"]))
            != _normalized_schema_sql(_CREATE_CONTINUATION_SQL)
        ):
            raise GroundedPartialOutputError(
                "grounded_partial_continuations has an incompatible definition."
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
            if attempt_no > 0:
                continuation = connection.execute(
                    """
                    SELECT chat_id
                    FROM grounded_partial_continuations
                    WHERE operation_id = ? AND attempt_no = ?
                    """,
                    (operation_blob, attempt_no),
                ).fetchone()
                if (
                    continuation is None
                    or bytes(continuation["chat_id"]) != chat_blob
                ):
                    raise GroundedPartialOutputError(
                        "Continuation partial output requires a durable continuation claim."
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


    def load_cumulative(
        self,
        operation_id: uuid.UUID,
    ) -> GroundedPartialOutput | None:
        operation_blob = uuid_to_blob(operation_id)
        rows = self.database.connection.execute(
            """
            SELECT chat_id, attempt_no, chunk_no, content
            FROM grounded_partial_output_chunks
            WHERE operation_id = ?
            ORDER BY attempt_no ASC, chunk_no ASC
            """,
            (operation_blob,),
        ).fetchall()
        if not rows:
            return None

        chat_id = uuid_from_blob(bytes(rows[0]["chat_id"]))
        current_attempt = -1
        expected_chunk = 0
        parts: list[str] = []
        chunk_count = 0
        for row in rows:
            if uuid_from_blob(bytes(row["chat_id"])) != chat_id:
                raise GroundedPartialOutputError(
                    "Partial-output chunks disagree on chat identity."
                )
            attempt_no = int(row["attempt_no"])
            chunk_no = int(row["chunk_no"])
            if attempt_no != current_attempt:
                if attempt_no != current_attempt + 1:
                    raise GroundedPartialOutputError(
                        "Partial-output attempts are not contiguous."
                    )
                current_attempt = attempt_no
                expected_chunk = 0
            if chunk_no != expected_chunk:
                raise GroundedPartialOutputError(
                    "Partial-output chunk sequence is not contiguous."
                )
            parts.append(str(row["content"]))
            chunk_count += 1
            expected_chunk += 1

        return GroundedPartialOutput(
            operation_id=operation_id,
            chat_id=chat_id,
            attempt_no=current_attempt,
            content="".join(parts),
            chunk_count=chunk_count,
        )

    def load_through_attempt(
        self,
        operation_id: uuid.UUID,
        *,
        max_attempt_no: int,
    ) -> GroundedPartialOutput | None:
        if (
            isinstance(max_attempt_no, bool)
            or not isinstance(max_attempt_no, int)
            or max_attempt_no < 0
        ):
            raise ValueError(
                "Grounded partial-output max_attempt_no must be non-negative."
            )
        operation_blob = uuid_to_blob(operation_id)
        rows = self.database.connection.execute(
            """
            SELECT chat_id, attempt_no, chunk_no, content
            FROM grounded_partial_output_chunks
            WHERE operation_id = ? AND attempt_no <= ?
            ORDER BY attempt_no ASC, chunk_no ASC
            """,
            (operation_blob, max_attempt_no),
        ).fetchall()
        if not rows:
            return None
        chat_id = uuid_from_blob(bytes(rows[0]["chat_id"]))
        current_attempt = -1
        expected_chunk = 0
        parts: list[str] = []
        chunk_count = 0
        for row in rows:
            if uuid_from_blob(bytes(row["chat_id"])) != chat_id:
                raise GroundedPartialOutputError(
                    "Partial-output chunks disagree on chat identity."
                )
            attempt_no = int(row["attempt_no"])
            if attempt_no != current_attempt:
                if attempt_no != current_attempt + 1:
                    raise GroundedPartialOutputError(
                        "Partial-output attempts are not contiguous."
                    )
                current_attempt = attempt_no
                expected_chunk = 0
            if int(row["chunk_no"]) != expected_chunk:
                raise GroundedPartialOutputError(
                    "Partial-output chunk sequence is not contiguous."
                )
            parts.append(str(row["content"]))
            chunk_count += 1
            expected_chunk += 1
        if current_attempt > max_attempt_no:
            raise GroundedPartialOutputError(
                "Partial-output attempt exceeded requested reconstruction bound."
            )
        return GroundedPartialOutput(
            operation_id=operation_id,
            chat_id=chat_id,
            attempt_no=current_attempt,
            content="".join(parts),
            chunk_count=chunk_count,
        )

    def claim_continuation(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        context_package_request_id: uuid.UUID,
        expected_prefix: str,
    ) -> GroundedPartialContinuation:
        if not isinstance(expected_prefix, str) or not expected_prefix:
            raise ValueError("Grounded continuation prefix must be non-empty text.")
        cumulative = self.load_cumulative(operation_id)
        if (
            cumulative is None
            or cumulative.chat_id != chat_id
            or cumulative.content != expected_prefix
        ):
            raise GroundedPartialOutputError(
                "Grounded continuation prefix conflicts with durable partial output."
            )
        prefix_hash = hashlib.sha256(expected_prefix.encode("utf-8")).hexdigest()
        operation_blob = uuid_to_blob(operation_id)
        chat_blob = uuid_to_blob(chat_id)
        with self.database.write_transaction() as connection:
            latest_claim = connection.execute(
                """
                SELECT MAX(attempt_no) AS attempt_no
                FROM grounded_partial_continuations
                WHERE operation_id = ?
                """,
                (operation_blob,),
            ).fetchone()
            claimed_attempt = (
                None
                if latest_claim is None or latest_claim["attempt_no"] is None
                else int(latest_claim["attempt_no"])
            )
            if claimed_attempt is not None and claimed_attempt > cumulative.attempt_no:
                raise GroundedPartialOutputError(
                    "A Grounded continuation is already ambiguous before its first checkpoint."
                )
            next_attempt = cumulative.attempt_no + 1
            if claimed_attempt is not None and claimed_attempt >= next_attempt:
                raise GroundedPartialOutputError(
                    "Grounded continuation attempt identity is not monotonic."
                )
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_partial_continuations (
                    operation_id,
                    chat_id,
                    attempt_no,
                    processing_run_id,
                    context_package_request_id,
                    prefix_content_sha256,
                    prefix_length,
                    strategy_id,
                    created_at_us,
                    extension_schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    operation_blob,
                    chat_blob,
                    next_attempt,
                    uuid_to_blob(processing_run_id),
                    uuid_to_blob(context_package_request_id),
                    prefix_hash,
                    len(expected_prefix),
                    CONTINUATION_STRATEGY_ID,
                    created_at_us,
                    GROUNDED_PARTIAL_CONTINUATION_EXTENSION_VERSION,
                ),
            )
        return GroundedPartialContinuation(
            operation_id=operation_id,
            chat_id=chat_id,
            attempt_no=next_attempt,
            processing_run_id=processing_run_id,
            context_package_request_id=context_package_request_id,
            prefix_content_sha256=prefix_hash,
            prefix_length=len(expected_prefix),
            strategy_id=CONTINUATION_STRATEGY_ID,
            created_at_us=created_at_us,
        )

    def load_latest_continuation(
        self,
        operation_id: uuid.UUID,
    ) -> GroundedPartialContinuation | None:
        row = self.database.connection.execute(
            """
            SELECT chat_id, attempt_no, processing_run_id,
                   context_package_request_id, prefix_content_sha256,
                   prefix_length, strategy_id, created_at_us
            FROM grounded_partial_continuations
            WHERE operation_id = ?
            ORDER BY attempt_no DESC
            LIMIT 1
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        return GroundedPartialContinuation(
            operation_id=operation_id,
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            attempt_no=int(row["attempt_no"]),
            processing_run_id=uuid_from_blob(bytes(row["processing_run_id"])),
            context_package_request_id=uuid_from_blob(
                bytes(row["context_package_request_id"])
            ),
            prefix_content_sha256=str(row["prefix_content_sha256"]),
            prefix_length=int(row["prefix_length"]),
            strategy_id=str(row["strategy_id"]),
            created_at_us=int(row["created_at_us"]),
        )
