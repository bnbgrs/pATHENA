"""Atomic assistant-turn persistence for durable Grounded chat sends."""

from __future__ import annotations

import uuid

from athena.chat.grounded_context_package import (
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run_provenance,
)
from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptRepository,
    _canonical_receipt_payload,
)
from athena.chat.grounded_provider_result_contract import (
    GroundedProviderResultContractError,
    validate_provider_result_contract,
)
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
        self.context_packages = GroundedContextPackageRepository(database)
        self.provider_attempts = GroundedProviderAttemptRepository(database)
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
                SELECT chat_id, mode, state, processing_run_id, updated_at_us
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
                or str(provider_result["assistant_content"]) != content
            ):
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn requires the matching durable provider result."
                )
            operation_run_blob = operation["processing_run_id"]
            if operation_run_blob is not None:
                provider_run_id = uuid_from_blob(
                    bytes(provider_result["processing_run_id"])
                )
                operation_run_id = uuid_from_blob(bytes(operation_run_blob))
                if provider_run_id != operation_run_id:
                    raise ChatSendOperationConflictError(
                        "Grounded assistant turn provider result conflicts with the "
                        "operation-pinned ProcessingRun."
                    )
            try:
                receipt_payload_json = str(provider_result["receipt_payload_json"])
                canonical_receipt, receipt_digest = _canonical_receipt_payload(
                    receipt_payload_json
                )
                validate_provider_result_contract(
                    assistant_content=str(provider_result["assistant_content"]),
                    receipt_payload_json=receipt_payload_json,
                )
            except (ValueError, GroundedProviderResultContractError) as exc:
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn found a corrupted durable provider result."
                ) from exc
            if (
                canonical_receipt != receipt_payload_json
                or receipt_digest != str(provider_result["receipt_payload_sha256"])
            ):
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn found a corrupted durable provider result checksum."
                )

            provider_identity = connection.execute(
                """
                SELECT provider_id, model_id
                FROM grounded_provider_result_identities
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            try:
                context_record = self.context_packages.load(operation_id)
            except GroundedContextPackageSchemaError as exc:
                raise ChatSendOperationConflictError(
                    "Grounded assistant turn found a corrupted pinned ContextPackage."
                ) from exc
            pinned_identity: tuple[str, str] | None = None
            if context_record is not None:
                if operation_run_blob is None:
                    raise ChatSendOperationConflictError(
                        "Pinned ContextPackage requires operation-pinned ProcessingRun "
                        "before assistant commit."
                    )
                signature = context_record.package.model_signature
                pinned_identity = (signature.provider, signature.model_identifier)
                if provider_identity is None:
                    raise ChatSendOperationConflictError(
                        "Pinned ContextPackage requires durable provider result identity before assistant commit."
                    )

            expected_actor_identity: tuple[str, str] | None = pinned_identity
            if provider_identity is not None:
                durable_identity = (
                    str(provider_identity["provider_id"]),
                    str(provider_identity["model_id"]),
                )
                if pinned_identity is not None and durable_identity != pinned_identity:
                    raise ChatSendOperationConflictError(
                        "Grounded assistant provider identity conflicts with pinned ContextPackage model."
                    )
                expected_actor_identity = durable_identity

            if expected_actor_identity is not None:
                actor = connection.execute(
                    """
                    SELECT actor_type, display_name
                    FROM actors
                    WHERE actor_id = ?
                    """,
                    (uuid_to_blob(actor_id),),
                ).fetchone()
                expected_display_name = (
                    f"{expected_actor_identity[0]}:{expected_actor_identity[1]}"
                )
                if (
                    actor is None
                    or str(actor["actor_type"]) != "primary_model"
                    or str(actor["display_name"]) != expected_display_name
                ):
                    raise ChatSendOperationConflictError(
                        "Grounded assistant actor conflicts with durable provider identity."
                    )

            user = connection.execute(
                """
                SELECT chat_id, sequence_no, message_type, actor_id
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
            if context_record is not None:
                assert operation_run_blob is not None
                try:
                    validate_grounded_processing_run_provenance(
                        self.database,
                        processing_run_id=uuid_from_blob(bytes(operation_run_blob)),
                        package=context_record.package,
                        trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
                    )
                except GroundedProcessingRunError as exc:
                    raise ChatSendOperationConflictError(
                        "Grounded assistant turn found invalid ProcessingRun provenance."
                    ) from exc
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