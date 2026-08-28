from __future__ import annotations

import json
import uuid
from collections.abc import Iterator, Sequence

import pytest

from athena.chat.durable_grounded_generation import (
    DurableGroundedGenerationError,
    DurableGroundedGenerationService,
)
from athena.chat.generation import ChatGenerationService
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.model.domain import ModelChatMessage, ModelInfo, ProviderHealth, ProviderHealthStatus
from athena.model.provenance import ModelRunRepository, ModelSignature
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
        yield "answer"


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


def _package(user_message, signature: ModelSignature):
    context = ContextBuilderService().build_from_ranked(
        query="hello",
        results=(),
        max_estimated_tokens=300,
    )
    return ContextPackageService.build(
        model_signature=signature,
        context=context,
        system_text="system",
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
        snapshot_commit_seq=1,
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )


def _receipt(content: str, provider_id: str, model_id: str) -> str:
    return json.dumps(
        {
            "assistant_text": content,
            "provider_id": provider_id,
            "model_id": model_id,
        }
    )


def _prepared_generation(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
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
    provider = _Provider()
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=provider.discover_models()[0],
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    package = _package(started.user_message, signature)
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="durable-grounded-provider-hook-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="durable-grounded-provider-hook",
        prompt_template_version="1",
    )
    generation = DurableGroundedGenerationService(
        ChatGenerationService(ChatService(chats), provider),
        coordinator,
    )
    return (
        chats,
        chat_id,
        operation_id,
        fingerprint,
        coordinator,
        started,
        package,
        run.processing_run_id,
        provider,
        generation,
    )


def test_provider_hook_failure_does_not_claim_irreversible_boundary(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        (
            chats,
            chat_id,
            operation_id,
            fingerprint,
            coordinator,
            started,
            package,
            processing_run_id,
            provider,
            generation,
        ) = _prepared_generation(database)

        def fail_before_provider() -> None:
            raise RuntimeError("hook failure")

        with pytest.raises(RuntimeError, match="hook failure"):
            generation.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=started.user_message,
                context_package=package,
                processing_run_id=processing_run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=_receipt,
                on_before_provider_call=fail_before_provider,
            )

        assert provider.calls == 0
        assert coordinator.load_context_package(operation_id) is not None
        assert coordinator.provider_attempts.load(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.RESUMABLE

        result = generation.send_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            user_message=started.user_message,
            context_package=package,
            processing_run_id=processing_run_id,
            fingerprint=fingerprint,
            receipt_payload_builder=_receipt,
        )
        assert provider.calls == 1
        assert result.assistant_message.content == "answer"
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.FINALIZATION_REQUIRED
        assert [item.content for item in chats.load_chat(chat_id).messages] == [
            "hello",
            "answer",
        ]
    finally:
        database.stop()


def test_receipt_builder_failure_journals_provider_answer_for_recovery(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        (
            chats,
            chat_id,
            operation_id,
            fingerprint,
            coordinator,
            started,
            package,
            processing_run_id,
            provider,
            generation,
        ) = _prepared_generation(database)

        def broken_receipt_builder(
            content: str,
            provider_id: str,
            model_id: str,
        ) -> str:
            del content, provider_id, model_id
            raise RuntimeError("receipt exploded")

        with pytest.raises(
            DurableGroundedGenerationError,
            match="answer was journaled for recovery",
        ):
            generation.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=started.user_message,
                context_package=package,
                processing_run_id=processing_run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=broken_receipt_builder,
            )

        assert provider.calls == 1
        status = coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.RESULT_AVAILABLE
        assert status.provider_result is not None
        assert status.provider_result.assistant_content == "answer"
        assert status.provider_result.processing_run_id == processing_run_id
        assert json.loads(status.provider_result.receipt_payload_json) == {
            "assistant_text": "answer",
            "model_id": "primary",
            "provider_id": "lm_studio",
            "recovery_receipt": True,
        }
        assert [item.content for item in chats.load_chat(chat_id).messages] == ["hello"]

        receipt = coordinator.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert receipt.processing_run_id == processing_run_id
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.COMPLETE
        assert [item.content for item in chats.load_chat(chat_id).messages] == [
            "hello",
            "answer",
        ]
    finally:
        database.stop()
