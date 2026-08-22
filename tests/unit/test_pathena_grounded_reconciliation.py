from __future__ import annotations

import uuid

from athena.chat.grounded_completion import GroundedSendCompletionRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationMode, ChatSendOperationRepository
from athena.common.ids import uuid_to_blob
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
    chats = ChatRepository(database)
    actor = chats.create_actor(actor_type="user")
    return chats.create_chat(actor_id=actor)


def _journal_and_force_assistant(
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
    database.connection.execute(
        "UPDATE chat_send_operations SET state = 'assistant_committed' WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )


def test_reconciliation_projects_absent_incomplete_complete_and_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    reconciler = GroundedSendReconciler(database)

    assert reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.ABSENT

    operations = ChatSendOperationRepository(database)
    operations.store_user_committed(
        operation_id=operation_id,
        chat_id=chat_id,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=fingerprint,
    )
    assert reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE

    conflict = reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=_fingerprint(chat_id, "different"),
    )
    assert conflict.state is GroundedReconciliationState.CONFLICT

    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer","evidence":[]}'
    _journal_and_force_assistant(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    completed = GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    status = reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.COMPLETE
    assert status.receipt == completed
    database.stop()


def test_reconciliation_survives_restart_and_returns_exact_receipt(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    operations = ChatSendOperationRepository(database)
    operations.store_user_committed(
        operation_id=operation_id,
        chat_id=chat_id,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=fingerprint,
    )
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"replay","evidence":["CTX-001"]}'
    _journal_and_force_assistant(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    status = GroundedSendReconciler(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.COMPLETE
    assert status.receipt is not None
    assert status.receipt.payload_json == payload
    database.stop()


def test_reconciliation_fails_closed_when_complete_operation_loses_receipt(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    operations = ChatSendOperationRepository(database)
    operations.store_user_committed(
        operation_id=operation_id,
        chat_id=chat_id,
        mode=ChatSendOperationMode.GROUNDED,
        fingerprint=fingerprint,
    )
    run_id = uuid.uuid4()
    payload = '{"assistant_text":"answer"}'
    _journal_and_force_assistant(
        database,
        chat_id=chat_id,
        operation_id=operation_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    completion = GroundedSendCompletionRepository(database)
    completion.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    database.connection.execute(
        "DELETE FROM grounded_send_receipts WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )
    status = GroundedSendReconciler(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.CONFLICT
    assert status.receipt is None
    database.stop()
