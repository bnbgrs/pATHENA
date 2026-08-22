"""Durable request identity and lifecycle for chat send operations.

This module intentionally owns its SQLite extension table instead of advancing
ATHENA's global schema version.  The extension is created transactionally on
first repository construction and verified fail-closed before use.  This keeps
chat crash-safety independent from unrelated historical migration fixtures.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from enum import Enum

from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

CHAT_SEND_OPERATION_EXTENSION_VERSION = 1


class ChatSendOperationMode(str, Enum):
    DIRECT = "direct"
    GROUNDED = "grounded"


class ChatSendOperationState(str, Enum):
    USER_COMMITTED = "user_committed"
    ASSISTANT_COMMITTED = "assistant_committed"
    RECEIPT_COMMITTED = "receipt_committed"
    COMPLETE = "complete"


class ChatSendOperationMatch(str, Enum):
    ABSENT = "absent"
    MATCH = "match"
    CONFLICT = "conflict"


class ChatSendOperationConflictError(RuntimeError):
    """The same operation id was reused with different durable identity."""


class ChatSendOperationNotFoundError(LookupError):
    """The requested durable operation does not exist."""


class ChatSendOperationSchemaError(RuntimeError):
    """The subsystem-owned send-operation schema is missing or incompatible."""


@dataclass(frozen=True, slots=True)
class ChatSendOperation:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    mode: ChatSendOperationMode
    request_fingerprint_payload_json: str
    request_fingerprint_sha256: str
    request_fingerprint_format_version: int
    state: ChatSendOperationState
    processing_run_id: uuid.UUID | None
    receipt_payload_sha256: str | None
    created_at_us: int
    updated_at_us: int


_STATE_RANK = {
    ChatSendOperationState.USER_COMMITTED: 1,
    ChatSendOperationState.ASSISTANT_COMMITTED: 2,
    ChatSendOperationState.RECEIPT_COMMITTED: 3,
    ChatSendOperationState.COMPLETE: 4,
}

_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "mode",
    "request_fingerprint_payload_json",
    "request_fingerprint_sha256",
    "request_fingerprint_format_version",
    "extension_schema_version",
    "state",
    "processing_run_id",
    "receipt_payload_sha256",
    "created_at_us",
    "updated_at_us",
)

_CREATE_SQL = """
CREATE TABLE chat_send_operations (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    mode TEXT NOT NULL CHECK(mode IN ('direct', 'grounded')),
    request_fingerprint_payload_json TEXT NOT NULL
        CHECK(length(request_fingerprint_payload_json) > 1),
    request_fingerprint_sha256 TEXT NOT NULL
        CHECK(length(request_fingerprint_sha256) = 64),
    request_fingerprint_format_version INTEGER NOT NULL
        CHECK(request_fingerprint_format_version >= 1),
    extension_schema_version INTEGER NOT NULL
        CHECK(extension_schema_version = 1),
    state TEXT NOT NULL
        CHECK(state IN ('user_committed', 'assistant_committed', 'receipt_committed', 'complete')),
    processing_run_id BLOB(16) NULL
        CHECK(processing_run_id IS NULL OR length(processing_run_id) = 16),
    receipt_payload_sha256 TEXT NULL
        CHECK(receipt_payload_sha256 IS NULL OR length(receipt_payload_sha256) = 64),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    updated_at_us INTEGER NOT NULL CHECK(updated_at_us >= created_at_us),
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


class ChatSendOperationRepository:
    """Transactional persistence for retry/reconciliation identity."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self._ensure_extension_schema()

    def _ensure_extension_schema(self) -> None:
        connection = self.database.connection
        row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'chat_send_operations'"
        ).fetchone()
        if row is None:
            with self.database.write_transaction() as transaction:
                transaction.execute(_CREATE_SQL)
        self._verify_extension_schema()

    def _verify_extension_schema(self) -> None:
        connection = self.database.connection
        rows = connection.execute("PRAGMA table_info(chat_send_operations)").fetchall()
        actual = tuple(str(row["name"]) for row in rows)
        if actual != _REQUIRED_COLUMNS:
            raise ChatSendOperationSchemaError(
                "chat_send_operations has an incompatible schema extension layout."
            )

        foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(chat_send_operations)"
        ).fetchall()
        if not any(
            str(row["table"]) == "chats"
            and str(row["from"]) == "chat_id"
            and str(row["on_delete"]).upper() == "CASCADE"
            for row in foreign_keys
        ):
            raise ChatSendOperationSchemaError(
                "chat_send_operations must cascade from chats(chat_id)."
            )

    def load(self, operation_id: uuid.UUID) -> ChatSendOperation | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, mode,
                   request_fingerprint_payload_json,
                   request_fingerprint_sha256,
                   request_fingerprint_format_version,
                   state, processing_run_id, receipt_payload_sha256,
                   created_at_us, updated_at_us
            FROM chat_send_operations
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        return None if row is None else self._from_row(row)

    def match_request(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        mode: ChatSendOperationMode,
        fingerprint: ChatRequestFingerprint,
    ) -> ChatSendOperationMatch:
        self._validate_fingerprint(fingerprint)
        existing = self.load(operation_id)
        if existing is None:
            return ChatSendOperationMatch.ABSENT
        if self._identity_matches(existing, chat_id, mode, fingerprint):
            return ChatSendOperationMatch.MATCH
        return ChatSendOperationMatch.CONFLICT

    def store_user_committed(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        mode: ChatSendOperationMode,
        fingerprint: ChatRequestFingerprint,
    ) -> ChatSendOperation:
        self._validate_fingerprint(fingerprint)
        with self.database.write_transaction() as connection:
            existing = self._load_in_transaction(connection, operation_id)
            if existing is not None:
                if not self._identity_matches(existing, chat_id, mode, fingerprint):
                    raise ChatSendOperationConflictError(
                        "Chat send operation identity conflict."
                    )
                return existing

            now = utc_now_us()
            connection.execute(
                """
                INSERT INTO chat_send_operations (
                    operation_id, chat_id, mode,
                    request_fingerprint_payload_json,
                    request_fingerprint_sha256,
                    request_fingerprint_format_version,
                    extension_schema_version,
                    state, processing_run_id, receipt_payload_sha256,
                    created_at_us, updated_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'user_committed', NULL, NULL, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    mode.value,
                    fingerprint.payload_json,
                    fingerprint.payload_sha256,
                    fingerprint.format_version,
                    CHAT_SEND_OPERATION_EXTENSION_VERSION,
                    now,
                    now,
                ),
            )
        operation = self.load(operation_id)
        if operation is None:
            raise RuntimeError("Stored chat send operation disappeared after commit.")
        return operation

    def advance(
        self,
        operation_id: uuid.UUID,
        state: ChatSendOperationState,
        *,
        processing_run_id: uuid.UUID | None = None,
        receipt_payload_sha256: str | None = None,
    ) -> ChatSendOperation:
        with self.database.write_transaction() as connection:
            existing = self._load_in_transaction(connection, operation_id)
            if existing is None:
                raise ChatSendOperationNotFoundError(str(operation_id))
            if _STATE_RANK[state] < _STATE_RANK[existing.state]:
                raise ChatSendOperationConflictError(
                    "Chat send operation lifecycle cannot move backwards."
                )

            run_id = self._merge_run_id(existing.processing_run_id, processing_run_id)
            receipt_sha = self._merge_receipt_sha(
                existing.receipt_payload_sha256,
                receipt_payload_sha256,
            )
            self._validate_target(existing.mode, state, run_id, receipt_sha)

            now = max(utc_now_us(), existing.updated_at_us)
            connection.execute(
                """
                UPDATE chat_send_operations
                SET state = ?, processing_run_id = ?,
                    receipt_payload_sha256 = ?, updated_at_us = ?
                WHERE operation_id = ?
                """,
                (
                    state.value,
                    uuid_to_blob(run_id) if run_id is not None else None,
                    receipt_sha,
                    now,
                    uuid_to_blob(operation_id),
                ),
            )
        operation = self.load(operation_id)
        if operation is None:
            raise RuntimeError("Advanced chat send operation disappeared after commit.")
        return operation

    def _load_in_transaction(
        self,
        connection: sqlite3.Connection,
        operation_id: uuid.UUID,
    ) -> ChatSendOperation | None:
        row = connection.execute(
            """
            SELECT operation_id, chat_id, mode,
                   request_fingerprint_payload_json,
                   request_fingerprint_sha256,
                   request_fingerprint_format_version,
                   state, processing_run_id, receipt_payload_sha256,
                   created_at_us, updated_at_us
            FROM chat_send_operations WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        return None if row is None else self._from_row(row)

    @staticmethod
    def _validate_fingerprint(fingerprint: ChatRequestFingerprint) -> None:
        if fingerprint.format_version < 1 or len(fingerprint.payload_json) <= 1:
            raise ValueError("Invalid chat request fingerprint.")
        try:
            parsed = json.loads(fingerprint.payload_json)
        except json.JSONDecodeError as exc:
            raise ValueError("Chat request fingerprint payload must be valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Chat request fingerprint payload must be a JSON object.")
        expected = hashlib.sha256(fingerprint.payload_json.encode("utf-8")).hexdigest()
        if fingerprint.payload_sha256 != expected:
            raise ValueError("Chat request fingerprint SHA-256 does not match its payload.")

    @staticmethod
    def _identity_matches(
        existing: ChatSendOperation,
        chat_id: uuid.UUID,
        mode: ChatSendOperationMode,
        fingerprint: ChatRequestFingerprint,
    ) -> bool:
        return (
            existing.chat_id == chat_id
            and existing.mode is mode
            and existing.request_fingerprint_payload_json == fingerprint.payload_json
            and existing.request_fingerprint_sha256 == fingerprint.payload_sha256
            and existing.request_fingerprint_format_version == fingerprint.format_version
        )

    @staticmethod
    def _merge_run_id(
        existing: uuid.UUID | None,
        incoming: uuid.UUID | None,
    ) -> uuid.UUID | None:
        if existing is not None and incoming is not None and existing != incoming:
            raise ChatSendOperationConflictError(
                "Chat send operation processing-run identity conflict."
            )
        return existing if existing is not None else incoming

    @staticmethod
    def _merge_receipt_sha(existing: str | None, incoming: str | None) -> str | None:
        if incoming is not None and (
            len(incoming) != 64
            or any(
                character not in "0123456789abcdef"
                for character in incoming
            )
        ):
            raise ValueError("Receipt SHA-256 must be lowercase hexadecimal.")
        if existing is not None and incoming is not None and existing != incoming:
            raise ChatSendOperationConflictError(
                "Chat send operation receipt identity conflict."
            )
        return existing if existing is not None else incoming

    @staticmethod
    def _validate_target(
        mode: ChatSendOperationMode,
        state: ChatSendOperationState,
        run_id: uuid.UUID | None,
        receipt_sha: str | None,
    ) -> None:
        if mode is ChatSendOperationMode.DIRECT:
            if state is ChatSendOperationState.RECEIPT_COMMITTED or receipt_sha is not None:
                raise ValueError("Direct chat operations cannot bind a Grounded receipt.")
            return
        if state in {ChatSendOperationState.RECEIPT_COMMITTED, ChatSendOperationState.COMPLETE}:
            if run_id is None or receipt_sha is None:
                raise ValueError(
                    "Grounded receipt/complete states require run and receipt identity."
                )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ChatSendOperation:
        run_blob = row["processing_run_id"]
        return ChatSendOperation(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            mode=ChatSendOperationMode(str(row["mode"])),
            request_fingerprint_payload_json=str(row["request_fingerprint_payload_json"]),
            request_fingerprint_sha256=str(row["request_fingerprint_sha256"]),
            request_fingerprint_format_version=int(row["request_fingerprint_format_version"]),
            state=ChatSendOperationState(str(row["state"])),
            processing_run_id=(uuid_from_blob(bytes(run_blob)) if run_blob is not None else None),
            receipt_payload_sha256=(
                str(row["receipt_payload_sha256"])
                if row["receipt_payload_sha256"] is not None
                else None
            ),
            created_at_us=int(row["created_at_us"]),
            updated_at_us=int(row["updated_at_us"]),
        )
