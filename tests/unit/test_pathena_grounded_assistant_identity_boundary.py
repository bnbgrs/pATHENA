from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_send import GroundedAssistantCommitError, GroundedSendCoordinator
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationConflictError
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
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
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
        snapshot_commit_seq=_user_commit_seq(database, revision_id),
    )


def _prepared_result(database: SQLiteDatabase):
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
    package = _package(
        database,
        operation_id,
        message.revision_id,
        signature=signature,
    )
    GroundedContextPackageRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="assistant-identity-boundary-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"mode": "unified_local_chat"},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="assistant-identity-boundary-test",
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
    provider = GroundedProviderAttemptRepository(database)
    provider.claim_started(operation_id=operation_id, chat_id=chat_id)
    provider.store_result(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        assistant_content="answer",
        receipt_payload_json='{"assistant_text":"answer"}',
        provider_id="lm_studio",
        model_id="primary",
    )
    with database.write_transaction() as connection:
        connection.execute(
            "DELETE FROM grounded_provider_result_identities WHERE operation_id = ?",
            (uuid_to_blob(operation_id),),
        )
    return chats, user, chat_id, operation_id


def test_assistant_commit_rejects_missing_identity_for_pinned_context(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats, user, chat_id, operation_id = _prepared_result(database)

        with pytest.raises(
            GroundedAssistantCommitError,
            match="requires durable provider identity",
        ):
            GroundedSendCoordinator(database).commit_assistant(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=user,
                content="answer",
            )

        thread = chats.load_chat(chat_id)
        assert [item.content for item in thread.messages] == ["hello"]
    finally:
        database.stop()


def test_low_level_assistant_commit_rejects_missing_pinned_result_identity(
    tmp_path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats, user, chat_id, operation_id = _prepared_result(database)

        with pytest.raises(
            ChatSendOperationConflictError,
            match="requires durable provider result identity",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=user,
                content="answer",
            )

        thread = chats.load_chat(chat_id)
        assert [item.content for item in thread.messages] == ["hello"]
    finally:
        database.stop()
