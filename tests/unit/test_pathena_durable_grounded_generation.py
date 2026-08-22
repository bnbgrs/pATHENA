from __future__ import annotations

import json
import uuid
from collections.abc import Iterator, Sequence

import pytest

from athena.chat.durable_grounded_generation import DurableGroundedGenerationService
from athena.chat.generation import ChatGenerationService
from athena.chat.grounding import GroundingContract
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_send import GroundedProviderBoundaryError, GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.model.domain import ModelChatMessage, ModelInfo, ProviderHealth, ProviderHealthStatus
from athena.model.provenance import ModelSignature
from athena.retrieval.context import ContextBuilderService
from athena.retrieval.context_package import (
    ContextPackageBudget,
    ContextPackageService,
    ContextTokenEstimates,
)
from athena.storage.database import SQLiteDatabase


class _Provider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.calls = 0

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (
            ModelInfo(
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
        )

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
    ) -> Iterator[str]:
        del messages
        assert model_id == "primary"
        assert max_output_tokens == 1000
        assert reasoning_mode == "off"
        self.calls += 1
        yield "durable answer"


def _package(user_message, *, snapshot_commit_seq: int):
    context = ContextBuilderService().build_from_ranked(
        query=user_message.content or "request",
        results=(),
        max_estimated_tokens=300,
    )
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
    return ContextPackageService.build(
        model_signature=signature,
        context=context,
        system_text="PACKAGE SYSTEM",
        prior_messages=(),
        current_user_message=user_message,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=300,
            output_reserve=1000,
            safety_margin=200,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=10,
            context_tokens=context.estimated_tokens,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=snapshot_commit_seq,
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )


def test_provider_result_survives_restart_and_finalizes_without_replay(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
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
        package = _package(started.user_message, snapshot_commit_seq=1)
        provider = _Provider()
        generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(chats), provider),
            coordinator,
        )
        run_id = uuid.uuid4()

        result = generation.send_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            user_message=started.user_message,
            context_package=package,
            processing_run_id=run_id,
            fingerprint=fingerprint,
            receipt_payload_builder=lambda content, provider_id, model_id: json.dumps(
                {
                    "assistant_text": content,
                    "provider_id": provider_id,
                    "model_id": model_id,
                }
            ),
        )

        assert provider.calls == 1
        assert result.assistant_message.content == "durable answer"
        recorded = coordinator.provider_attempts.load_result(operation_id)
        assert recorded is not None
        assert recorded.processing_run_id == run_id
        assert recorded.assistant_content == "durable answer"
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.FINALIZATION_REQUIRED
        assert len(chats.load_chat(chat_id).messages) == 2

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        recovery = GroundedSendRecovery(database)
        pending = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert pending.state is GroundedRecoveryState.FINALIZATION_REQUIRED
        assert pending.provider_result is not None
        assert pending.provider_result.assistant_content == "durable answer"
        assert pending.provider_identity is not None
        assert pending.provider_identity.provider_id == "lm_studio"
        assert pending.provider_identity.model_id == "primary"

        receipt = recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert provider.calls == 1
        complete = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert complete.state is GroundedRecoveryState.COMPLETE
        assert complete.receipt == receipt
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        restarted_complete = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert restarted_complete.state is GroundedRecoveryState.COMPLETE
        assert restarted_complete.receipt == receipt
        assert provider.calls == 1
    finally:
        database.stop()


def test_grounding_retry_is_fenced_before_second_provider_call(tmp_path) -> None:
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
        package = _package(started.user_message, snapshot_commit_seq=1)
        provider = _Provider()
        generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(chats), provider),
            coordinator,
        )
        before_provider_calls = 0

        def on_before_provider_call() -> None:
            nonlocal before_provider_calls
            before_provider_calls += 1

        with pytest.raises(GroundedProviderBoundaryError) as exc_info:
            generation.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=started.user_message,
                context_package=package,
                processing_run_id=uuid.uuid4(),
                fingerprint=fingerprint,
                receipt_payload_builder=lambda content, provider_id, model_id: json.dumps(
                    {
                        "assistant_text": content,
                        "provider_id": provider_id,
                        "model_id": model_id,
                    }
                ),
                grounding_contract=GroundingContract(
                    evidence_refs=(),
                    allow_model_prior=False,
                    require_provenance_markers=True,
                ),
                on_before_provider_call=on_before_provider_call,
            )

        assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS
        assert provider.calls == 1
        assert before_provider_calls == 1
        assert coordinator.provider_attempts.load(operation_id) is not None
        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.AMBIGUOUS
        assert len(chats.load_chat(chat_id).messages) == 1
    finally:
        database.stop()
