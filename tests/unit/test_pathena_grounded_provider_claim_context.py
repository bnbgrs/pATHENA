from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptConflictError,
    GroundedProviderAttemptRepository,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


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


def _package(
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    *,
    signature: ModelSignature | None = None,
):
    if signature is None:
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
                content="durable evidence",
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


def _operation(database: SQLiteDatabase):
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
    return chat_id, operation_id, message.revision_id, user


def _pin_context_and_run(
    database: SQLiteDatabase,
    *,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    trigger_actor_id: uuid.UUID,
) -> None:
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=ModelInfo(
            provider="lm_studio",
            backend_model_id="primary",
            display_name="primary",
            model_type="llm",
            context_capacity=32768,
            quantization="Q4_K_M",
            loaded=True,
            vision=False,
            trained_for_tool_use=False,
            loaded_context_length=4096,
        ),
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"mode": "unified_local_chat"},
    )
    package = _package(operation_id, revision_id, signature=signature)
    GroundedContextPackageRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=trigger_actor_id,
        pipeline_version="provider-claim-context-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"mode": "unified_local_chat"},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="provider-claim-context-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )


def test_exclusive_provider_claim_requires_pinned_processing_run(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, _, _ = _operation(database)
        repository = GroundedProviderAttemptRepository(database)

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="requires a pinned Grounded ProcessingRun",
        ):
            repository.claim_started(operation_id=operation_id, chat_id=chat_id)

        assert repository.load(operation_id) is None
    finally:
        database.stop()


def test_legacy_mark_started_remains_compatible_without_context_package(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, _, _ = _operation(database)
        repository = GroundedProviderAttemptRepository(database)

        attempt = repository.mark_started(operation_id=operation_id, chat_id=chat_id)

        assert attempt.operation_id == operation_id
        assert attempt.chat_id == chat_id
    finally:
        database.stop()


def test_exclusive_provider_claim_succeeds_after_context_and_run_are_pinned(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, revision_id, user = _operation(database)
        _pin_context_and_run(
            database,
            chat_id=chat_id,
            operation_id=operation_id,
            revision_id=revision_id,
            trigger_actor_id=user,
        )
        repository = GroundedProviderAttemptRepository(database)

        attempt = repository.claim_started(operation_id=operation_id, chat_id=chat_id)

        assert attempt.operation_id == operation_id
        assert attempt.chat_id == chat_id
    finally:
        database.stop()
