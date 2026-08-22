from __future__ import annotations

import json
import uuid

import pytest

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
from athena.common.ids import uuid_to_blob
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
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor,
        content="hello",
        fingerprint=fingerprint,
    )
    return chat_id, operation_id, operations


def _journal_result(
    database: SQLiteDatabase,
    *,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    payload_json: str,
) -> None:
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=processing_run_id,
        assistant_content="answer",
        receipt_payload_json=payload_json,
    )


def _force_assistant_committed(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
) -> None:
    database.connection.execute(
        "UPDATE chat_send_operations SET state = 'assistant_committed' WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )


def test_completion_is_atomic_exact_and_idempotent(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    completions = GroundedSendCompletionRepository(database)
    run_id = uuid.uuid4()
    payload = json.dumps({"assistant_text": "answer", "label": "Äthena", "evidence": [2, 1]})
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    _force_assistant_committed(database, operation_id)

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
    assert json.loads(first.payload_json) == {
        "assistant_text": "answer",
        "evidence": [2, 1],
        "label": "Äthena",
    }
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
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","label":"no"}'
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    completions = GroundedSendCompletionRepository(database)
    with pytest.raises(
        GroundedSendCompletionConflictError,
        match="assistant_committed",
    ):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
    assert completions.load(operation_id) is None
    database.stop()


def test_completion_conflict_preserves_original_receipt(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, _ = _setup(database)
    completions = GroundedSendCompletionRepository(database)
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","label":"first"}'
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    _force_assistant_committed(database, operation_id)
    original = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    with pytest.raises(GroundedSendCompletionConflictError):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json='{"assistant_text":"answer","label":"different"}',
        )
    assert completions.load(operation_id) == original
    database.stop()


def test_completion_rejects_run_or_payload_different_from_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","label":"recorded"}'
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    _force_assistant_committed(database, operation_id)
    completions = GroundedSendCompletionRepository(database)

    with pytest.raises(
        GroundedSendCompletionConflictError,
        match="durable provider result",
    ):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=uuid.uuid4(),
            payload_json=payload,
        )
    with pytest.raises(
        GroundedSendCompletionConflictError,
        match="durable provider result",
    ):
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json='{"assistant_text":"answer","label":"different"}',
        )

    operation = operations.load(operation_id)
    assert operation is not None
    assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
    assert completions.load(operation_id) is None
    database.stop()


def test_failed_operation_update_rolls_back_receipt_insert(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","label":"rollback"}'
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    _force_assistant_committed(database, operation_id)
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
            processing_run_id=run_id,
            payload_json=payload,
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
    chat_id, operation_id, _ = _setup(database)
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","label":"restart"}'
    _journal_result(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    _force_assistant_committed(database, operation_id)
    completions = GroundedSendCompletionRepository(database)
    stored = completions.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    ChatSendOperationRepository(database)
    recovered = GroundedSendCompletionRepository(database).load(operation_id)
    assert recovered == stored
    database.stop()


def test_completion_load_rejects_operation_chain_corruption(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, _ = _setup(database)
        run_id = uuid.uuid4()
        payload = '{"assistant_text":"answer","label":"operation-chain"}'
        _journal_result(
            database,
            chat_id=chat_id,
            operation_id=operation_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        _force_assistant_committed(database, operation_id)
        completions = GroundedSendCompletionRepository(database)
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE chat_send_operations SET state = 'assistant_committed' WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            )

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="durable operation chain",
        ):
            completions.load(operation_id)
    finally:
        database.stop()


def test_completion_load_rejects_missing_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, _ = _setup(database)
        run_id = uuid.uuid4()
        payload = '{"assistant_text":"answer","label":"provider-chain"}'
        _journal_result(
            database,
            chat_id=chat_id,
            operation_id=operation_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        _force_assistant_committed(database, operation_id)
        completions = GroundedSendCompletionRepository(database)
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        with database.write_transaction() as connection:
            connection.execute(
                "DELETE FROM grounded_provider_results WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            )

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="durable operation chain",
        ):
            completions.load(operation_id)
    finally:
        database.stop()


def test_completion_rejects_corrupted_provider_attempt_identity(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, operations = _setup(database)
        chats = ChatRepository(database)
        actor = chats.create_actor(actor_type="user")
        other_chat_id = chats.create_chat(actor_id=actor)
        run_id = uuid.uuid4()
        payload = '{"assistant_text":"answer","label":"attempt-chain"}'
        _journal_result(
            database,
            chat_id=chat_id,
            operation_id=operation_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        _force_assistant_committed(database, operation_id)
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_attempts SET chat_id = ? WHERE operation_id = ?",
                (uuid_to_blob(other_chat_id), uuid_to_blob(operation_id)),
            )

        completions = GroundedSendCompletionRepository(database)
        with pytest.raises(
            GroundedSendCompletionConflictError,
            match="durable provider result",
        ):
            completions.complete(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=run_id,
                payload_json=payload,
            )
        operation = operations.load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
        assert completions.load(operation_id) is None
    finally:
        database.stop()


def test_same_named_but_weakened_receipt_definition_fails_closed(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id, operation_id, operations = _setup(database)
    assert chat_id is not None
    assert operation_id is not None
    assert operations is not None
    database.connection.execute(
        """
        CREATE TABLE grounded_send_receipts (
            operation_id BLOB PRIMARY KEY,
            chat_id BLOB,
            processing_run_id BLOB,
            payload_json TEXT,
            payload_sha256 TEXT,
            format_version INTEGER,
            extension_schema_version INTEGER,
            created_at_us INTEGER,
            FOREIGN KEY(operation_id)
                REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
            FOREIGN KEY(chat_id)
                REFERENCES chats(chat_id) ON DELETE CASCADE
        )
        """
    )
    with pytest.raises(
        GroundedSendCompletionCorruptionError,
        match="incompatible extension definition",
    ):
        GroundedSendCompletionRepository(database)
    database.stop()