from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationConflictError, ChatSendOperationRepository
from athena.storage.database import SQLiteDatabase


def _fingerprint(*, chat_id: uuid.UUID, content: str, mode: ChatSendMode):
    return build_chat_request_fingerprint(
        mode=mode,
        chat_id=chat_id,
        content=content,
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={},
    )


def test_grounded_user_turn_rejects_fingerprint_for_different_content(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        with pytest.raises(
            ChatSendOperationConflictError,
            match="does not match the committed user turn",
        ):
            GroundedUserTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=user,
                content="actual",
                fingerprint=_fingerprint(
                    chat_id=chat_id,
                    content="different",
                    mode=ChatSendMode.GROUNDED,
                ),
            )
        assert ChatSendOperationRepository(database).load(operation_id) is None
        assert all(message.message_id != operation_id for message in chats.load_chat(chat_id).messages)
    finally:
        database.stop()


def test_grounded_user_turn_rejects_fingerprint_for_different_chat_or_mode(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        other_chat_id = chats.create_chat(actor_id=user)
        repository = GroundedUserTurnRepository(database)

        for fingerprint in (
            _fingerprint(
                chat_id=other_chat_id,
                content="actual",
                mode=ChatSendMode.GROUNDED,
            ),
            _fingerprint(
                chat_id=chat_id,
                content="actual",
                mode=ChatSendMode.DIRECT,
            ),
        ):
            operation_id = uuid.uuid4()
            with pytest.raises(
                ChatSendOperationConflictError,
                match="does not match the committed user turn",
            ):
                repository.commit(
                    operation_id=operation_id,
                    chat_id=chat_id,
                    actor_id=user,
                    content="actual",
                    fingerprint=fingerprint,
                )
            assert ChatSendOperationRepository(database).load(operation_id) is None
    finally:
        database.stop()
