"""Durable provider-call boundary and result journal for Grounded sends."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import cast

from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PROVIDER_ATTEMPT_EXTENSION_VERSION = 1
GROUNDED_PROVIDER_RESULT_EXTENSION_VERSION = 1


class GroundedProviderAttemptConflictError(RuntimeError):
    """The provider boundary conflicts with existing durable operation state."""


class GroundedProviderAttemptSchemaError(RuntimeError):
    """A provider-boundary extension table is missing or incompatible."""


@dataclass(frozen=True, slots=True)
class GroundedProviderAttempt:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    started_at_us: int


@dataclass(frozen=True, slots=True)
class GroundedProviderResult:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    processing_run_id: uuid.UUID
    assistant_content: str
    receipt_payload_json: str
    receipt_payload_sha256: str
    created_at_us: int


_ATTEMPT_COLUMNS = (
    "operation_id",
    "chat_id",
    "extension_schema_version",
    "started_at_us",
)
_RESULT_COLUMNS = (
    "operation_id",
    "chat_id",
    "processing_run_id",
    "assistant_content",
    "receipt_payload_json",
    "receipt_payload_sha256",
    "extension_schema_version",
    "created_at_us",
)

_ATTEMPT_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_provider_attempts (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    started_at_us INTEGER NOT NULL CHECK(started_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""

_RESULT_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_provider_results (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    processing_run_id BLOB(16) NOT NULL CHECK(length(processing_run_id) = 16),
    assistant_content TEXT NOT NULL CHECK(length(trim(assistant_content)) > 0),
    receipt_payload_json TEXT NOT NULL CHECK(length(receipt_payload_json) > 1),
    receipt_payload_sha256 TEXT NOT NULL CHECK(length(receipt_payload_sha256) = 64),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES grounded_provider_attempts(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _canonical_receipt_payload(payload_json: str) -> tuple[str, str, str]:
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Provider result receipt payload must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Provider result receipt payload must be a JSON object.")
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assistant_text = payload.get("assistant_text")
    if not isinstance(assistant_text, str) or not assistant_text.strip():
        raise ValueError(
            "Provider result receipt payload requires non-empty assistant_text."
        )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return canonical, digest, assistant_text


class GroundedProviderAttemptRepository:
    """Persist the irreversible provider boundary and returned result durably."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        ChatSendOperationRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_ATTEMPT_CREATE_SQL)
            connection.execute(_RESULT_CREATE_SQL)
        self._verify_table(
            "grounded_provider_attempts",
            _ATTEMPT_CREATE_SQL,
            _ATTEMPT_COLUMNS,
        )
        self._verify_table(
            "grounded_provider_results",
            _RESULT_CREATE_SQL,
            _RESULT_COLUMNS,
        )

    def _verify_table(
        self,
        table: str,
        expected_sql: str,
        expected_columns: tuple[str, ...],
    ) -> None:
        connection = self.database.connection
        schema = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        if (
            schema is None
            or schema["sql"] is None
            or _normalized_schema_sql(str(schema["sql"]))
            != _normalized_schema_sql(expected_sql)
        ):
            raise GroundedProviderAttemptSchemaError(
                f"{table} has an incompatible extension definition."
            )
        columns = connection.execute(f"PRAGMA table_info({table})").fetchall()
        if tuple(str(row["name"]) for row in columns) != expected_columns:
            raise GroundedProviderAttemptSchemaError(
                f"{table} has an incompatible extension layout."
            )

    def load(self, operation_id: uuid.UUID) -> GroundedProviderAttempt | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, started_at_us
            FROM grounded_provider_attempts
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        return GroundedProviderAttempt(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            started_at_us=int(row["started_at_us"]),
        )

    def load_result(self, operation_id: uuid.UUID) -> GroundedProviderResult | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, processing_run_id,
                   assistant_content, receipt_payload_json,
                   receipt_payload_sha256, created_at_us
            FROM grounded_provider_results
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        return None if row is None else self._result_from_row(row)

    def mark_started(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> GroundedProviderAttempt:
        with self.database.write_transaction() as connection:
            operation = self._require_grounded_operation(connection, operation_id, chat_id)
            existing = connection.execute(
                """
                SELECT operation_id, chat_id, started_at_us
                FROM grounded_provider_attempts WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                attempt = GroundedProviderAttempt(
                    operation_id=uuid_from_blob(bytes(existing["operation_id"])),
                    chat_id=uuid_from_blob(bytes(existing["chat_id"])),
                    started_at_us=int(existing["started_at_us"]),
                )
                if attempt.chat_id != chat_id:
                    raise GroundedProviderAttemptConflictError(
                        "Provider attempt marker belongs to another chat."
                    )
                return attempt
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt may start only from user_committed state."
                )
            started_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_provider_attempts (
                    operation_id, chat_id, extension_schema_version, started_at_us
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    GROUNDED_PROVIDER_ATTEMPT_EXTENSION_VERSION,
                    started_at_us,
                ),
            )
        stored = self.load(operation_id)
        if stored is None:
            raise RuntimeError("Provider attempt marker disappeared after commit.")
        return stored

    def store_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        assistant_content: str,
        receipt_payload_json: str,
    ) -> GroundedProviderResult:
        if not assistant_content.strip():
            raise ValueError("Provider result assistant content must not be blank.")
        canonical, digest, receipt_assistant_text = _canonical_receipt_payload(
            receipt_payload_json
        )
        if receipt_assistant_text != assistant_content:
            raise ValueError(
                "Provider result receipt assistant_text must match assistant content exactly."
            )
        with self.database.write_transaction() as connection:
            operation = self._require_grounded_operation(connection, operation_id, chat_id)
            attempt = connection.execute(
                "SELECT chat_id FROM grounded_provider_attempts WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if attempt is None or uuid_from_blob(bytes(attempt["chat_id"])) != chat_id:
                raise GroundedProviderAttemptConflictError(
                    "Provider result requires the matching durable attempt marker."
                )
            existing = connection.execute(
                """
                SELECT operation_id, chat_id, processing_run_id,
                       assistant_content, receipt_payload_json,
                       receipt_payload_sha256, created_at_us
                FROM grounded_provider_results WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                result = self._result_from_row(existing)
                if (
                    result.chat_id == chat_id
                    and result.processing_run_id == processing_run_id
                    and result.assistant_content == assistant_content
                    and result.receipt_payload_json == canonical
                    and result.receipt_payload_sha256 == digest
                ):
                    return result
                raise GroundedProviderAttemptConflictError(
                    "Provider result conflicts with the already recorded result."
                )
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise GroundedProviderAttemptConflictError(
                    "A new provider result may be recorded only before assistant commit."
                )
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_provider_results (
                    operation_id, chat_id, processing_run_id,
                    assistant_content, receipt_payload_json,
                    receipt_payload_sha256, extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    uuid_to_blob(processing_run_id),
                    assistant_content,
                    canonical,
                    digest,
                    GROUNDED_PROVIDER_RESULT_EXTENSION_VERSION,
                    created_at_us,
                ),
            )
        stored = self.load_result(operation_id)
        if stored is None:
            raise RuntimeError("Provider result disappeared after commit.")
        return stored

    @staticmethod
    def _require_grounded_operation(
        connection: sqlite3.Connection,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> sqlite3.Row:
        operation = connection.execute(
            "SELECT chat_id, mode, state FROM chat_send_operations WHERE operation_id = ?",
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if operation is None:
            raise GroundedProviderAttemptConflictError(
                "Provider boundary requires an existing send operation."
            )
        if uuid_from_blob(bytes(operation["chat_id"])) != chat_id:
            raise GroundedProviderAttemptConflictError(
                "Provider boundary chat identity conflicts with send operation."
            )
        if str(operation["mode"]) != "grounded":
            raise GroundedProviderAttemptConflictError(
                "Provider boundary marker is Grounded-only."
            )
        return cast(sqlite3.Row, operation)

    @staticmethod
    def _result_from_row(row: sqlite3.Row) -> GroundedProviderResult:
        result = GroundedProviderResult(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            processing_run_id=uuid_from_blob(bytes(row["processing_run_id"])),
            assistant_content=str(row["assistant_content"]),
            receipt_payload_json=str(row["receipt_payload_json"]),
            receipt_payload_sha256=str(row["receipt_payload_sha256"]),
            created_at_us=int(row["created_at_us"]),
        )
        canonical, digest, receipt_assistant_text = _canonical_receipt_payload(
            result.receipt_payload_json
        )
        if (
            canonical != result.receipt_payload_json
            or digest != result.receipt_payload_sha256
            or receipt_assistant_text != result.assistant_content
        ):
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider result failed checksum verification."
            )
        return result
