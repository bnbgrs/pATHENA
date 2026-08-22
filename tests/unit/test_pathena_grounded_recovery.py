from __future__ import annotations

import uuid

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import GroundedSendCompletionRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_turn import GroundedUserTurnRepository
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


def test_recovery_distinguishes_safe_ambiguous_finalize_and_replay(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(actor_type="primary_model", display_name="local:model")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    recovery = GroundedSendRecovery(database)

    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.ABSENT

    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESUMABLE

    first_attempt = GroundedProviderAttemptRepository(database).mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    same_attempt = GroundedProviderAttemptRepository(database).mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    assert first_attempt == same_attempt
    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.AMBIGUOUS

    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.FINALIZATION_REQUIRED

    receipt = GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        payload_json='{"assistant_text":"answer"}',
    )
    complete = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert complete.state is GroundedRecoveryState.COMPLETE
    assert complete.receipt == receipt

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    replay = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert replay.state is GroundedRecoveryState.COMPLETE
    assert replay.receipt == receipt
    database.stop()


def test_recovery_conflict_for_same_operation_different_request(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    status = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=_fingerprint(chat_id, "different"),
    )
    assert status.state is GroundedRecoveryState.CONFLICT
    database.stop()
