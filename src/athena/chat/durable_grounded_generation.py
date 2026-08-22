"""Crash-safe adapter between ContextPackage generation and Grounded persistence."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from athena.chat.generation import ChatGenerationResult, ChatGenerationService
from athena.chat.grounding import GroundingContract
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.service import ChatService
from athena.retrieval.context_package import ContextPackage

ReceiptPayloadBuilder = Callable[[str, str, str], str]


class DurableGroundedGenerationError(RuntimeError):
    """Generation attempted to escape the durable Grounded operation boundary."""


class _DurableAssistantChatService(ChatService):
    def __init__(
        self,
        base: ChatService,
        *,
        coordinator: GroundedSendCoordinator,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
        receipt_payload_builder: ReceiptPayloadBuilder,
    ) -> None:
        super().__init__(base.repository)
        self._coordinator = coordinator
        self._operation_id = operation_id
        self._chat_id = chat_id
        self._processing_run_id = processing_run_id
        self._fingerprint = fingerprint
        self._receipt_payload_builder = receipt_payload_builder

    def add_assistant_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        provider_id: str,
        model_id: str,
        operation_id: uuid.UUID | None = None,
    ) -> ChatMessage:
        if chat_id != self._chat_id or operation_id != self._operation_id:
            raise DurableGroundedGenerationError(
                "Generated assistant persistence escaped its Grounded operation identity."
            )

        payload_json = self._receipt_payload_builder(
            content,
            provider_id,
            model_id,
        )
        result = self._coordinator.record_provider_result(
            operation_id=self._operation_id,
            chat_id=self._chat_id,
            fingerprint=self._fingerprint,
            processing_run_id=self._processing_run_id,
            assistant_content=content,
            receipt_payload_json=payload_json,
            provider_id=provider_id,
            model_id=model_id,
        )
        actor_id = self.ensure_primary_model(
            provider_id=provider_id,
            model_id=model_id,
        )
        return self._coordinator.commit_assistant(
            operation_id=self._operation_id,
            chat_id=self._chat_id,
            actor_id=actor_id,
            content=result.assistant_content,
        )


class DurableGroundedGenerationService:
    """Run a ContextPackage with durable provider-boundary persistence."""

    def __init__(
        self,
        generation: ChatGenerationService,
        coordinator: GroundedSendCoordinator,
    ) -> None:
        self.generation = generation
        self.coordinator = coordinator

    def send_context_package(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        user_message: ChatMessage,
        context_package: ContextPackage,
        processing_run_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
        receipt_payload_builder: ReceiptPayloadBuilder,
        on_delta: Callable[[str], None] | None = None,
        grounding_contract: GroundingContract | None = None,
        on_before_provider_call: Callable[[], None] | None = None,
    ) -> ChatGenerationResult:
        if user_message.message_id != operation_id:
            raise DurableGroundedGenerationError(
                "Grounded generation user message must equal the operation identity."
            )

        durable_chat = _DurableAssistantChatService(
            self.generation.chat,
            coordinator=self.coordinator,
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            fingerprint=fingerprint,
            receipt_payload_builder=receipt_payload_builder,
        )
        delegated = ChatGenerationService(
            durable_chat,
            self.generation.provider,
            interactive_demand=self.generation.interactive_demand,
        )

        def before_provider() -> None:
            self.coordinator.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
            if on_before_provider_call is not None:
                on_before_provider_call()

        result = delegated.send_context_package(
            chat_id=chat_id,
            user_message=user_message,
            context_package=context_package,
            operation_id=operation_id,
            on_delta=None,
            grounding_contract=grounding_contract,
            on_before_provider_call=before_provider,
        )
        if on_delta is not None:
            persisted_content = result.assistant_message.content
            if persisted_content is None:
                raise DurableGroundedGenerationError(
                    "Durable Grounded assistant has no persisted content to publish."
                )
            on_delta(persisted_content)
        return result
