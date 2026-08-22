"""Crash-safe Unified Local chat over the preserved retrieval implementation."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from athena.chat.durable_grounded_generation import DurableGroundedGenerationService
from athena.chat.generation import ChatGenerationResult, ChatGenerationService
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedRecoveryStatus
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.grounding import GroundingContract
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.service import ChatService
from athena.chat.unified_durable import (
    build_unified_grounded_fingerprint,
    build_unified_grounded_receipt,
)
from athena.chat.unified_legacy import (
    UnifiedLocalBudgetReport as UnifiedLocalBudgetReport,
)
from athena.chat.unified_legacy import (
    UnifiedLocalChatResult as UnifiedLocalChatResult,
)
from athena.chat.unified_legacy import (
    UnifiedLocalChatService as _LegacyUnifiedLocalChatService,
)
from athena.chat.unified_legacy import _canonical_text_key as _canonical_text_key
from athena.chat.unified_legacy import _merge_canonical_results as _merge_canonical_results
from athena.chat.unified_legacy import _query_tokens as _query_tokens
from athena.chat.unified_legacy import _render_epistemic_context as _render_epistemic_context
from athena.chat.unified_legacy import (
    _resolve_contextual_retrieval_query as _resolve_contextual_retrieval_query,
)
from athena.common.ids import new_uuid7
from athena.memory.models import MemoryScopeKind
from athena.model.provenance import (
    ModelRunRepository,
    ModelSignature,
    ProcessingRun,
)
from athena.retrieval.context import ContextBuilderError
from athena.retrieval.context_package import ContextPackage


class UnifiedGroundedRecoveryRequiredError(RuntimeError):
    """An existing Unified operation needs deterministic replay/recovery handling."""

    def __init__(self, status: GroundedRecoveryStatus) -> None:
        self.status = status
        super().__init__(
            f"Unified Grounded operation {status.operation_id} is "
            f"{status.state.value}; provider execution will not be replayed."
        )


@dataclass(slots=True)
class _UnifiedDurableCallState:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    fingerprint: ChatRequestFingerprint
    user_actor_id: uuid.UUID
    retrieval_query_override: str | None
    processing_run_id: uuid.UUID | None = None
    context_configuration: dict[str, Any] | None = None


class _DurableUnifiedUserChatService(ChatService):
    def __init__(
        self,
        base: ChatService,
        *,
        coordinator: GroundedSendCoordinator,
        state: _UnifiedDurableCallState,
    ) -> None:
        super().__init__(base.repository)
        self._coordinator = coordinator
        self._state = state

    def add_user_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        operation_id: uuid.UUID | None = None,
    ) -> ChatMessage:
        if chat_id != self._state.chat_id:
            raise RuntimeError("Unified durable user persistence escaped its chat identity.")
        if operation_id is not None and operation_id != self._state.operation_id:
            raise RuntimeError(
                "Unified durable user persistence escaped its operation identity."
            )
        started = self._coordinator.start(
            operation_id=self._state.operation_id,
            chat_id=chat_id,
            actor_id=self._state.user_actor_id,
            content=content,
            fingerprint=self._state.fingerprint,
        )
        return started.user_message


class _DurableUnifiedModelRunRepository(ModelRunRepository):
    def __init__(
        self,
        base: ModelRunRepository,
        *,
        coordinator: GroundedSendCoordinator,
        state: _UnifiedDurableCallState,
    ) -> None:
        super().__init__(base.database)
        self._base = base
        self._coordinator = coordinator
        self._state = state

    def get_or_create_signature(
        self,
        *,
        model: Any,
        generation_parameters: Mapping[str, Any],
        context_configuration: Mapping[str, Any] | None = None,
    ) -> ModelSignature:
        augmented = dict(context_configuration or {})
        if augmented.get("mode") == "unified_local_chat":
            augmented["retrieval_query_override"] = self._state.retrieval_query_override
            self._state.context_configuration = augmented
        return self._base.get_or_create_signature(
            model=model,
            generation_parameters=generation_parameters,
            context_configuration=augmented if context_configuration is not None else None,
        )

    def start_run(
        self,
        *,
        run_type: str,
        trigger_actor_id: uuid.UUID,
        pipeline_version: str,
        input_snapshot: Mapping[str, Any],
        configuration: Mapping[str, Any],
        model_signature_id: uuid.UUID | None,
        prompt_template_id: str | None,
        prompt_template_version: str | None,
    ) -> ProcessingRun:
        if run_type != "chat.unified_local_context_package":
            return self._base.start_run(
                run_type=run_type,
                trigger_actor_id=trigger_actor_id,
                pipeline_version=pipeline_version,
                input_snapshot=input_snapshot,
                configuration=configuration,
                model_signature_id=model_signature_id,
                prompt_template_id=prompt_template_id,
                prompt_template_version=prompt_template_version,
            )
        if trigger_actor_id != self._state.user_actor_id:
            raise RuntimeError(
                "Unified ProcessingRun trigger actor escaped the durable operation."
            )
        if self._state.processing_run_id is not None:
            raise RuntimeError("Unified durable call attempted to create a second ProcessingRun.")
        if self._state.context_configuration is None:
            raise RuntimeError(
                "Unified ProcessingRun started before its ModelSignature configuration was pinned."
            )

        exact_snapshot = dict(input_snapshot)
        legacy_override = exact_snapshot.pop("retrieval_query_override", None)
        if (
            self._state.retrieval_query_override is not None
            and legacy_override != self._state.retrieval_query_override
        ):
            raise RuntimeError(
                "Unified retrieval override drifted between signature and ProcessingRun."
            )
        run = self._base.start_run(
            run_type=run_type,
            trigger_actor_id=trigger_actor_id,
            pipeline_version=pipeline_version,
            input_snapshot=exact_snapshot,
            configuration=self._state.context_configuration,
            model_signature_id=model_signature_id,
            prompt_template_id=prompt_template_id,
            prompt_template_version=prompt_template_version,
        )
        self._state.processing_run_id = run.processing_run_id
        return run

    def finish_run(
        self,
        processing_run_id: uuid.UUID,
        *,
        status: str,
        error_detail: str | None = None,
    ) -> ProcessingRun:
        run = self._base.load_run(processing_run_id)
        if run.finished_at_us is not None:
            if status == "succeeded" and run.status != "succeeded":
                raise RuntimeError(
                    "Unified provider returned successfully after its ProcessingRun "
                    f"was already terminal as {run.status}."
                )
            return run

        if (
            processing_run_id == self._state.processing_run_id
            and status in {"failed", "cancelled"}
        ):
            recovery = self._coordinator.recover(
                operation_id=self._state.operation_id,
                chat_id=self._state.chat_id,
                fingerprint=self._state.fingerprint,
            )
            if recovery.state is GroundedRecoveryState.RESUMABLE:
                # The durable adapter deliberately leaves a run live when a
                # deterministic pre-provider callback fails. The legacy outer
                # orchestration must not turn that safely resumable state into a
                # false terminal failure.
                return run

        return self._base.finish_run(
            processing_run_id,
            status=status,
            error_detail=error_detail,
        )


class _UnifiedDurableGenerationAdapter(ChatGenerationService):
    def __init__(
        self,
        base: ChatGenerationService,
        durable_chat: ChatService,
        *,
        coordinator: GroundedSendCoordinator,
        state: _UnifiedDurableCallState,
    ) -> None:
        super().__init__(
            durable_chat,
            base.provider,
            interactive_demand=base.interactive_demand,
        )
        self._durable = DurableGroundedGenerationService(base, coordinator)
        self._state = state

    def send_context_package(
        self,
        *,
        chat_id: uuid.UUID,
        user_message: ChatMessage,
        context_package: ContextPackage,
        operation_id: uuid.UUID | None = None,
        on_delta: Callable[[str], None] | None = None,
        grounding_contract: GroundingContract | None = None,
        on_before_provider_call: Callable[[], None] | None = None,
    ) -> ChatGenerationResult:
        if chat_id != self._state.chat_id:
            raise RuntimeError("Unified generation escaped its durable chat identity.")
        if operation_id is not None and operation_id != self._state.operation_id:
            raise RuntimeError("Unified generation escaped its durable operation identity.")
        processing_run_id = self._state.processing_run_id
        if processing_run_id is None:
            raise RuntimeError(
                "Unified generation reached the provider boundary without a ProcessingRun."
            )

        embedding_model_id = _embedding_model_id(context_package)

        def receipt_payload_builder(
            assistant_text: str,
            provider_id: str,
            model_id: str,
        ) -> str:
            return build_unified_grounded_receipt(
                assistant_text=assistant_text,
                provider_id=provider_id,
                model_id=model_id,
                operation_id=self._state.operation_id,
                processing_run_id=processing_run_id,
                context_package_request_id=context_package.request_id,
                embedding_model_id=embedding_model_id,
            )

        return self._durable.send_context_package(
            operation_id=self._state.operation_id,
            chat_id=chat_id,
            user_message=user_message,
            context_package=context_package,
            processing_run_id=processing_run_id,
            fingerprint=self._state.fingerprint,
            receipt_payload_builder=receipt_payload_builder,
            on_delta=on_delta,
            grounding_contract=grounding_contract,
            on_before_provider_call=on_before_provider_call,
        )


def _embedding_model_id(package: ContextPackage) -> str | None:
    raw = package.model_signature.context_configuration_json
    if raw is None:
        return None
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("Unified ModelSignature context configuration is not an object.")
    value = parsed.get("embedding_model_id")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("Unified embedding model provenance is invalid.")
    return value


class UnifiedLocalChatService(_LegacyUnifiedLocalChatService):
    """Run the mature Unified retrieval algorithm behind a durable send boundary."""

    def send_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        retrieval_query: str | None = None,
        requested_model_id: str | None = None,
        requested_embedding_model_id: str | None = None,
        max_memory_context_tokens: int = 1200,
        max_memory_context_items: int = 8,
        max_memory_items: int = 8,
        max_source_context_tokens: int = 1200,
        max_source_context_items: int = 8,
        max_recent_conversation_turns: int = 8,
        memory_scope_kind: MemoryScopeKind | None = None,
        memory_scope_entity_id: uuid.UUID | None = None,
        effective_context_limit: int | None = None,
        output_reserve: int = 2048,
        safety_margin: int = 256,
        temperature: float | None = None,
        reasoning_mode: str | None = "off",
        allow_model_prior: bool = True,
        on_delta: Callable[[str], None] | None = None,
        operation_id: uuid.UUID | None = None,
    ) -> UnifiedLocalChatResult:
        normalized_retrieval_query: str | None = None
        if retrieval_query is not None:
            normalized_retrieval_query = retrieval_query.strip()
            if not normalized_retrieval_query:
                raise ContextBuilderError("Retrieval query override must not be empty.")

        resolved_operation_id = operation_id or new_uuid7()
        fingerprint = build_unified_grounded_fingerprint(
            chat_id=chat_id,
            content=content,
            retrieval_query_override=normalized_retrieval_query,
            requested_model_id=requested_model_id,
            requested_embedding_model_id=requested_embedding_model_id,
            max_memory_context_tokens=max_memory_context_tokens,
            max_memory_context_items=max_memory_context_items,
            max_memory_items=max_memory_items,
            max_source_context_tokens=max_source_context_tokens,
            max_source_context_items=max_source_context_items,
            max_recent_conversation_turns=max_recent_conversation_turns,
            memory_scope_kind=(
                None if memory_scope_kind is None else memory_scope_kind.value
            ),
            memory_scope_entity_id=memory_scope_entity_id,
            effective_context_limit=effective_context_limit,
            output_reserve=output_reserve,
            safety_margin=safety_margin,
            temperature=temperature,
            reasoning_mode=reasoning_mode,
            allow_model_prior=allow_model_prior,
        )

        coordinator = GroundedSendCoordinator(self.model_runs.database)
        recovery = coordinator.recover(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if recovery.state is not GroundedRecoveryState.ABSENT:
            raise UnifiedGroundedRecoveryRequiredError(recovery)

        # Resolve/create the canonical Local User before retrieval begins. Actor
        # creation must never become an unexpected semantic write between the
        # retrieval snapshot and the exact Grounded user commit.
        user_actor_id = self.chat_generation.chat.ensure_local_user()
        state = _UnifiedDurableCallState(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            user_actor_id=user_actor_id,
            retrieval_query_override=normalized_retrieval_query,
        )
        durable_chat = _DurableUnifiedUserChatService(
            self.chat_generation.chat,
            coordinator=coordinator,
            state=state,
        )
        durable_generation = _UnifiedDurableGenerationAdapter(
            self.chat_generation,
            durable_chat,
            coordinator=coordinator,
            state=state,
        )
        durable_model_runs = _DurableUnifiedModelRunRepository(
            self.model_runs,
            coordinator=coordinator,
            state=state,
        )
        delegated = _LegacyUnifiedLocalChatService(
            chat_generation=durable_generation,
            embedding_provider=self.embedding_provider,
            hybrid_retrieval=self.hybrid_retrieval,
            memory_context_builder=self.memory_context_builder,
            evidence_policy=self.evidence_policy,
            personal_memory=self.personal_memory,
            archive_retrieval=self.archive_retrieval,
            source_context_builder=self.source_context_builder,
            context_packages=self.context_packages,
            model_runs=durable_model_runs,
        )
        return delegated.send_message(
            chat_id=chat_id,
            content=content,
            retrieval_query=normalized_retrieval_query,
            requested_model_id=requested_model_id,
            requested_embedding_model_id=requested_embedding_model_id,
            max_memory_context_tokens=max_memory_context_tokens,
            max_memory_context_items=max_memory_context_items,
            max_memory_items=max_memory_items,
            max_source_context_tokens=max_source_context_tokens,
            max_source_context_items=max_source_context_items,
            max_recent_conversation_turns=max_recent_conversation_turns,
            memory_scope_kind=memory_scope_kind,
            memory_scope_entity_id=memory_scope_entity_id,
            effective_context_limit=effective_context_limit,
            output_reserve=output_reserve,
            safety_margin=safety_margin,
            temperature=temperature,
            reasoning_mode=reasoning_mode,
            allow_model_prior=allow_model_prior,
            on_delta=on_delta,
        )