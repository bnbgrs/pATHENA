"""Atomic assistant-turn persistence for durable Grounded chat sends."""

from __future__ import annotations

import uuid

from athena.chat.models import ChatMessage, MessageType
from athena.chat.repository import ChatRepository, _message_payload_hash
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


class GroundedAssistantTurnRepository:
    """Persist deterministic assistant turn and lifecycle transition atomically."""

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
    ) -> ChatMessage:
        if not content.strip():
            raise ValueError("Grounded assistant message must contain non-whitespace text.")
        assistant_id = assistant_message_id_for_operation(operation_id)
        revision_id = new_uuid7()
        provenance_id = new_uuid7()
        commit_id = new_uuid7()
        created_at_us = utc_now_us()
        payload_hash = _message_payload_hash(content, "text/plain")

        with self.database.write_transaction() as connection:
            self.chat._require_active_actor(connection, actor_id)
            self.chat._require_standard_chat(connection, chat_id)
            operation = connection.execute(
                """
                SELECT chat_id, mode, state, updated_at_us
                FROM chat_send_operations
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if operation is None:
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn requires an existing operation."
                )
            if uuid_from_blob(bytes(operation["chat_id"])) != chat_id:
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn belongs to another chat."
                )
            if str(operation["mode"]) != "grounded":
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn requires Grounded operation mode."
                )
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise ChatSendOperationConflictError(
                    "Grounded assistant operation must be user_committed; reconcile before retry."
                )

            user = connection.execute(
                """
                SELECT chat_id, sequence_no, message_type
                FROM chat_messages
                WHERE message_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if (
                user is None
                or uuid_from_blob(bytes(user["chat_id"])) != chat_id
                or str(user["message_type"]) != MessageType.USER.value
            ):
                raise ChatSendOperationConflictError(
                    "Grounded operation user turn is missing or inconsistent."
                )
            user_sequence = int(user["sequence_no"])
            latest_sequence = int(
                connection.execute(
                    "SELECT COALESCE(MAX(sequence_no), 0) FROM chat_messages WHERE chat_id = ?",
                    (uuid_to_blob(chat_id),),
                ).fetchone()[0]
            )
            if latest_sequence != user_sequence:
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn cannot cross an interleaved chat turn."
                )
            if connection.execute(
                "SELECT 1 FROM chat_messages WHERE message_id = ?",
                (uuid_to_blob(assistant_id),),
            ).fetchone() is not None:
                raise ChatSendOperationConflictError(
                    "Grounded assistant identity already exists; reconcile before retry."
                )

            assistant_sequence = user_sequence + 1
            commit_seq = self.chat._insert_commit(
                connection,
                commit_id=commit_id,
                actor_id=actor_id,
                operation_type="chat_message.create",
                committed_at_us=created_at_us,
            )
            self.chat._insert_entity(
                connection,
                entity_id=assistant_id,
                entity_type="chat_message",
                actor_id=actor_id,
                created_at_us=created_at_us,
                commit_seq=commit_seq,
            )
            self.chat._insert_provenance(
                connection,
                provenance_id=provenance_id,
                entity_id=assistant_id,
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
                    uuid_to_blob(assistant_id),
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
                (uuid_to_blob(assistant_id), uuid_to_blob(revision_id)),
            )
            connection.execute(
                """
                INSERT INTO chat_messages (
                    message_id, chat_id, sequence_no, message_type, actor_id
                ) VALUES (?, ?, ?, 'assistant', ?)
                """,
                (
                    uuid_to_blob(assistant_id),
                    uuid_to_blob(chat_id),
                    assistant_sequence,
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
                    uuid_to_blob(assistant_id),
                    uuid_to_blob(revision_id),
                ),
            )
            updated_at_us = max(created_at_us, int(operation["updated_at_us"]))
            connection.execute(
                """
                UPDATE chat_send_operations
                SET state = 'assistant_committed', updated_at_us = ?
                WHERE operation_id = ?
                """,
                (updated_at_us, uuid_to_blob(operation_id)),
            )

        return ChatMessage(
            message_id=assistant_id,
            chat_id=chat_id,
            sequence_no=assistant_sequence,
            message_type=MessageType.ASSISTANT,
            actor_id=actor_id,
            created_at_us=created_at_us,
            revision_id=revision_id,
            content=content,
            content_format="text/plain",
        )
