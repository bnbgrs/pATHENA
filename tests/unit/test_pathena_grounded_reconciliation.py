from __future__ import annotations

import uuid

from athena.chat.grounded_completion import GroundedSendCompletionRepository
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


def _force_assistant_committed(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
) -> None:
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

    _force_assistant_committed(database, operation_id)
    run_id = uuid.uuid4()
    completed = GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json='{"assistant_text":"answer","evidence":[]}',
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
    _force_assistant_committed(database, operation_id)
    GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        payload_json='{"assistant_text":"replay","evidence":["CTX-001"]}',
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
    assert status.receipt.payload_json == (
        '{"assistant_text":"replay","evidence":["CTX-001"]}'
    )
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
    _force_assistant_committed(database, operation_id)
    completion = GroundedSendCompletionRepository(database)
    completion.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        payload_json='{"assistant_text":"answer"}',
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
