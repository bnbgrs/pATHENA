from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptConflictError
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedProviderBoundaryError, GroundedSendCoordinator
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
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
        requested_model_id="model",
        requested_embedding_model_id="embed",
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
    )


def _user_commit_seq(database: SQLiteDatabase, revision_id: uuid.UUID) -> int:
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


def _package(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    *,
    signature: ModelSignature,
):
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1024,
            safety_margin=176,
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
        snapshot_commit_seq=_user_commit_seq(database, revision_id),
    )


def _pin_context_and_run(
    database: SQLiteDatabase,
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    revision_id: uuid.UUID,
    trigger_actor_id: uuid.UUID,
) -> None:
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=ModelInfo(
            provider="lm_studio",
            backend_model_id="model",
            display_name="model",
            model_type="llm",
            context_capacity=32768,
            quantization="Q4_K_M",
            loaded=True,
            vision=False,
            trained_for_tool_use=False,
            loaded_context_length=4096,
        ),
        generation_parameters={
            "max_output_tokens": 1024,
            "reasoning_mode": "off",
            "temperature": 0.3,
        },
        context_configuration={"embedding_model_id": "embed", "max_items": 4},
    )
    package = _package(
        database,
        operation_id,
        revision_id,
        signature=signature,
    )
    GroundedContextPackageRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=trigger_actor_id,
        pipeline_version="provider-attempt-claim-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"embedding_model_id": "embed", "max_items": 4},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="provider-attempt-claim-test",
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


def _started_operation(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    _pin_context_and_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        revision_id=message.revision_id,
        trigger_actor_id=user,
    )
    return GroundedSendCoordinator(database), operation_id, chat_id, fingerprint


def test_provider_attempt_claim_is_single_owner(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, operation_id, chat_id, _ = _started_operation(database)
        first = coordinator.provider_attempts.claim_started(
            operation_id=operation_id,
            chat_id=chat_id,
        )

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="already been claimed",
        ):
            coordinator.provider_attempts.claim_started(
                operation_id=operation_id,
                chat_id=chat_id,
            )

        assert coordinator.provider_attempts.mark_started(
            operation_id=operation_id,
            chat_id=chat_id,
        ) == first
    finally:
        database.stop()


def test_stale_resumable_precheck_cannot_reclaim_provider_boundary(
    tmp_path,
    monkeypatch,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        first, operation_id, chat_id, fingerprint = _started_operation(database)
        contender = GroundedSendCoordinator(database)
        stale = contender.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert stale.state is GroundedRecoveryState.RESUMABLE

        first.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        current = contender.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert current.state is GroundedRecoveryState.AMBIGUOUS

        recoveries = iter((stale, current))
        monkeypatch.setattr(contender, "recover", lambda **_: next(recoveries))

        with pytest.raises(GroundedProviderBoundaryError) as exc_info:
            contender.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS
        assert contender.provider_attempts.load(operation_id) is not None
    finally:
        database.stop()
