from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationMode,
    ChatSendOperationRepository,
    ChatSendOperationSchemaError,
)
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID, mode: ChatSendMode):
    return build_chat_request_fingerprint(
        mode=mode,
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


def test_operation_load_rejects_corrupted_request_fingerprint_hash(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        repository = ChatSendOperationRepository(database)
        repository.store_user_committed(
            operation_id=operation_id,
            chat_id=chat_id,
            mode=ChatSendOperationMode.DIRECT,
            fingerprint=_fingerprint(chat_id, ChatSendMode.DIRECT),
        )
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE chat_send_operations
                SET request_fingerprint_sha256 = ?
                WHERE operation_id = ?
                """,
                ("0" * 64, uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            ChatSendOperationSchemaError,
            match="invalid request fingerprint",
        ):
            repository.load(operation_id)
    finally:
        database.stop()


def test_operation_load_rejects_completion_identity_in_incomplete_grounded_state(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=_fingerprint(chat_id, ChatSendMode.GROUNDED),
        )
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE chat_send_operations
                SET processing_run_id = ?, receipt_payload_sha256 = ?
                WHERE operation_id = ?
                """,
                (uuid_to_blob(uuid.uuid4()), "a" * 64, uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            ChatSendOperationSchemaError,
            match="incomplete Grounded operation",
        ):
            ChatSendOperationRepository(database).load(operation_id)
    finally:
        database.stop()
