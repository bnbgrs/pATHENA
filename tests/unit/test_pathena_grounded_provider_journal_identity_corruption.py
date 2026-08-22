from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptRepository,
    GroundedProviderAttemptSchemaError,
)
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


def _operation(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    other_chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    repository = GroundedProviderAttemptRepository(database)
    repository.mark_started(operation_id=operation_id, chat_id=chat_id)
    return repository, chat_id, other_chat_id, operation_id


def test_load_attempt_rejects_chat_identity_corruption(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        repository, _chat_id, other_chat_id, operation_id = _operation(database)
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_attempts SET chat_id = ? WHERE operation_id = ?",
                (uuid_to_blob(other_chat_id), uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedProviderAttemptSchemaError,
            match="Grounded operation",
        ):
            repository.load(operation_id)
    finally:
        database.stop()


def test_load_result_rejects_chat_identity_corruption(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        repository, chat_id, other_chat_id, operation_id = _operation(database)
        repository.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=uuid.uuid4(),
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="primary",
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET chat_id = ? WHERE operation_id = ?",
                (uuid_to_blob(other_chat_id), uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedProviderAttemptSchemaError,
            match="Grounded operation",
        ):
            repository.load_result(operation_id)
    finally:
        database.stop()
