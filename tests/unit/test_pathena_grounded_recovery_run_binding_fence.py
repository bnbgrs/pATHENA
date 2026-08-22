from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import (
    GroundedRecoveryConflictError,
    GroundedRecoveryState,
    GroundedSendRecovery,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationRepository
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
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


def test_recovery_fails_closed_when_provider_result_run_conflicts_with_pinned_run(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )

        pinned_run_id = uuid.uuid4()
        result_run_id = uuid.uuid4()
        assert result_run_id != pinned_run_id
        ChatSendOperationRepository(database).bind_grounded_processing_run(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=pinned_run_id,
        )

        provider = GroundedProviderAttemptRepository(database)
        provider.mark_started(operation_id=operation_id, chat_id=chat_id)
        provider.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result_run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
            provider_id="lm_studio",
            model_id="primary",
        )

        recovery = GroundedSendRecovery(database)
        status = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.provider_result is None
        assert status.provider_identity is None

        with pytest.raises(
            GroundedRecoveryConflictError,
            match="cannot finalize from conflict",
        ):
            recovery.finalize_recorded_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
        assert len(chats.load_chat(chat_id).messages) == 1
    finally:
        database.stop()
