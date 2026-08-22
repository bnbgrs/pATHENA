from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.models import MessageType
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(actor_type="primary_model", display_name="local:model")
    chat_id = chats.create_chat(actor_id=user)
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
        retrieval_configuration={"max_items": 4},
    )
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
    )
    return chats, user, model, chat_id, operation_id


def test_assistant_turn_and_state_commit_atomically(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats, _, model, chat_id, operation_id = _setup(database)
    message = GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    thread = chats.load_chat(chat_id)
    assert thread.messages[-1] == message
    assert message.sequence_no == 2
    operation = ChatSendOperationRepository(database).load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
    database.stop()


def test_operation_update_failure_rolls_back_entire_assistant_turn(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats, _, model, chat_id, operation_id = _setup(database)
    repository = GroundedAssistantTurnRepository(database)
    before = chats.load_chat(chat_id)
    database.connection.execute(
        """
        CREATE TRIGGER fail_assistant_state
        BEFORE UPDATE ON chat_send_operations
        WHEN NEW.state = 'assistant_committed'
        BEGIN
            SELECT RAISE(ABORT, 'forced assistant state failure');
        END
        """
    )
    with pytest.raises(Exception, match="forced assistant state failure"):
        repository.commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=model,
            content="answer",
        )
    assert chats.load_chat(chat_id) == before
    operation = ChatSendOperationRepository(database).load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.USER_COMMITTED
    database.stop()


def test_interleaved_turn_blocks_operation_assistant(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats, user, model, chat_id, operation_id = _setup(database)
    chats.append_message(
        chat_id=chat_id,
        actor_id=user,
        message_type=MessageType.USER,
        content="interleaved",
    )
    with pytest.raises(ChatSendOperationConflictError, match="interleaved"):
        GroundedAssistantTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=model,
            content="answer",
        )
    assert database.connection.execute(
        "SELECT COUNT(*) FROM chat_messages WHERE chat_id = ?",
        (uuid_to_blob(chat_id),),
    ).fetchone()[0] == 2
    database.stop()


def test_assistant_turn_requires_recorded_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats, _, model, chat_id, operation_id = _setup(database)
    database.connection.execute(
        "DELETE FROM grounded_provider_results WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )
    before = chats.load_chat(chat_id)
    with pytest.raises(ChatSendOperationConflictError, match="matching durable provider result"):
        GroundedAssistantTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=model,
            content="answer",
        )
    assert chats.load_chat(chat_id) == before
    database.stop()


def test_assistant_turn_rejects_content_different_from_recorded_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats, _, model, chat_id, operation_id = _setup(database)
    before = chats.load_chat(chat_id)
    with pytest.raises(
        ChatSendOperationConflictError,
        match="matching durable provider result",
    ):
        GroundedAssistantTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=model,
            content="different answer",
        )
    assert chats.load_chat(chat_id) == before
    database.stop()
