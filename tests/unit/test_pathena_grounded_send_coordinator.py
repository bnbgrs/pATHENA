from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_reconciliation import GroundedReconciliationState
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import (
    GroundedProviderBoundaryError,
    GroundedSendCoordinator,
    GroundedSendStateError,
)
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

    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESUMABLE
    attempt = coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert attempt.operation_id == operation_id
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.AMBIGUOUS
    with pytest.raises(GroundedProviderBoundaryError) as exc_info:
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
    assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS

    run_id = uuid.uuid4()
    result = coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":["CTX-001"]}',
    )
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESULT_AVAILABLE

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    coordinator = GroundedSendCoordinator(database)
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESULT_AVAILABLE

    receipt = coordinator.finalize_recorded_result(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        fingerprint=fingerprint,
    )
    assert receipt.payload_json == result.receipt_payload_json
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


def test_provider_result_rejects_receipt_assistant_text_mismatch(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, user, _, chat_id = _setup(database)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        coordinator = GroundedSendCoordinator(database)
        coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

        with pytest.raises(ValueError, match="must match assistant content exactly"):
            coordinator.record_provider_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                processing_run_id=uuid.uuid4(),
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"different"}',
            )

        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.AMBIGUOUS
    finally:
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
