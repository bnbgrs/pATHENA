from __future__ import annotations

import uuid

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import GroundedSendCompletionRepository
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository, _message_payload_hash
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
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


def test_recovery_distinguishes_provider_crash_boundaries_and_exact_replay(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(actor_type="primary_model", display_name="local:model")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    run_id = uuid.uuid4()
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

    provider = GroundedProviderAttemptRepository(database)
    first_attempt = provider.mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    assert provider.mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    ) == first_attempt
    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.AMBIGUOUS

    result = provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":["CTX-001"]}',
        provider_id="lm_studio",
        model_id="primary",
    )
    assert provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"evidence":["CTX-001"],"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    ) == result
    available = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert available.state is GroundedRecoveryState.RESULT_AVAILABLE
    assert available.provider_result == result
    assert available.provider_identity is not None
    assert available.provider_identity.provider_id == "lm_studio"
    assert available.provider_identity.model_id == "primary"

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    recovery = GroundedSendRecovery(database)
    restarted = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert restarted.state is GroundedRecoveryState.RESULT_AVAILABLE
    assert restarted.provider_result == result
    assert restarted.provider_identity is not None
    assert restarted.provider_identity.provider_id == "lm_studio"
    assert restarted.provider_identity.model_id == "primary"

    durable_model = recovery.chat.ensure_primary_model(
        provider_id="lm_studio",
        model_id="primary",
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=durable_model,
        content="answer",
    )
    pending_finalization = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert pending_finalization.state is GroundedRecoveryState.FINALIZATION_REQUIRED
    assert pending_finalization.provider_result == result
    assert pending_finalization.provider_identity is not None
    assert pending_finalization.provider_identity.model_id == "primary"

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    recovery = GroundedSendRecovery(database)
    receipt = recovery.finalize_recorded_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    complete = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert complete.state is GroundedRecoveryState.COMPLETE
    assert complete.receipt == receipt
    assert complete.provider_result == result
    assert complete.provider_identity is not None
    assert complete.provider_identity.model_id == "primary"
    assert receipt.processing_run_id == run_id
    assert receipt.payload_json == result.receipt_payload_json

    assert recovery.finalize_recorded_result(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        fingerprint=fingerprint,
    ) == receipt
    assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
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


def test_recovery_inspect_fails_closed_when_assistant_content_conflicts(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:primary",
    )
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
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        assistant_content="recorded answer",
        receipt_payload_json='{"assistant_text":"recorded answer","evidence":[]}',
        provider_id="lm_studio",
        model_id="primary",
    )
    assistant = GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="recorded answer",
    )
    database.connection.execute(
        "UPDATE chat_message_revisions SET content = ? WHERE revision_id = ?",
        ("different answer", uuid_to_blob(assistant.revision_id)),
    )
    database.connection.execute(
        "UPDATE revisions SET payload_hash = ? WHERE revision_id = ?",
        (
            _message_payload_hash("different answer", "text/plain"),
            uuid_to_blob(assistant.revision_id),
        ),
    )

    status = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedRecoveryState.CONFLICT
    database.stop()


def test_recovery_inspect_fails_closed_when_assistant_model_conflicts(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:primary",
    )
    wrong_model = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:other",
    )
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
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
        provider_id="lm_studio",
        model_id="primary",
    )
    assistant = GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    database.connection.execute(
        "UPDATE chat_messages SET actor_id = ? WHERE message_id = ?",
        (uuid_to_blob(wrong_model), uuid_to_blob(assistant.message_id)),
    )

    status = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedRecoveryState.CONFLICT
    database.stop()


def test_recovery_complete_fails_closed_when_provider_result_is_lost(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    run_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    result = provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
        provider_id="lm_studio",
        model_id="primary",
    )
    recovery = GroundedSendRecovery(database)
    model = recovery.chat.ensure_primary_model(
        provider_id="lm_studio",
        model_id="primary",
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content=result.assistant_content,
    )
    GroundedSendCompletionRepository(database).complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=result.receipt_payload_json,
    )
    assert recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.COMPLETE

    database.connection.execute(
        "DELETE FROM grounded_provider_results WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )
    status = recovery.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedRecoveryState.CONFLICT
    assert status.receipt is None
    database.stop()
