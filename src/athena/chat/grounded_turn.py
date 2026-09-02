"""Atomic user-turn and durable operation start for Grounded chat sends."""

from __future__ import annotations

import json
import uuid

from athena.chat.models import ChatMessage, MessageType
from athena.chat.repository import ChatRepository, _message_payload_hash
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_operation import (
    CHAT_SEND_OPERATION_EXTENSION_VERSION,
    ChatSendOperationConflictError,
    ChatSendOperationMode,
    ChatSendOperationRepository,
)
from athena.common.ids import new_uuid7, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


class GroundedUserTurnRepository:
    """Persist the deterministic user turn and operation start atomically."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.operations = ChatSendOperationRepository(database)
        self.chat = ChatRepository(database)

    def commit(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        content: str,
        fingerprint: ChatRequestFingerprint,
    ) -> ChatMessage:
        if not content.strip():
            raise ValueError("Grounded user message must contain non-whitespace text.")
        ChatSendOperationRepository._validate_fingerprint(fingerprint)
        fingerprint_payload = json.loads(fingerprint.payload_json)
        if (
            fingerprint_payload.get("fingerprint_format_version")
            != fingerprint.format_version
            or fingerprint_payload.get("mode") != ChatSendOperationMode.GROUNDED.value
            or fingerprint_payload.get("chat_id") != str(chat_id)
            or fingerprint_payload.get("content") != content
        ):
            raise ChatSendOperationConflictError(
                "Grounded request fingerprint does not match the committed user turn."
            )
        revision_id = new_uuid7()
        provenance_id = new_uuid7()
        commit_id = new_uuid7()
        created_at_us = utc_now_us()
        payload_hash = _message_payload_hash(content, "text/plain")

        with self.database.write_transaction() as connection:
            self.chat._require_active_actor(connection, actor_id)
            self.chat._require_standard_chat(connection, chat_id)

            existing_operation = connection.execute(
                "SELECT 1 FROM chat_send_operations WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing_operation is not None:
                raise ChatSendOperationConflictError(
                    "Grounded user-turn operation already exists; reconcile before retry."
                )

            existing_message = connection.execute(
                "SELECT 1 FROM chat_messages WHERE message_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing_message is not None:
                raise ChatSendOperationConflictError(
                    "Grounded user-turn message identity already exists without operation state."
                )

            next_sequence = int(
                connection.execute(
                    """
                    SELECT COALESCE(MAX(sequence_no), 0) + 1
                    FROM chat_messages
                    WHERE chat_id = ?
                    """,
                    (uuid_to_blob(chat_id),),
                ).fetchone()[0]
            )
            commit_seq = self.chat._insert_commit(
                connection,
                commit_id=commit_id,
                actor_id=actor_id,
                operation_type="chat_message.create",
                committed_at_us=created_at_us,
            )
            self.chat._insert_entity(
                connection,
                entity_id=operation_id,
                entity_type="chat_message",
                actor_id=actor_id,
                created_at_us=created_at_us,
                commit_seq=commit_seq,
            )
            self.chat._insert_provenance(
                connection,
                provenance_id=provenance_id,
                entity_id=operation_id,
                revision_id=revision_id,
                operation="chat_message.create",
                actor_id=actor_id,
                created_at_us=created_at_us,
            )
            connection.execute(
                """
                INSERT INTO revisions (
                    revision_id, entity_id, revision_no, parent_revision_id,
                    created_at_us, created_by_actor_id, provenance_id,
                    schema_version, payload_hash, change_kind, commit_id
                ) VALUES (?, ?, 1, NULL, ?, ?, ?, 1, ?, 'create', ?)
                """,
                (
                    uuid_to_blob(revision_id),
                    uuid_to_blob(operation_id),
                    created_at_us,
                    uuid_to_blob(actor_id),
                    uuid_to_blob(provenance_id),
                    payload_hash,
                    uuid_to_blob(commit_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO entity_heads (
                    entity_id, current_revision_id, current_revision_no
                ) VALUES (?, ?, 1)
                """,
                (uuid_to_blob(operation_id), uuid_to_blob(revision_id)),
            )
            connection.execute(
                """
                INSERT INTO chat_messages (
                    message_id, chat_id, sequence_no, message_type, actor_id
                ) VALUES (?, ?, ?, 'user', ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    next_sequence,
                    uuid_to_blob(actor_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO chat_message_revisions (
                    revision_id, content, content_format, protected_payload_id
                ) VALUES (?, ?, 'text/plain', NULL)
                """,
                (uuid_to_blob(revision_id), content),
            )
            connection.execute(
                """
                INSERT INTO commit_changes (
                    commit_seq, entity_id, revision_id, change_type
                ) VALUES (?, ?, ?, 'create')
                """,
                (
                    commit_seq,
                    uuid_to_blob(operation_id),
                    uuid_to_blob(revision_id),
                ),
            )
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
                    ChatSendOperationMode.GROUNDED.value,
                    fingerprint.payload_json,
                    fingerprint.payload_sha256,
                    fingerprint.format_version,
                    CHAT_SEND_OPERATION_EXTENSION_VERSION,
                    created_at_us,
                    created_at_us,
                ),
            )

        return ChatMessage(
            message_id=operation_id,
            chat_id=chat_id,
            sequence_no=next_sequence,
            message_type=MessageType.USER,
            actor_id=actor_id,
            created_at_us=created_at_us,
            revision_id=revision_id,
            content=content,
            content_format="text/plain",
        )