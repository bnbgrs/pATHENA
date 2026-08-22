from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_reconciliation import GroundedReconciliationState
from athena.chat.grounded_send import GroundedSendCoordinator, GroundedSendStateError
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
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


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(actor_type="primary_model", display_name="local:model")
    chat_id = chats.create_chat(actor_id=user)
    return chats, user, model, chat_id


def test_crash_boundaries_reconcile_without_reexecution(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats, user, model, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)

    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.ABSENT

    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    assert started.status.state is GroundedReconciliationState.INCOMPLETE
    assert len(chats.load_chat(chat_id).messages) == 1

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    coordinator = GroundedSendCoordinator(database)
    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE
    with pytest.raises(GroundedSendStateError):
        coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )

    coordinator.commit_assistant(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    coordinator = GroundedSendCoordinator(database)
    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE

    run_id = uuid.uuid4()
    receipt = coordinator.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json='{"assistant_text":"answer","evidence":["CTX-001"]}',
    )
    complete = coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert complete.state is GroundedReconciliationState.COMPLETE
    assert complete.receipt == receipt

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    replay = GroundedSendCoordinator(database).reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert replay.state is GroundedReconciliationState.COMPLETE
    assert replay.receipt is not None
    assert replay.receipt.payload_json == receipt.payload_json
    assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
    database.stop()


def test_same_operation_different_request_is_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, user, _, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    coordinator = GroundedSendCoordinator(database)
    coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    conflict = coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=_fingerprint(chat_id, "different"),
    )
    assert conflict.state is GroundedReconciliationState.CONFLICT
    with pytest.raises(GroundedSendStateError) as exc_info:
        coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="different",
            fingerprint=_fingerprint(chat_id, "different"),
        )
    assert exc_info.value.status.state is GroundedReconciliationState.CONFLICT
    database.stop()
