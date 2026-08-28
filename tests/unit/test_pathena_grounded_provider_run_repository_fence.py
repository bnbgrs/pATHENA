from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptConflictError
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import (
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID) -> ChatRequestFingerprint:
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


def _model_info() -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="model",
        display_name="model",
        model_type="llm",
        context_capacity=32768,
        quantization=None,
        loaded=True,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=4096,
    )


def _commit_seq(database: SQLiteDatabase, revision_id: uuid.UUID) -> int:
    row = database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.revision_id = ?
        """,
        (uuid_to_blob(revision_id),),
    ).fetchone()
    assert row is not None
    return int(row["commit_seq"])


def _ready_operation(
    tmp_path: Path,
) -> tuple[
    SQLiteDatabase,
    GroundedSendCoordinator,
    uuid.UUID,
    uuid.UUID,
    ChatRequestFingerprint,
    uuid.UUID,
]:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user_id = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user_id)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user_id,
        content="hello",
        fingerprint=fingerprint,
    )

    model_runs = ModelRunRepository(database)
    context_configuration = {
        "mode": "grounded",
        "embedding_model_id": "embed",
    }
    signature = model_runs.get_or_create_signature(
        model=_model_info(),
        generation_parameters={
            "max_output_tokens": 1024,
            "reasoning_mode": "off",
            "temperature": 0.3,
        },
        context_configuration=context_configuration,
    )
    package = ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2872,
            output_reserve=1024,
            safety_margin=200,
        ),
        sections=(
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
                revision_id=started.user_message.revision_id,
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
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1034,
        ),
        snapshot_commit_seq=_commit_seq(database, started.user_message.revision_id),
    )
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user_id,
        pipeline_version="test-v1",
        input_snapshot=package.run_snapshot(),
        configuration=context_configuration,
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=user_id,
    )
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    return (
        database,
        coordinator,
        operation_id,
        chat_id,
        fingerprint,
        run.processing_run_id,
    )


def test_low_level_result_rejects_unknown_run_when_context_is_pinned(
    tmp_path: Path,
) -> None:
    database, coordinator, operation_id, chat_id, fingerprint, valid_run_id = (
        _ready_operation(tmp_path)
    )
    try:
        unknown_run_id = uuid.uuid4()
        assert unknown_run_id != valid_run_id

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="Provider result conflicts with the pinned Grounded ProcessingRun",
        ):
            coordinator.provider_attempts.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=unknown_run_id,
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer"}',
                provider_id="lm_studio",
                model_id="model",
            )

        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.AMBIGUOUS
    finally:
        database.stop()


def test_low_level_result_accepts_exact_matching_run_when_context_is_pinned(
    tmp_path: Path,
) -> None:
    database, coordinator, operation_id, chat_id, fingerprint, run_id = (
        _ready_operation(tmp_path)
    )
    try:
        result = coordinator.provider_attempts.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="model",
        )

        assert result.processing_run_id == run_id
        assert coordinator.provider_attempts.load_result(operation_id) == result
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.RESULT_AVAILABLE
    finally:
        database.stop()
