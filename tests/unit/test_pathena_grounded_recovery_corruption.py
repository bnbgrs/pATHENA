from __future__ import annotations

import uuid

from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
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


def test_recovery_inspect_classifies_provider_result_corruption_as_conflict(tmp_path) -> None:
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
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET assistant_content = ? WHERE operation_id = ?",
                ("tampered", uuid_to_blob(operation_id)),
            )

        status = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.provider_result is None
        assert status.provider_identity is None
    finally:
        database.stop()


def test_recovery_inspect_classifies_provider_attempt_identity_corruption_as_conflict(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        other_chat_id = chats.create_chat(actor_id=user)
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
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_attempts SET chat_id = ? WHERE operation_id = ?",
                (uuid_to_blob(other_chat_id), uuid_to_blob(operation_id)),
            )

        status = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.provider_result is None
        assert status.provider_identity is None
    finally:
        database.stop()
