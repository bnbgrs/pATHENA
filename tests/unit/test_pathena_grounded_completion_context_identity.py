from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import (
    GroundedSendCompletionConflictError,
    GroundedSendCompletionCorruptionError,
    GroundedSendCompletionRepository,
)
from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.chat.service import ChatService
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


def _signature(database: SQLiteDatabase) -> ModelSignature:
    return ModelRunRepository(database).get_or_create_signature(
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
        context_configuration={"context_package_version": 1},
    )


def _package(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
):
    signature = _signature(database)
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
            estimated_total_tokens=1210,
        ),
        snapshot_commit_seq=_user_commit_seq(database, revision_id),
    )


def _assistant_committed(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    payload = '{"assistant_text":"answer"}'
    fingerprint = build_chat_request_fingerprint(
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
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    package = _package(database, operation_id, started.user_message.revision_id)
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = ModelRunRepository(database).start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="completion-context-identity-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=package.model_signature.model_signature_id,
        prompt_template_id="completion-context-identity-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=user,
    )
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=run.processing_run_id,
        assistant_content="answer",
        receipt_payload_json=payload,
        provider_id="lm_studio",
        model_id="primary",
    )
    model_actor = ChatService(chats).ensure_primary_model(
        provider_id="lm_studio",
        model_id="primary",
    )
    GroundedAssistantTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model_actor,
        content="answer",
    )
    return chats, chat_id, operation_id, run.processing_run_id, payload


def test_completion_rejects_identity_tampered_against_context_model(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, chat_id, operation_id, run_id, payload = _assistant_committed(database)
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE grounded_provider_result_identities
                SET provider_id = ?
                WHERE operation_id = ?
                """,
                ("tampered_provider", uuid_to_blob(operation_id)),
            )

        completions = GroundedSendCompletionRepository(database)
        with pytest.raises(
            GroundedSendCompletionConflictError,
            match="pinned ContextPackage model",
        ):
            completions.complete(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=run_id,
                payload_json=payload,
            )

        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.ASSISTANT_COMMITTED
        assert completions.load(operation_id) is None
    finally:
        database.stop()


def test_completion_load_rejects_identity_tampered_after_completion(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, chat_id, operation_id, run_id, payload = _assistant_committed(database)
        completions = GroundedSendCompletionRepository(database)
        completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE grounded_provider_result_identities
                SET provider_id = ?
                WHERE operation_id = ?
                """,
                ("tampered_provider", uuid_to_blob(operation_id)),
            )

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="pinned ContextPackage model",
        ):
            completions.load(operation_id)
    finally:
        database.stop()
