from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_turn import GroundedUserTurnRepository
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


def _fingerprint(
    chat_id: uuid.UUID,
    content: str = "hello",
    *,
    mode: ChatSendMode = ChatSendMode.GROUNDED,
):
    return build_chat_request_fingerprint(
        mode=mode,
        chat_id=chat_id,
        content=content,
        requested_model_id="model",
        requested_embedding_model_id=(
            "embed" if mode is ChatSendMode.GROUNDED else None
        ),
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
    )


def _chat(database: SQLiteDatabase) -> tuple[uuid.UUID, uuid.UUID]:
    repository = ChatRepository(database)
    actor_id = repository.create_actor(actor_type="user")
    return actor_id, repository.create_chat(actor_id=actor_id)


def _start_grounded(
    database: SQLiteDatabase,
    *,
    actor_id: uuid.UUID,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
) -> None:
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor_id,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )


def test_extension_is_created_and_survives_restart(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    _, chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    stored = repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.DIRECT,
        fingerprint=_fingerprint(chat, mode=ChatSendMode.DIRECT),
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
    _, chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    repository.store_user_committed(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.DIRECT,
        fingerprint=_fingerprint(chat, mode=ChatSendMode.DIRECT),
    )
    assert repository.match_request(
        operation_id=operation_id,
        chat_id=chat,
        mode=ChatSendOperationMode.DIRECT,
        fingerprint=_fingerprint(
            chat,
            "different",
            mode=ChatSendMode.DIRECT,
        ),
    ) is ChatSendOperationMatch.CONFLICT
    with pytest.raises(ChatSendOperationConflictError):
        repository.store_user_committed(
            operation_id=operation_id,
            chat_id=chat,
            mode=ChatSendOperationMode.DIRECT,
            fingerprint=_fingerprint(
                chat,
                "different",
                mode=ChatSendMode.DIRECT,
            ),
        )
    database.stop()


def test_grounded_start_cannot_bypass_atomic_user_turn_repository(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)

    with pytest.raises(
        ChatSendOperationConflictError,
        match="atomic Grounded user-turn repository",
    ):
        repository.store_user_committed(
            operation_id=operation_id,
            chat_id=chat,
            mode=ChatSendOperationMode.GROUNDED,
            fingerprint=_fingerprint(chat),
        )

    assert repository.load(operation_id) is None
    database.stop()


def test_grounded_lifecycle_cannot_bypass_atomic_repositories(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor, chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    _start_grounded(
        database,
        actor_id=actor,
        chat_id=chat,
        operation_id=operation_id,
    )

    with pytest.raises(
        ChatSendOperationConflictError,
        match="atomic Grounded repositories",
    ):
        repository.advance(
            operation_id,
            ChatSendOperationState.ASSISTANT_COMMITTED,
        )

    for target in (
        ChatSendOperationState.RECEIPT_COMMITTED,
        ChatSendOperationState.COMPLETE,
    ):
        with pytest.raises(
            ChatSendOperationConflictError,
            match="atomic Grounded repositories",
        ):
            repository.advance(
                operation_id,
                target,
                processing_run_id=uuid.uuid4(),
                receipt_payload_sha256="a" * 64,
            )

    operation = repository.load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.USER_COMMITTED
    assert operation.processing_run_id is None
    assert operation.receipt_payload_sha256 is None
    database.stop()


def test_grounded_lifecycle_cannot_skip_assistant_commit(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor, chat = _chat(database)
    operation_id = uuid.uuid4()
    repository = ChatSendOperationRepository(database)
    _start_grounded(
        database,
        actor_id=actor,
        chat_id=chat,
        operation_id=operation_id,
    )
    with pytest.raises(
        ChatSendOperationConflictError,
        match="atomic Grounded repositories",
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
