from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptConflictError,
    GroundedProviderAttemptRepository,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
)
from athena.chat.service import ChatService
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


def _prepare_grounded_attempt(
    database: SQLiteDatabase,
) -> tuple[uuid.UUID, uuid.UUID, GroundedProviderAttemptRepository]:
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
    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(operation_id=operation_id, chat_id=chat_id)
    return operation_id, chat_id, provider


def test_provider_result_run_conflict_rolls_back_before_persistence(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, provider = _prepare_grounded_attempt(database)
        pinned_run_id = uuid.uuid4()
        result_run_id = uuid.uuid4()
        ChatSendOperationRepository(database).bind_grounded_processing_run(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=pinned_run_id,
        )

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="pinned Grounded ProcessingRun",
        ):
            provider.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=result_run_id,
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
                provider_id="lm_studio",
                model_id="primary",
            )

        row = database.connection.execute(
            "SELECT 1 FROM grounded_provider_results WHERE operation_id = ?",
            (uuid_to_blob(operation_id),),
        ).fetchone()
        assert row is None
        assert provider.load_result(operation_id) is None
    finally:
        database.stop()


def test_existing_provider_result_replay_rejects_legacy_run_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, provider = _prepare_grounded_attempt(database)
        result_run_id = uuid.uuid4()
        provider.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result_run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
            provider_id="lm_studio",
            model_id="primary",
        )

        conflicting_run_id = uuid.uuid4()
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE chat_send_operations
                SET processing_run_id = ?
                WHERE operation_id = ?
                """,
                (
                    uuid_to_blob(conflicting_run_id),
                    uuid_to_blob(operation_id),
                ),
            )

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="pinned Grounded ProcessingRun",
        ):
            provider.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=result_run_id,
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
                provider_id="lm_studio",
                model_id="primary",
            )
    finally:
        database.stop()


def test_run_binding_rejects_recorded_provider_result_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, provider = _prepare_grounded_attempt(database)
        result_run_id = uuid.uuid4()
        provider.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result_run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
            provider_id="lm_studio",
            model_id="primary",
        )

        operations = ChatSendOperationRepository(database)
        with pytest.raises(
            ChatSendOperationConflictError,
            match="recorded provider result",
        ):
            operations.bind_grounded_processing_run(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=uuid.uuid4(),
            )

        operation = operations.load(operation_id)
        assert operation is not None
        assert operation.processing_run_id is None

        bound = operations.bind_grounded_processing_run(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result_run_id,
        )
        assert bound.processing_run_id == result_run_id
        stored = provider.load_result(operation_id)
        assert stored is not None
        assert stored.processing_run_id == result_run_id
    finally:
        database.stop()


def test_assistant_commit_rejects_legacy_provider_result_run_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, provider = _prepare_grounded_attempt(database)
        result_run_id = uuid.uuid4()
        provider.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result_run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
            provider_id="lm_studio",
            model_id="primary",
        )
        conflicting_run_id = uuid.uuid4()
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE chat_send_operations
                SET processing_run_id = ?
                WHERE operation_id = ?
                """,
                (
                    uuid_to_blob(conflicting_run_id),
                    uuid_to_blob(operation_id),
                ),
            )

        actor_id = ChatService(ChatRepository(database)).ensure_primary_model(
            provider_id="lm_studio",
            model_id="primary",
        )
        with pytest.raises(
            ChatSendOperationConflictError,
            match="operation-pinned ProcessingRun",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=actor_id,
                content="answer",
            )

        assistant_id = assistant_message_id_for_operation(operation_id)
        assistant = database.connection.execute(
            "SELECT 1 FROM chat_messages WHERE message_id = ?",
            (uuid_to_blob(assistant_id),),
        ).fetchone()
        assert assistant is None
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state.value == "user_committed"
    finally:
        database.stop()
