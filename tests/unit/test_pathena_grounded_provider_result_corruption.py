from __future__ import annotations

import uuid
from pathlib import Path

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


def _repository(
    tmp_path: Path,
) -> tuple[SQLiteDatabase, GroundedProviderAttemptRepository, uuid.UUID, uuid.UUID]:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
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
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    repository = GroundedProviderAttemptRepository(database)
    repository.mark_started(operation_id=operation_id, chat_id=chat_id)
    repository.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=uuid.uuid4(),
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    )
    return database, repository, chat_id, operation_id


def test_load_result_rejects_semantic_corruption_with_valid_receipt_checksum(
    tmp_path: Path,
) -> None:
    database, repository, _chat_id, operation_id = _repository(tmp_path)
    try:
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET assistant_content = ? WHERE operation_id = ?",
                ("tampered", uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedProviderAttemptSchemaError,
            match="durable receipt contract",
        ):
            repository.load_result(operation_id)
    finally:
        database.stop()


def test_load_result_normalizes_malformed_receipt_to_schema_corruption(
    tmp_path: Path,
) -> None:
    database, repository, _chat_id, operation_id = _repository(tmp_path)
    try:
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_provider_results SET receipt_payload_json = ? WHERE operation_id = ?",
                ("{bad", uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedProviderAttemptSchemaError,
            match="durable receipt contract",
        ):
            repository.load_result(operation_id)
    finally:
        database.stop()
