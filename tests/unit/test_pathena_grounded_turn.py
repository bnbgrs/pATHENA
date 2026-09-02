from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_turn import GroundedUserTurnRepository
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
    actor_id = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor_id)
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
    return actor_id, chat_id, operation_id, fingerprint


def test_user_turn_and_operation_start_commit_atomically(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id, chat_id, operation_id, fingerprint = _setup(database)
    message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor_id,
        content="hello",
        fingerprint=fingerprint,
    )
    assert message.message_id == operation_id
    thread = ChatRepository(database).load_chat(chat_id)
    assert thread.messages[-1] == message
    operation = ChatSendOperationRepository(database).load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.USER_COMMITTED
    assert operation.request_fingerprint_sha256 == fingerprint.payload_sha256
    database.stop()


def test_operation_insert_failure_rolls_back_entire_user_turn(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id, chat_id, operation_id, fingerprint = _setup(database)
    repository = GroundedUserTurnRepository(database)
    database.connection.execute(
        """
        CREATE TRIGGER fail_send_operation_start
        BEFORE INSERT ON chat_send_operations
        BEGIN
            SELECT RAISE(ABORT, 'forced operation insert failure');
        END
        """
    )
    before = ChatRepository(database).load_chat(chat_id)
    with pytest.raises(Exception, match="forced operation insert failure"):
        repository.commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content="hello",
            fingerprint=fingerprint,
        )
    after = ChatRepository(database).load_chat(chat_id)
    assert after == before
    assert database.connection.execute(
        "SELECT 1 FROM entity_registry WHERE entity_id = ?",
        (uuid_to_blob(operation_id),),
    ).fetchone() is None
    assert ChatSendOperationRepository(database).load(operation_id) is None
    database.stop()


def test_duplicate_operation_requires_reconciliation_instead_of_reexecution(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id, chat_id, operation_id, fingerprint = _setup(database)
    repository = GroundedUserTurnRepository(database)
    repository.commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor_id,
        content="hello",
        fingerprint=fingerprint,
    )
    with pytest.raises(ChatSendOperationConflictError, match="reconcile before retry"):
        repository.commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content="hello",
            fingerprint=fingerprint,
        )
    thread = ChatRepository(database).load_chat(chat_id)
    assert len(thread.messages) == 1
    database.stop()
