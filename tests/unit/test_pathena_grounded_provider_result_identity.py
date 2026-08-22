from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptConflictError,
    GroundedProviderAttemptRepository,
)
from athena.chat.grounded_provider_result_contract import GroundedProviderResultContractError
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
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
        requested_model_id="model",
        requested_embedding_model_id="embed",
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
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
    return database, repository, chat_id, operation_id


def test_provider_result_identity_is_atomic_and_immutable(tmp_path: Path) -> None:
    database, repository, chat_id, operation_id = _repository(tmp_path)
    run_id = uuid.uuid4()
    result = repository.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    )
    assert repository.load_result(operation_id) == result
    identity = repository.load_result_identity(operation_id)
    assert identity is not None
    assert identity.provider_id == "lm_studio"
    assert identity.model_id == "primary"

    assert repository.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    ) == result

    with pytest.raises(GroundedProviderAttemptConflictError):
        repository.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="other",
            model_id="primary",
        )
    database.stop()


def test_legacy_provider_result_cannot_gain_identity_on_replay(tmp_path: Path) -> None:
    database, repository, chat_id, operation_id = _repository(tmp_path)
    run_id = uuid.uuid4()
    result = repository.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
    )
    assert repository.load_result_identity(operation_id) is None
    assert repository.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
    ) == result

    with pytest.raises(GroundedProviderAttemptConflictError):
        repository.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="primary",
        )

    assert repository.load_result(operation_id) == result
    assert repository.load_result_identity(operation_id) is None
    database.stop()


def test_provider_result_repository_rejects_receipt_content_mismatch(
    tmp_path: Path,
) -> None:
    database, repository, chat_id, operation_id = _repository(tmp_path)
    try:
        with pytest.raises(
            GroundedProviderResultContractError,
            match="must match assistant content exactly",
        ):
            repository.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=uuid.uuid4(),
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"different"}',
            )

        assert repository.load_result(operation_id) is None
        assert repository.load_result_identity(operation_id) is None
    finally:
        database.stop()