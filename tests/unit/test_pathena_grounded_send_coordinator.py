from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_reconciliation import GroundedReconciliationState
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import (
    GroundedAssistantCommitError,
    GroundedCompletionCommitError,
    GroundedProviderBoundaryError,
    GroundedProviderContextError,
    GroundedProviderRunError,
    GroundedSendCoordinator,
    GroundedSendStateError,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
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


def _setup(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:model",
    )
    chat_id = chats.create_chat(actor_id=user)
    return chats, user, model, chat_id


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


def _context_package(
    signature: ModelSignature,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    *,
    snapshot_commit_seq: int,
) -> ContextPackage:
    return ContextPackageService.build_from_sections(
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
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1034,
        ),
        snapshot_commit_seq=snapshot_commit_seq,
    )


def _store_context_and_run(
    coordinator: GroundedSendCoordinator,
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    revision_id: uuid.UUID,
    trigger_actor_id: uuid.UUID,
) -> uuid.UUID:
    commit_row = coordinator.database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.entity_id = ? AND r.revision_id = ?
        """,
        (uuid_to_blob(operation_id), uuid_to_blob(revision_id)),
    ).fetchone()
    assert commit_row is not None

    model_runs = ModelRunRepository(coordinator.database)
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
    package = _context_package(
        signature,
        operation_id,
        revision_id,
        snapshot_commit_seq=int(commit_row["commit_seq"]),
    )
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=trigger_actor_id,
        pipeline_version="test-v1",
        input_snapshot=package.run_snapshot(),
        configuration=context_configuration,
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        coordinator.database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    return run.processing_run_id


def test_crash_boundaries_reconcile_without_reexecution(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats, user, model, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)

    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.ABSENT

    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    assert started.status.state is GroundedReconciliationState.INCOMPLETE
    assert len(chats.load_chat(chat_id).messages) == 1
    run_id = _store_context_and_run(
        coordinator,
        operation_id=operation_id,
        chat_id=chat_id,
        revision_id=started.user_message.revision_id,
        trigger_actor_id=user,
    )

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    coordinator = GroundedSendCoordinator(database)
    assert coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE
    with pytest.raises(GroundedSendStateError):
        coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )

    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESUMABLE
    attempt = coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert attempt.operation_id == operation_id
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.AMBIGUOUS
    with pytest.raises(GroundedProviderBoundaryError) as exc_info:
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
    assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS

    result = coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":["CTX-001"]}',
        provider_id="lm_studio",
        model_id="model",
    )
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESULT_AVAILABLE

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    coordinator = GroundedSendCoordinator(database)
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESULT_AVAILABLE

    receipt = coordinator.finalize_recorded_result(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        fingerprint=fingerprint,
    )
    assert receipt.payload_json == result.receipt_payload_json
    complete = coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert complete.state is GroundedReconciliationState.COMPLETE
    assert complete.receipt == receipt

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    replay = GroundedSendCoordinator(database).reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert replay.state is GroundedReconciliationState.COMPLETE
    assert replay.receipt is not None
    assert replay.receipt.payload_json == receipt.payload_json
    assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
    database.stop()


def test_provider_attempt_requires_durable_context_package(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, user, _, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)
    coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )

    with pytest.raises(GroundedProviderContextError, match="durable ContextPackage"):
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

    assert coordinator.provider_attempts.load(operation_id) is None
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.RESUMABLE
    database.stop()


def test_provider_result_rejects_receipt_assistant_text_mismatch(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, user, _, chat_id = _setup(database)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        coordinator = GroundedSendCoordinator(database)
        started = coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        run_id = _store_context_and_run(
            coordinator,
            operation_id=operation_id,
            chat_id=chat_id,
            revision_id=started.user_message.revision_id,
            trigger_actor_id=user,
        )
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

        with pytest.raises(ValueError, match="must match assistant content exactly"):
            coordinator.record_provider_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                processing_run_id=run_id,
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"different"}',
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


def test_provider_result_rejects_unknown_processing_run(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, user, _, chat_id = _setup(database)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        coordinator = GroundedSendCoordinator(database)
        started = coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        _store_context_and_run(
            coordinator,
            operation_id=operation_id,
            chat_id=chat_id,
            revision_id=started.user_message.revision_id,
            trigger_actor_id=user,
        )
        coordinator.begin_provider_attempt(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

        with pytest.raises(GroundedProviderRunError, match="ProcessingRun"):
            coordinator.record_provider_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                processing_run_id=uuid.uuid4(),
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


def test_same_operation_different_request_is_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, user, _, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    coordinator = GroundedSendCoordinator(database)
    coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    conflict = coordinator.reconcile(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=_fingerprint(chat_id, "different"),
    )
    assert conflict.state is GroundedReconciliationState.CONFLICT
    with pytest.raises(GroundedSendStateError) as exc_info:
        coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="different",
            fingerprint=_fingerprint(chat_id, "different"),
        )
    assert exc_info.value.status.state is GroundedReconciliationState.CONFLICT
    database.stop()


def test_assistant_commit_requires_recorded_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, user, model, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    coordinator = GroundedSendCoordinator(database)
    coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )

    with pytest.raises(GroundedAssistantCommitError):
        coordinator.commit_assistant(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=model,
            content="answer",
        )

    assert len(ChatRepository(database).load_chat(chat_id).messages) == 1
    database.stop()


def test_completion_requires_exact_recorded_provider_result(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    _, user, model, chat_id = _setup(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    run_id = _store_context_and_run(
        coordinator,
        operation_id=operation_id,
        chat_id=chat_id,
        revision_id=started.user_message.revision_id,
        trigger_actor_id=user,
    )
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    result = coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer","evidence":[]}',
        provider_id="lm_studio",
        model_id="model",
    )
    coordinator.commit_assistant(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content=result.assistant_content,
    )

    with pytest.raises(GroundedCompletionCommitError):
        coordinator.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=uuid.uuid4(),
            payload_json=result.receipt_payload_json,
        )
    with pytest.raises(GroundedCompletionCommitError):
        coordinator.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json='{"assistant_text":"different"}',
        )

    receipt = coordinator.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=result.receipt_payload_json,
    )
    assert receipt.processing_run_id == run_id
    assert coordinator.recover(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedRecoveryState.COMPLETE
    database.stop()
