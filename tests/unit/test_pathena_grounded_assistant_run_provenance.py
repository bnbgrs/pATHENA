from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_processing_run import (
    bind_grounded_processing_run,
    complete_grounded_processing_run,
)
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import (
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
    ChatSendOperationState,
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


def _model() -> ModelInfo:
    return ModelInfo(
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
    )


def _prepare_recorded_result(
    database: SQLiteDatabase,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, uuid.UUID, ChatRequestFingerprint]:
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:primary",
    )
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
    )
    user_message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )

    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=_model(),
        generation_parameters={
            "max_output_tokens": 1000,
            "temperature": 0.3,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    package = ContextPackageService.build_from_sections(
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
                content="grounded",
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
                revision_id=user_message.revision_id,
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
            context_tokens=0,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=1,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-test",
        prompt_template_version="1",
    )
    GroundedContextPackageRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=user,
    )

    provider = GroundedProviderAttemptRepository(database)
    provider.mark_started(
        operation_id=operation_id,
        chat_id=chat_id,
    )
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    )
    return chat_id, operation_id, model, run.processing_run_id, fingerprint


def test_assistant_commit_rejects_invalid_processing_run_provenance(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, model, run_id, _ = _prepare_recorded_result(database)
        other_user = ChatRepository(database).create_actor(actor_type="user")
        database.connection.execute(
            """
            UPDATE processing_runs
            SET trigger_actor_id = ?
            WHERE processing_run_id = ?
            """,
            (uuid_to_blob(other_user), uuid_to_blob(run_id)),
        )
        chats = ChatRepository(database)
        before = chats.load_chat(chat_id)

        with pytest.raises(
            ChatSendOperationConflictError,
            match="invalid ProcessingRun provenance",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=model,
                content="answer",
            )

        assert chats.load_chat(chat_id) == before
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.USER_COMMITTED
        assert database.connection.execute(
            """
            SELECT COUNT(*)
            FROM chat_messages
            WHERE chat_id = ? AND message_type = 'assistant'
            """,
            (uuid_to_blob(chat_id),),
        ).fetchone()[0] == 0
    finally:
        database.stop()


def test_restart_after_assistant_commit_completes_processing_run_once(
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chat_id, operation_id, model, run_id, fingerprint = _prepare_recorded_result(
        database
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    pending = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert pending.state is GroundedRecoveryState.FINALIZATION_REQUIRED
    assert ModelRunRepository(database).load_run(run_id).status == "running"
    assert len(ChatRepository(database).load_chat(chat_id).messages) == 2

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    try:
        recovery = GroundedSendRecovery(database)
        receipt = recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        complete = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

        assert complete.state is GroundedRecoveryState.COMPLETE
        assert complete.receipt == receipt
        run = ModelRunRepository(database).load_run(run_id)
        assert run.status == "succeeded"
        assert run.finished_at_us is not None
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
        assert recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ) == receipt
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
    finally:
        database.stop()


def test_restart_after_run_completion_finishes_receipt_without_duplicate(
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chat_id, operation_id, model, run_id, fingerprint = _prepare_recorded_result(
        database
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model,
        content="answer",
    )
    context_record = GroundedContextPackageRepository(database).load(operation_id)
    assert context_record is not None
    user_message = ChatRepository(database).load_chat(chat_id).messages[0]
    assert user_message.actor_id is not None
    complete_grounded_processing_run(
        database,
        processing_run_id=run_id,
        package=context_record.package,
        trigger_actor_id=user_message.actor_id,
    )
    assert ModelRunRepository(database).load_run(run_id).status == "succeeded"
    pending = GroundedSendRecovery(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert pending.state is GroundedRecoveryState.FINALIZATION_REQUIRED

    database.stop()
    database = SQLiteDatabase(path)
    database.start()
    try:
        recovery = GroundedSendRecovery(database)
        receipt = recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        complete = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

        assert complete.state is GroundedRecoveryState.COMPLETE
        assert complete.receipt == receipt
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.COMPLETE
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
        assert ModelRunRepository(database).load_run(run_id).status == "succeeded"
    finally:
        database.stop()


def test_assistant_commit_rejects_failed_processing_run(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat_id, operation_id, model, run_id, _ = _prepare_recorded_result(database)
        ModelRunRepository(database).finish_run(
            run_id,
            status="failed",
            error_detail="synthetic failure after provider result",
        )
        chats = ChatRepository(database)
        before = chats.load_chat(chat_id)

        with pytest.raises(
            ChatSendOperationConflictError,
            match="invalid ProcessingRun provenance",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=model,
                content="answer",
            )

        assert chats.load_chat(chat_id) == before
        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.USER_COMMITTED
    finally:
        database.stop()
