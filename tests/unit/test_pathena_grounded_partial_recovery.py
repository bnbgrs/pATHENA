from __future__ import annotations

import uuid

from athena.chat.grounded_partial_output import GroundedPartialOutputRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_turn import GroundedUserTurnRepository
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


def test_recovery_surfaces_exact_noncanonical_partial_output(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
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
    GroundedProviderAttemptRepository(database).mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    partials = GroundedPartialOutputRepository(database)
    partials.append_delta(
        operation_id=operation_id,
        chat_id=chat_id,
        delta="The first ",
    )
    persisted = partials.append_delta(
        operation_id=operation_id,
        chat_id=chat_id,
        delta="two chunks.",
    )
    assert persisted.content == "The first two chunks."
    assert persisted.delta_count == 2

    status = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedRecoveryState.PARTIAL
    assert status.partial_output is not None
    assert status.partial_output.content == "The first two chunks."
    assert status.provider_result is None
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    restarted = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert restarted.state is GroundedRecoveryState.PARTIAL
    assert restarted.partial_output is not None
    assert restarted.partial_output.content == "The first two chunks."
    assert restarted.partial_output.delta_count == 2
    database.stop()
