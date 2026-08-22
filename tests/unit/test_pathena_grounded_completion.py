from __future__ import annotations

import json
import uuid

import pytest

from athena.chat.grounded_completion import (
    GroundedSendCompletionConflictError,
    GroundedSendCompletionRepository,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationMode,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.storage.database import SQLiteDatabase


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    actor = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor)
    operation_id = uuid.uuid4()
    operations = ChatSendOperationRepository(database)
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
    operations.store_user_committed(
        operation_id=operation_id,
        chat_id=chat_id,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=fingerprint,
    )
    return chat_id, operation_id, operations


def test_completion_is_atomic_exact_and_idempotent(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    operations.advance(operation_id, ChatSendOperationState.ASSISTANT_COMMITTED)
    completions = GroundedSendCompletionRepository(database)
    run_id = uuid.uuid4()
    payload = json.dumps({"text": "Äthena", "evidence": [2, 1]})

    first = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    second = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )

    assert first == second
    assert json.loads(first.payload_json) == {"evidence": [2, 1], "text": "Äthena"}
    operation = operations.load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.COMPLETE
    assert operation.processing_run_id == run_id
    assert operation.receipt_payload_sha256 == first.payload_sha256
    database.stop()


def test_completion_refuses_before_assistant_commit(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, _ = _setup(database)
    completions = GroundedSendCompletionRepository(database)
    with pytest.raises(
        GroundedSendCompletionConflictError,
        match="assistant_committed",
    ):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=uuid.uuid4(),
            payload_json='{"text":"no"}',
        )
    assert completions.load(operation_id) is None
    database.stop()


def test_completion_conflict_preserves_original_receipt(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    operations.advance(operation_id, ChatSendOperationState.ASSISTANT_COMMITTED)
    completions = GroundedSendCompletionRepository(database)
    run_id = uuid.uuid4()
    original = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json='{"text":"first"}',
    )
    with pytest.raises(GroundedSendCompletionConflictError):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json='{"text":"different"}',
        )
    assert completions.load(operation_id) == original
    database.stop()


def test_failed_operation_update_rolls_back_receipt_insert(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    operations.advance(operation_id, ChatSendOperationState.ASSISTANT_COMMITTED)
    completions = GroundedSendCompletionRepository(database)
    database.connection.execute(
        """
        CREATE TRIGGER fail_grounded_completion
        BEFORE UPDATE ON chat_send_operations
        WHEN NEW.state = 'complete'
        BEGIN
            SELECT RAISE(ABORT, 'forced completion failure');
        END
        """
    )
    with pytest.raises(Exception, match="forced completion failure"):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=uuid.uuid4(),
            payload_json='{"text":"rollback"}',
        )
    assert completions.load(operation_id) is None
    operation = operations.load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
    database.stop()


def test_exact_receipt_survives_restart(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chat_id, operation_id, operations = _setup(database)
    operations.advance(operation_id, ChatSendOperationState.ASSISTANT_COMMITTED)
    completions = GroundedSendCompletionRepository(database)
    run_id = uuid.uuid4()
    stored = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json='{"text":"restart"}',
    )
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    ChatSendOperationRepository(database)
    recovered = GroundedSendCompletionRepository(database).load(operation_id)
    assert recovered == stored
    database.stop()
