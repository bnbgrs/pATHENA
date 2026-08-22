from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_provider_attempt import GroundedProviderAttemptConflictError
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedProviderBoundaryError, GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID):
    return build_chat_request_fingerprint(
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


def _started_operation(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
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
    return coordinator, operation_id, chat_id, fingerprint


def test_provider_attempt_claim_is_single_owner(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, operation_id, chat_id, _ = _started_operation(database)
        first = coordinator.provider_attempts.claim_started(
            operation_id=operation_id,
            chat_id=chat_id,
        )

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="already been claimed",
        ):
            coordinator.provider_attempts.claim_started(
                operation_id=operation_id,
                chat_id=chat_id,
            )

        assert coordinator.provider_attempts.mark_started(
            operation_id=operation_id,
            chat_id=chat_id,
        ) == first
    finally:
        database.stop()


def test_stale_resumable_precheck_cannot_reclaim_provider_boundary(
    tmp_path,
    monkeypatch,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        first, operation_id, chat_id, fingerprint = _started_operation(database)
        contender = GroundedSendCoordinator(database)
        stale = contender.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert stale.state is GroundedRecoveryState.RESUMABLE

        first.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        current = contender.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert current.state is GroundedRecoveryState.AMBIGUOUS

        recoveries = iter((stale, current))
        monkeypatch.setattr(contender, "recover", lambda **_: next(recoveries))

        with pytest.raises(GroundedProviderBoundaryError) as exc_info:
            contender.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS
        assert contender.provider_attempts.load(operation_id) is not None
    finally:
        database.stop()
