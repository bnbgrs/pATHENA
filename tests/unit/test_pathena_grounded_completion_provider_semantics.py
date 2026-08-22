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
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    actor = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="model",
        requested_embedding_model_id="embed",
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
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
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","evidence":[]}'
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json=payload,
    )
    return chat_id, operation_id, run_id, payload


def _commit_assistant(database: SQLiteDatabase, operation_id: uuid.UUID) -> None:
    user = database.connection.execute(
        "SELECT chat_id, actor_id FROM chat_messages WHERE message_id = ?",
        (uuid_to_blob(operation_id),),
    ).fetchone()
    assert user is not None
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=uuid_from_blob(bytes(user["chat_id"])),
        actor_id=uuid_from_blob(bytes(user["actor_id"])),
        content="answer",
    )


def test_completion_rejects_semantically_corrupted_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, run_id, payload = _setup(database)
        _commit_assistant(database, operation_id)
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET assistant_content = ? WHERE operation_id = ?",
                ("tampered", uuid_to_blob(operation_id)),
            )

        completions = GroundedSendCompletionRepository(database)
        with pytest.raises(
            GroundedSendCompletionConflictError,
            match="corrupted durable provider result",
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


def test_completion_load_rejects_semantically_corrupted_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, run_id, payload = _setup(database)
        _commit_assistant(database, operation_id)
        completions = GroundedSendCompletionRepository(database)
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET assistant_content = ? WHERE operation_id = ?",
                ("tampered", uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="provider result contract",
        ):
            completions.load(operation_id)
    finally:
        database.stop()
