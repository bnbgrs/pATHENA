"""Atomic exact-replay completion for durable Grounded chat sends."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass

from athena.chat.grounded_context_package import (
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run_provenance,
)
from athena.chat.grounded_provider_result_contract import (
    GroundedProviderResultContractError,
    validate_provider_result_contract,
)
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import ChatSendOperationState
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_SEND_RECEIPT_EXTENSION_VERSION = 1


class GroundedSendCompletionError(RuntimeError):
    """Base error for durable Grounded completion invariants."""


class GroundedSendCompletionConflictError(GroundedSendCompletionError):
    """Existing durable state conflicts with the requested completion."""


class GroundedSendCompletionCorruptionError(GroundedSendCompletionError):
    """Persisted exact-replay state failed integrity verification."""


@dataclass(frozen=True, slots=True)
class GroundedSendReceipt:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    processing_run_id: uuid.UUID
    payload_json: str
    payload_sha256: str
    format_version: int
    created_at_us: int


_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "processing_run_id",
    "payload_json",
    "payload_sha256",
    "format_version",
    "extension_schema_version",
    "created_at_us",
)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_send_receipts (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    processing_run_id BLOB(16) NOT NULL CHECK(length(processing_run_id) = 16),
    payload_json TEXT NOT NULL CHECK(length(payload_json) > 1),
    payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256) = 64),
    format_version INTEGER NOT NULL CHECK(format_version = 1),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _canonical_payload(payload_json: str) -> tuple[str, str]:
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Grounded receipt payload must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Grounded receipt payload must be a JSON object.")
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return canonical, digest


class GroundedSendCompletionRepository:
    """Atomically bind exact response bytes to a completed Grounded operation."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.context_packages = GroundedContextPackageRepository(database)
        self._ensure_extension_schema()

    def _ensure_extension_schema(self) -> None:
        row = self.database.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'grounded_send_receipts'"
        ).fetchone()
        if row is None:
            with self.database.write_transaction() as connection:
                connection.execute(_CREATE_SQL)
        self._verify_extension_schema()

    def _verify_extension_schema(self) -> None:
        connection = self.database.connection
        schema_row = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'grounded_send_receipts'"
        ).fetchone()
        if (
            schema_row is None
            or schema_row["sql"] is None
            or _normalized_schema_sql(str(schema_row["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
        ):
            raise GroundedSendCompletionCorruptionError(
                "grounded_send_receipts has an incompatible extension definition."
            )

        columns = connection.execute("PRAGMA table_info(grounded_send_receipts)").fetchall()
        if tuple(str(row["name"]) for row in columns) != _REQUIRED_COLUMNS:
            raise GroundedSendCompletionCorruptionError(
                "grounded_send_receipts has an incompatible extension layout."
            )
        foreign_keys = connection.execute(
            "PRAGMA foreign_key_list(grounded_send_receipts)"
        ).fetchall()
        bindings = {
            (str(row["table"]), str(row["from"]), str(row["on_delete"]).upper())
            for row in foreign_keys
        }
        required = {
            ("chat_send_operations", "operation_id", "CASCADE"),
            ("chats", "chat_id", "CASCADE"),
        }
        if not required.issubset(bindings):
            raise GroundedSendCompletionCorruptionError(
                "grounded_send_receipts is missing required cascade bindings."
            )

    def load(self, operation_id: uuid.UUID) -> GroundedSendReceipt | None:
        row = self.database.connection.execute(
            """
            SELECT r.operation_id, r.chat_id, r.processing_run_id,
                   r.payload_json, r.payload_sha256, r.format_version, r.created_at_us,
                   o.chat_id AS operation_chat_id, o.mode AS operation_mode,
                   o.state AS operation_state,
                   o.processing_run_id AS operation_processing_run_id,
                   o.receipt_payload_sha256 AS operation_receipt_payload_sha256,
                   p.chat_id AS provider_chat_id,
                   p.processing_run_id AS provider_processing_run_id,
                   p.assistant_content AS provider_assistant_content,
                   p.receipt_payload_json AS provider_payload_json,
                   p.receipt_payload_sha256 AS provider_payload_sha256
            FROM grounded_send_receipts AS r
            LEFT JOIN chat_send_operations AS o ON o.operation_id = r.operation_id
            LEFT JOIN grounded_provider_results AS p ON p.operation_id = r.operation_id
            WHERE r.operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        receipt = self._from_row(row)
        if (
            row["operation_chat_id"] is None
            or row["operation_processing_run_id"] is None
            or row["operation_receipt_payload_sha256"] is None
            or row["provider_chat_id"] is None
            or row["provider_processing_run_id"] is None
            or row["provider_assistant_content"] is None
            or row["provider_payload_json"] is None
            or row["provider_payload_sha256"] is None
            or uuid_from_blob(bytes(row["operation_chat_id"])) != receipt.chat_id
            or str(row["operation_mode"]) != "grounded"
            or str(row["operation_state"]) != ChatSendOperationState.COMPLETE.value
            or uuid_from_blob(bytes(row["operation_processing_run_id"]))
            != receipt.processing_run_id
            or str(row["operation_receipt_payload_sha256"]) != receipt.payload_sha256
            or uuid_from_blob(bytes(row["provider_chat_id"])) != receipt.chat_id
            or uuid_from_blob(bytes(row["provider_processing_run_id"]))
            != receipt.processing_run_id
            or str(row["provider_payload_json"]) != receipt.payload_json
            or str(row["provider_payload_sha256"]) != receipt.payload_sha256
        ):
            raise GroundedSendCompletionCorruptionError(
                "Persisted Grounded receipt no longer matches its durable operation chain."
            )
        try:
            validate_provider_result_contract(
                assistant_content=str(row["provider_assistant_content"]),
                receipt_payload_json=str(row["provider_payload_json"]),
            )
        except GroundedProviderResultContractError as exc:
            raise GroundedSendCompletionCorruptionError(
                "Persisted Grounded completion has a corrupted provider result contract."
            ) from exc
        self._validate_pinned_provider_identity(
            self.database.connection,
            operation_id=operation_id,
            corruption=True,
        )
        self._validate_processing_run_chain(
            self.database.connection,
            operation_id=operation_id,
            processing_run_id=receipt.processing_run_id,
            corruption=True,
        )
        self._validate_assistant_chain(
            self.database.connection,
            operation_id=operation_id,
            chat_id=receipt.chat_id,
            assistant_content=str(row["provider_assistant_content"]),
            corruption=True,
        )
        return receipt

    def complete(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        payload_json: str,
    ) -> GroundedSendReceipt:
        canonical, digest = _canonical_payload(payload_json)
        with self.database.write_transaction() as connection:
            operation = connection.execute(
                """
                SELECT chat_id, mode, state, processing_run_id,
                       receipt_payload_sha256, updated_at_us
                FROM chat_send_operations
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if operation is None:
                raise GroundedSendCompletionConflictError(
                    "Grounded completion requires an existing send operation."
                )
            if uuid_from_blob(bytes(operation["chat_id"])) != chat_id:
                raise GroundedSendCompletionConflictError(
                    "Grounded completion chat identity conflicts with send operation."
                )
            if str(operation["mode"]) != "grounded":
                raise GroundedSendCompletionConflictError(
                    "Only Grounded send operations may store Grounded receipts."
                )

            provider_table = connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = 'grounded_provider_results'
                """
            ).fetchone()
            if provider_table is None:
                raise GroundedSendCompletionConflictError(
                    "Grounded completion requires a durable provider result journal."
                )
            provider_result = connection.execute(
                """
                SELECT r.chat_id, r.processing_run_id, r.assistant_content,
                       r.receipt_payload_json, r.receipt_payload_sha256,
                       a.chat_id AS attempt_chat_id
                FROM grounded_provider_results AS r
                LEFT JOIN grounded_provider_attempts AS a ON a.operation_id = r.operation_id
                WHERE r.operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if (
                provider_result is None
                or provider_result["attempt_chat_id"] is None
                or uuid_from_blob(bytes(provider_result["chat_id"])) != chat_id
                or uuid_from_blob(bytes(provider_result["attempt_chat_id"])) != chat_id
                or uuid_from_blob(bytes(provider_result["processing_run_id"]))
                != processing_run_id
                or str(provider_result["receipt_payload_json"]) != canonical
                or str(provider_result["receipt_payload_sha256"]) != digest
            ):
                raise GroundedSendCompletionConflictError(
                    "Grounded completion conflicts with the durable provider result."
                )
            try:
                validate_provider_result_contract(
                    assistant_content=str(provider_result["assistant_content"]),
                    receipt_payload_json=str(provider_result["receipt_payload_json"]),
                )
            except GroundedProviderResultContractError as exc:
                raise GroundedSendCompletionConflictError(
                    "Grounded completion found a corrupted durable provider result."
                ) from exc
            self._validate_pinned_provider_identity(
                connection,
                operation_id=operation_id,
                corruption=False,
            )
            self._validate_processing_run_chain(
                connection,
                operation_id=operation_id,
                processing_run_id=processing_run_id,
                corruption=False,
            )
            self._validate_assistant_chain(
                connection,
                operation_id=operation_id,
                chat_id=chat_id,
                assistant_content=str(provider_result["assistant_content"]),
                corruption=False,
            )

            existing = self._load_in_transaction(connection, operation_id)
            if existing is not None:
                if (
                    existing.chat_id == chat_id
                    and existing.processing_run_id == processing_run_id
                    and existing.payload_json == canonical
                    and existing.payload_sha256 == digest
                    and str(operation["state"]) == ChatSendOperationState.COMPLETE.value
                    and operation["processing_run_id"] is not None
                    and uuid_from_blob(bytes(operation["processing_run_id"]))
                    == processing_run_id
                    and str(operation["receipt_payload_sha256"]) == digest
                ):
                    return existing
                raise GroundedSendCompletionConflictError(
                    "Grounded send operation already has different completion state."
                )

            if str(operation["state"]) != ChatSendOperationState.ASSISTANT_COMMITTED.value:
                raise GroundedSendCompletionConflictError(
                    "Grounded completion requires assistant_committed state."
                )
            if (
                operation["processing_run_id"] is not None
                and uuid_from_blob(bytes(operation["processing_run_id"]))
                != processing_run_id
            ):
                raise GroundedSendCompletionConflictError(
                    "Grounded completion conflicts with the pinned processing-run identity."
                )
            if operation["receipt_payload_sha256"] is not None:
                raise GroundedSendCompletionConflictError(
                    "Grounded operation already has unexpected receipt identity."
                )

            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_send_receipts (
                    operation_id, chat_id, processing_run_id,
                    payload_json, payload_sha256, format_version,
                    extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    uuid_to_blob(processing_run_id),
                    canonical,
                    digest,
                    GROUNDED_SEND_RECEIPT_EXTENSION_VERSION,
                    created_at_us,
                ),
            )
            updated_at_us = max(created_at_us, int(operation["updated_at_us"]))
            connection.execute(
                """
                UPDATE chat_send_operations
                SET state = 'complete', processing_run_id = ?,
                    receipt_payload_sha256 = ?, updated_at_us = ?
                WHERE operation_id = ?
                """,
                (
                    uuid_to_blob(processing_run_id),
                    digest,
                    updated_at_us,
                    uuid_to_blob(operation_id),
                ),
            )

        receipt = self.load(operation_id)
        if receipt is None:
            raise GroundedSendCompletionCorruptionError(
                "Committed Grounded receipt disappeared after transaction."
            )
        return receipt

    def _validate_processing_run_chain(
        self,
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        corruption: bool,
    ) -> None:
        try:
            context_record = self.context_packages.load(operation_id)
        except GroundedContextPackageSchemaError as exc:
            if corruption:
                raise GroundedSendCompletionCorruptionError(
                    "Persisted completion has a corrupted pinned ContextPackage."
                ) from exc
            raise GroundedSendCompletionConflictError(
                "Grounded completion found a corrupted pinned ContextPackage."
            ) from exc
        if context_record is None:
            return

        user = connection.execute(
            """
            SELECT chat_id, actor_id, message_type
            FROM chat_messages
            WHERE message_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if (
            user is None
            or user["actor_id"] is None
            or uuid_from_blob(bytes(user["chat_id"])) != context_record.chat_id
            or str(user["message_type"]) != "user"
        ):
            if corruption:
                raise GroundedSendCompletionCorruptionError(
                    "Persisted completion is missing its Grounded trigger user."
                )
            raise GroundedSendCompletionConflictError(
                "Grounded completion is missing its Grounded trigger user."
            )

        try:
            run = validate_grounded_processing_run_provenance(
                self.database,
                processing_run_id=processing_run_id,
                package=context_record.package,
                trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
            )
        except GroundedProcessingRunError as exc:
            if corruption:
                raise GroundedSendCompletionCorruptionError(
                    "Persisted completion conflicts with its ProcessingRun provenance."
                ) from exc
            raise GroundedSendCompletionConflictError(
                "Grounded completion conflicts with its ProcessingRun provenance."
            ) from exc
        if run.status == "succeeded" and run.finished_at_us is not None:
            return
        if corruption:
            raise GroundedSendCompletionCorruptionError(
                "Persisted completion requires a succeeded ProcessingRun."
            )
        raise GroundedSendCompletionConflictError(
            "Grounded completion requires a succeeded ProcessingRun."
        )

    def _validate_pinned_provider_identity(
        self,
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        corruption: bool,
    ) -> None:
        try:
            context_record = self.context_packages.load(operation_id)
        except GroundedContextPackageSchemaError as exc:
            if corruption:
                raise GroundedSendCompletionCorruptionError(
                    "Persisted completion has a corrupted pinned ContextPackage."
                ) from exc
            raise GroundedSendCompletionConflictError(
                "Grounded completion found a corrupted pinned ContextPackage."
            ) from exc
        if context_record is None:
            return
        identity = connection.execute(
            """
            SELECT provider_id, model_id
            FROM grounded_provider_result_identities
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        signature = context_record.package.model_signature
        matches = (
            identity is not None
            and str(identity["provider_id"]) == signature.provider
            and str(identity["model_id"]) == signature.model_identifier
        )
        if matches:
            return
        if corruption:
            raise GroundedSendCompletionCorruptionError(
                "Persisted completion provider identity conflicts with pinned ContextPackage model."
            )
        raise GroundedSendCompletionConflictError(
            "Grounded completion provider identity conflicts with pinned ContextPackage model."
        )

    @staticmethod
    def _validate_assistant_chain(
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        assistant_content: str,
        corruption: bool,
    ) -> None:
        user = connection.execute(
            """
            SELECT chat_id, sequence_no, message_type
            FROM chat_messages
            WHERE message_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        assistant = connection.execute(
            """
            SELECT m.chat_id, m.sequence_no, m.message_type, m.actor_id,
                   r.content
            FROM chat_messages AS m
            JOIN entity_heads AS h ON h.entity_id = m.message_id
            JOIN chat_message_revisions AS r ON r.revision_id = h.current_revision_id
            WHERE m.message_id = ?
            """,
            (uuid_to_blob(assistant_message_id_for_operation(operation_id)),),
        ).fetchone()
        valid = (
            user is not None
            and assistant is not None
            and uuid_from_blob(bytes(user["chat_id"])) == chat_id
            and str(user["message_type"]) == "user"
            and uuid_from_blob(bytes(assistant["chat_id"])) == chat_id
            and str(assistant["message_type"]) == "assistant"
            and int(assistant["sequence_no"]) == int(user["sequence_no"]) + 1
            and str(assistant["content"]) == assistant_content
        )
        if not valid:
            if corruption:
                raise GroundedSendCompletionCorruptionError(
                    "Persisted completion assistant turn conflicts with provider result."
                )
            raise GroundedSendCompletionConflictError(
                "Grounded completion assistant turn conflicts with provider result."
            )

        identity = connection.execute(
            """
            SELECT provider_id, model_id
            FROM grounded_provider_result_identities
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if identity is None:
            return
        actor = connection.execute(
            """
            SELECT actor_type, display_name
            FROM actors
            WHERE actor_id = ?
            """,
            (assistant["actor_id"],),
        ).fetchone()
        expected_display_name = f"{identity['provider_id']}:{identity['model_id']}"
        if (
            actor is not None
            and str(actor["actor_type"]) == "primary_model"
            and str(actor["display_name"]) == expected_display_name
        ):
            return
        if corruption:
            raise GroundedSendCompletionCorruptionError(
                "Persisted completion assistant actor conflicts with provider identity."
            )
        raise GroundedSendCompletionConflictError(
            "Grounded completion assistant actor conflicts with provider identity."
        )

    def _load_in_transaction(
        self,
        connection: sqlite3.Connection,
        operation_id: uuid.UUID,
    ) -> GroundedSendReceipt | None:
        row = connection.execute(
            """
            SELECT operation_id, chat_id, processing_run_id,
                   payload_json, payload_sha256, format_version, created_at_us
            FROM grounded_send_receipts
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        return None if row is None else self._from_row(row)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> GroundedSendReceipt:
        receipt = GroundedSendReceipt(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            processing_run_id=uuid_from_blob(bytes(row["processing_run_id"])),
            payload_json=str(row["payload_json"]),
            payload_sha256=str(row["payload_sha256"]),
            format_version=int(row["format_version"]),
            created_at_us=int(row["created_at_us"]),
        )
        if receipt.format_version != 1:
            raise GroundedSendCompletionCorruptionError(
                "Grounded receipt format version is unsupported."
            )
        try:
            canonical, digest = _canonical_payload(receipt.payload_json)
        except ValueError as exc:
            raise GroundedSendCompletionCorruptionError(
                "Grounded receipt contains invalid JSON."
            ) from exc
        if canonical != receipt.payload_json or digest != receipt.payload_sha256:
            raise GroundedSendCompletionCorruptionError(
                "Grounded receipt checksum verification failed."
            )
        return receipt
