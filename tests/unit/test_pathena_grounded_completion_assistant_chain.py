from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import (
    GroundedSendCompletionConflictError,
    GroundedSendCompletionCorruptionError,
    GroundedSendCompletionRepository,
)
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _assistant_committed(database: SQLiteDatabase):
    chats = ChatRepository(database)
    actor = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor)
    operation_id = uuid.uuid4()
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer"}'
    fingerprint = build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="model",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
    )
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor,
        content="hello",
        fingerprint=fingerprint,
    )
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json=payload,
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor,
        content="answer",
    )
    return chats, chat_id, operation_id, run_id, payload


def _tamper_assistant_content(database: SQLiteDatabase, operation_id: uuid.UUID) -> None:
    assistant_id = assistant_message_id_for_operation(operation_id)
    with database.write_transaction() as connection:
        revision = connection.execute(
            "SELECT current_revision_id FROM entity_heads WHERE entity_id = ?",
            (uuid_to_blob(assistant_id),),
        ).fetchone()
        assert revision is not None
        connection.execute(
            "UPDATE chat_message_revisions SET content = ? WHERE revision_id = ?",
            ("tampered", revision["current_revision_id"]),
        )


def test_completion_rejects_tampered_assistant_content(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, chat_id, operation_id, run_id, payload = _assistant_committed(database)
        _tamper_assistant_content(database, operation_id)

        completions = GroundedSendCompletionRepository(database)
        with pytest.raises(
            GroundedSendCompletionConflictError,
            match="assistant turn conflicts with provider result",
        ):
            completions.complete(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=run_id,
                payload_json=payload,
            )

        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
        assert completions.load(operation_id) is None
    finally:
        database.stop()


def test_completion_load_rejects_assistant_tampered_after_completion(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, chat_id, operation_id, run_id, payload = _assistant_committed(database)
        completions = GroundedSendCompletionRepository(database)
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        _tamper_assistant_content(database, operation_id)

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="assistant turn conflicts with provider result",
        ):
            completions.load(operation_id)
    finally:
        database.stop()
