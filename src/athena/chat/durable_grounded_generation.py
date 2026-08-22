"""Crash-safe adapter between ContextPackage generation and Grounded persistence."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable

from athena.chat.generation import ChatGenerationResult, ChatGenerationService
from athena.chat.grounding import GroundingContract
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    cancel_grounded_processing_run,
    complete_grounded_processing_run,
    fail_grounded_processing_run,
    validate_grounded_processing_run,
)
from athena.chat.grounded_provider_result_contract import validate_provider_result_contract
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_request_context import (
    GroundedRequestContextBindingError,
    validate_grounded_request_context_binding,
)
from athena.chat.grounded_send import (
    GroundedProviderBoundaryError,
    GroundedSendCoordinator,
)
from athena.chat.grounded_snapshot import (
    GroundedSnapshotBindingError,
    validate_grounded_snapshot_current,
)
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

        try:
            payload_json = self._receipt_payload_builder(
                content,
                provider_id,
                model_id,
            )
            validate_provider_result_contract(
                assistant_content=content,
                receipt_payload_json=payload_json,
            )
        except Exception as exc:
            fallback_payload_json = json.dumps(
                {
                    "assistant_text": content,
                    "model_id": model_id,
                    "provider_id": provider_id,
                    "recovery_receipt": True,
                },
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            self._coordinator.record_provider_result(
                operation_id=self._operation_id,
                chat_id=self._chat_id,
                fingerprint=self._fingerprint,
                processing_run_id=self._processing_run_id,
                assistant_content=content,
                receipt_payload_json=fallback_payload_json,
                provider_id=provider_id,
                model_id=model_id,
            )
            raise DurableGroundedGenerationError(
                "Provider returned a valid assistant answer, but durable receipt "
                "construction failed; the answer was journaled for recovery."
            ) from exc

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

    def _require_current_snapshot(
        self,
        *,
        context_package: ContextPackage,
        operation_id: uuid.UUID,
        message: str,
    ) -> None:
        try:
            validate_grounded_snapshot_current(
                self.coordinator.database,
                package=context_package,
                operation_id=operation_id,
            )
        except GroundedSnapshotBindingError as exc:
            raise DurableGroundedGenerationError(message) from exc

    def _reconcile_processing_run_after_error(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
        context_package: ContextPackage,
        processing_run_id: uuid.UUID,
        trigger_actor_id: uuid.UUID,
        error: BaseException,
    ) -> None:
        recovery = self.coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        try:
            if recovery.state in {
                GroundedRecoveryState.RESULT_AVAILABLE,
                GroundedRecoveryState.FINALIZATION_REQUIRED,
                GroundedRecoveryState.COMPLETE,
            }:
                complete_grounded_processing_run(
                    self.coordinator.database,
                    processing_run_id=processing_run_id,
                    package=context_package,
                    trigger_actor_id=trigger_actor_id,
                )
            elif recovery.state is GroundedRecoveryState.AMBIGUOUS:
                if isinstance(error, KeyboardInterrupt):
                    cancel_grounded_processing_run(
                        self.coordinator.database,
                        processing_run_id=processing_run_id,
                        package=context_package,
                        trigger_actor_id=trigger_actor_id,
                    )
                else:
                    fail_grounded_processing_run(
                        self.coordinator.database,
                        processing_run_id=processing_run_id,
                        package=context_package,
                        trigger_actor_id=trigger_actor_id,
                        error_detail=type(error).__name__,
                    )
        except GroundedProcessingRunError as exc:
            raise DurableGroundedGenerationError(
                "Grounded failure could not reconcile its ProcessingRun provenance."
            ) from exc

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
        if user_message.actor_id is None:
            raise DurableGroundedGenerationError(
                "Grounded generation user message is missing trigger-actor provenance."
            )
        recovery = self.coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if recovery.state is not GroundedRecoveryState.RESUMABLE:
            raise DurableGroundedGenerationError(
                "Grounded generation request identity is not safely resumable."
            )
        try:
            validate_grounded_request_context_binding(
                package=context_package,
                fingerprint=fingerprint,
            )
        except GroundedRequestContextBindingError as exc:
            raise DurableGroundedGenerationError(
                "Grounded ContextPackage conflicts with the durable request fingerprint."
            ) from exc
        self._require_current_snapshot(
            context_package=context_package,
            operation_id=operation_id,
            message="Grounded ContextPackage no longer owns the current canonical snapshot.",
        )
        try:
            validate_grounded_processing_run(
                self.coordinator.database,
                processing_run_id=processing_run_id,
                package=context_package,
                trigger_actor_id=user_message.actor_id,
            )
        except GroundedProcessingRunError as exc:
            raise DurableGroundedGenerationError(
                "Grounded generation lacks matching durable ProcessingRun provenance."
            ) from exc

        self.coordinator.store_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            package=context_package,
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
            before = self.coordinator.recover(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
            if before.state is not GroundedRecoveryState.RESUMABLE:
                raise GroundedProviderBoundaryError(before)
            self._require_current_snapshot(
                context_package=context_package,
                operation_id=operation_id,
                message="Canonical state changed before the Grounded provider boundary.",
            )
            if on_before_provider_call is not None:
                on_before_provider_call()
            self._require_current_snapshot(
                context_package=context_package,
                operation_id=operation_id,
                message="Canonical state changed during Grounded provider preflight.",
            )
            # Claim ambiguity only after every deterministic caller preflight has
            # succeeded. Once this durable claim returns, the provider call is the
            # very next external side effect and recovery must conservatively assume
            # it may have happened.
            self.coordinator.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        try:
            result = delegated.send_context_package(
                chat_id=chat_id,
                user_message=user_message,
                context_package=context_package,
                operation_id=operation_id,
                on_delta=None,
                grounding_contract=grounding_contract,
                on_before_provider_call=before_provider,
            )
        except KeyboardInterrupt as exc:
            self._reconcile_processing_run_after_error(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                context_package=context_package,
                processing_run_id=processing_run_id,
                trigger_actor_id=user_message.actor_id,
                error=exc,
            )
            raise
        except Exception as exc:
            self._reconcile_processing_run_after_error(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                context_package=context_package,
                processing_run_id=processing_run_id,
                trigger_actor_id=user_message.actor_id,
                error=exc,
            )
            raise
        try:
            complete_grounded_processing_run(
                self.coordinator.database,
                processing_run_id=processing_run_id,
                package=context_package,
                trigger_actor_id=user_message.actor_id,
            )
        except GroundedProcessingRunError as exc:
            raise DurableGroundedGenerationError(
                "Grounded answer is durable, but ProcessingRun finalization failed."
            ) from exc
        if on_delta is not None:
            persisted_content = result.assistant_message.content
            if persisted_content is None:
                raise DurableGroundedGenerationError(
                    "Durable Grounded assistant has no persisted content to publish."
                )
            on_delta(persisted_content)
        return result
