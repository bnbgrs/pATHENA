from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationMatch,
    ChatSendOperationMode,
    ChatSendOperationRepository,
    ChatSendOperationSchemaError,
    ChatSendOperationState,
)
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID, content: str = "hello"):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content=content,
        requested_model_id="model",
        requested_embedding_model_id="embed",
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
    )


def _chat(database: SQLiteDatabase) -> uuid.UUID:
    repository = ChatRepository(database)
    actor_id = repository.create_actor(actor_type="user")
    return repository.create_chat(actor_id=actor_id)


def test_extension_is_created_and_survives_restart(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    stored = repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=_fingerprint(chat),
    )
    assert stored.state is ChatSendOperationState.USER_COMMITTED
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    recovered = ChatSendOperationRepository(database).load(operation_id)
    assert recovered == stored
    database.stop()


def test_same_operation_id_with_different_request_conflicts(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=_fingerprint(chat),
    )
    assert repository.match_request(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=_fingerprint(chat, "different"),
    ) is ChatSendOperationMatch.CONFLICT
    with pytest.raises(ChatSendOperationConflictError):
        repository.store_user_committed(
            operation_id=operation_id,
            chat_id=chat,
            mode=ChatSendOperationMode.GROUNDED,
            fingerprint=_fingerprint(chat, "different"),
        )
    database.stop()


def test_grounded_lifecycle_cannot_manufacture_receipt_or_completion(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=_fingerprint(chat),
    )
    repository.advance(operation_id, ChatSendOperationState.ASSISTANT_COMMITTED)

    for target in (
        ChatSendOperationState.RECEIPT_COMMITTED,
        ChatSendOperationState.COMPLETE,
    ):
        with pytest.raises(
            ChatSendOperationConflictError,
            match="atomic Grounded completion repositories",
        ):
            repository.advance(
                operation_id,
                target,
                processing_run_id=uuid.uuid4(),
                receipt_payload_sha256="a" * 64,
            )

    operation = repository.load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
    assert operation.processing_run_id is None
    assert operation.receipt_payload_sha256 is None
    database.stop()


def test_grounded_lifecycle_cannot_skip_assistant_commit(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=_fingerprint(chat),
    )
    with pytest.raises(
        ChatSendOperationConflictError,
        match="atomic Grounded completion repositories",
    ):
        repository.advance(
            operation_id,
            ChatSendOperationState.COMPLETE,
            processing_run_id=uuid.uuid4(),
            receipt_payload_sha256="a" * 64,
        )
    database.stop()


def test_incompatible_preexisting_extension_fails_closed(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    database.connection.execute("CREATE TABLE chat_send_operations (operation_id BLOB PRIMARY KEY)")
    with pytest.raises(ChatSendOperationSchemaError):
        ChatSendOperationRepository(database)
    database.stop()


def test_same_named_but_weakened_extension_definition_fails_closed(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    database.connection.execute(
        """
        CREATE TABLE chat_send_operations (
            operation_id BLOB PRIMARY KEY,
            chat_id BLOB,
            mode TEXT,
            request_fingerprint_payload_json TEXT,
            request_fingerprint_sha256 TEXT,
            request_fingerprint_format_version INTEGER,
            extension_schema_version INTEGER,
            state TEXT,
            processing_run_id BLOB,
            receipt_payload_sha256 TEXT,
            created_at_us INTEGER,
            updated_at_us INTEGER,
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
        )
        """
    )
    with pytest.raises(
        ChatSendOperationSchemaError,
        match="incompatible schema extension definition",
    ):
        ChatSendOperationRepository(database)
    database.stop()
