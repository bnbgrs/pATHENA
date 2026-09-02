from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={},
    )
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
        provider_id="lm_studio",
        model_id="primary",
    )
    model_actor = ChatService(chats).ensure_primary_model(
        provider_id="lm_studio",
        model_id="primary",
    )
    return chats, chat_id, operation_id, model_actor


def test_assistant_commit_rejects_semantically_corrupted_provider_result(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, chat_id, operation_id, model_actor = _setup(database)
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE grounded_provider_results
                SET receipt_payload_json = ?
                WHERE operation_id = ?
                """,
                (
                    '{"assistant_text":"tampered","evidence":[]}',
                    uuid_to_blob(operation_id),
                ),
            )

        with pytest.raises(
            ChatSendOperationConflictError,
            match="corrupted durable provider result",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=model_actor,
                content="answer",
            )
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.USER_COMMITTED
    finally:
        database.stop()


def test_assistant_commit_rejects_corrupted_provider_attempt_identity(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats, chat_id, operation_id, model_actor = _setup(database)
        user = chats.create_actor(actor_type="user")
        other_chat_id = chats.create_chat(actor_id=user)
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE grounded_provider_attempts
                SET chat_id = ?
                WHERE operation_id = ?
                """,
                (uuid_to_blob(other_chat_id), uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            ChatSendOperationConflictError,
            match="matching durable provider result",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=model_actor,
                content="answer",
            )
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.USER_COMMITTED
    finally:
        database.stop()
