from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_context_package import (
    GroundedContextPackageConflictError,
    GroundedContextPackageRepository,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _package(operation_id: uuid.UUID, revision_id: uuid.UUID):
    signature = ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization="Q4_K_M",
        generation_parameters_json='{"max_output_tokens":1000,"reasoning_mode":"off"}',
        context_configuration_json='{"mode":"unified_local_chat"}',
        signature_hash=b"s" * 32,
        created_at_us=1,
    )
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="system",
                role="system",
                content="exact durable evidence",
                included_ref_ids=(),
            ),
            ContextSection(
                name="current_user",
                role="user",
                content="hello",
                included_ref_ids=("CURRENT-USER",),
            ),
        ),
        included_refs=(
            ContextIncludedRef(
                ref_id="CURRENT-USER",
                entity_type="chat_message",
                entity_id=operation_id,
                revision_id=revision_id,
            ),
        ),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=0,
            conversation_included_count=0,
            conversation_excluded_count=0,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=10,
            context_tokens=10,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=1,
    )


def _fingerprint(chat_id: uuid.UUID):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
    )


def test_exact_grounded_context_package_survives_restart(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    package = _package(operation_id, message.revision_id)
    repository = GroundedContextPackageRepository(database)
    stored = repository.store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    assert repository.store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    ) == stored
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    recovered = GroundedContextPackageRepository(database).load(operation_id)
    assert recovered is not None
    assert recovered.payload_sha256 == stored.payload_sha256
    assert recovered.package == package
    assert recovered.package.model_messages() == package.model_messages()
    database.stop()


def test_grounded_context_package_rejects_other_current_user(tmp_path) -> None:
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
    with pytest.raises(GroundedContextPackageConflictError):
        GroundedContextPackageRepository(database).store(
            operation_id=operation_id,
            chat_id=chat_id,
            package=_package(uuid.uuid4(), uuid.uuid4()),
        )
    database.stop()
