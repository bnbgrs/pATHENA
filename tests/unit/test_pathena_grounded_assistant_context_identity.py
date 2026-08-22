from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
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
        context_configuration_json='{"context_package_version":1}',
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
        snapshot_commit_seq=1,
    )


def test_assistant_commit_rejects_identity_tampered_against_context_model(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
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
        coordinator.store_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            package=_package(operation_id, started.user_message.revision_id),
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
            processing_run_id=uuid.uuid4(),
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="primary",
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
        tampered_actor = ChatService(chats).ensure_primary_model(
            provider_id="tampered_provider",
            model_id="primary",
        )

        with pytest.raises(
            ChatSendOperationConflictError,
            match="pinned ContextPackage model",
        ):
            GroundedAssistantTurnRepository(database).commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=tampered_actor,
                content="answer",
            )

        operation = ChatSendOperationRepository(database).load(operation_id)
        assert operation is not None
        assert operation.state is ChatSendOperationState.USER_COMMITTED
        assert len(chats.load_chat(chat_id).messages) == 1
    finally:
        database.stop()
