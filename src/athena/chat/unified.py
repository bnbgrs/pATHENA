"""Crash-safe Unified Local chat over the preserved retrieval implementation."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.durable_grounded_generation import DurableGroundedGenerationService
from athena.chat.generation import ChatGenerationResult, ChatGenerationService
from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedRecoveryStatus
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.grounding import GroundingContract, validate_grounded_answer
from athena.chat.models import ChatMessage
from athena.chat.provenance import strip_durable_provenance_manifest
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
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
from athena.chat.unified_replay import (
    UnifiedReplayProjectionError,
    build_unified_replay_projection,
    load_unified_replay_projection,
)
from athena.chat.unified_replay_input import (
    UnifiedReplayInputRepository,
    UnifiedReplayInputSchemaError,
)
from athena.common.ids import new_uuid7
from athena.memory.models import MemoryScopeKind
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.model.domain import ModelInfo
from athena.model.provenance import (
    ModelRunRepository,
    ModelSignature,
    ProcessingRun,
)
from athena.retrieval.context import ContextBuilderError, ContextBuilderService, ContextBundle
from athena.retrieval.context_package import ContextPackage
from athena.retrieval.evidence import MemoryEvidencePolicy, MemoryEvidenceSelection
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.source_context import SourceContextBuilderService, SourceContextBundle


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
    primary_model: ModelInfo | None = None
    embedding_model: ModelInfo | None = None
    embedding_model_captured: bool = False
    memory_context: ContextBundle | None = None
    source_context: SourceContextBundle | None = None
    evidence_selection: MemoryEvidenceSelection | None = None


class _CapturingEmbeddingProvider:
    def __init__(
        self,
        base: LMStudioEmbeddingProvider,
        state: _UnifiedDurableCallState,
    ) -> None:
        self._base = base
        self._state = state

    def resolve_model(self, requested_model_id: str | None = None) -> ModelInfo:
        try:
            model = self._base.resolve_model(requested_model_id)
        except Exception:
            self._state.embedding_model = None
            self._state.embedding_model_captured = True
            raise
        self._state.embedding_model = model if model.loaded else None
        self._state.embedding_model_captured = True
        return model


class _CapturingMemoryContextBuilder:
    def __init__(
        self,
        base: ContextBuilderService,
        state: _UnifiedDurableCallState,
    ) -> None:
        self._base = base
        self._state = state

    def build_from_hybrid(self, *args: Any, **kwargs: Any) -> ContextBundle:
        bundle = self._base.build_from_hybrid(*args, **kwargs)
        self._state.memory_context = bundle
        return bundle


class _CapturingEvidencePolicy:
    def __init__(
        self,
        base: MemoryEvidencePolicy,
        state: _UnifiedDurableCallState,
    ) -> None:
        self._base = base
        self._state = state

    def classify(
        self,
        results: tuple[HybridSearchResult, ...],
    ) -> MemoryEvidenceSelection:
        selection = self._base.classify(results)
        self._state.evidence_selection = selection
        return selection


class _CapturingSourceContextBuilder:
    def __init__(
        self,
        base: SourceContextBuilderService,
        state: _UnifiedDurableCallState,
    ) -> None:
        self._base = base
        self._state = state

    def build_from_hybrid(self, *args: Any, **kwargs: Any) -> SourceContextBundle:
        bundle = self._base.build_from_hybrid(*args, **kwargs)
        self._state.source_context = bundle
        return bundle

    def verify_bundle(self, bundle: SourceContextBundle) -> None:
        self._base.verify_bundle(bundle)

    def rebase_context_ids(
        self,
        bundle: SourceContextBundle,
        *,
        start_index: int,
    ) -> SourceContextBundle:
        rebased = self._base.rebase_context_ids(
            bundle,
            start_index=start_index,
        )
        self._state.source_context = rebased
        return rebased


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
        self._coordinator = coordinator
        self._state = state

    def select_model(self, requested_model_id: str | None = None) -> ModelInfo:
        model = super().select_model(requested_model_id)
        self._state.primary_model = model
        return model

    def _replay_projection(
        self,
        *,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        context_package: ContextPackage,
    ) -> dict[str, Any]:
        if self._state.primary_model is None:
            raise UnifiedReplayProjectionError(
                "Unified replay projection is missing its primary model."
            )
        if not self._state.embedding_model_captured:
            raise UnifiedReplayProjectionError(
                "Unified replay projection is missing embedding resolution."
            )
        if self._state.memory_context is None:
            raise UnifiedReplayProjectionError(
                "Unified replay projection is missing Memory/Knowledge context."
            )
        if self._state.source_context is None:
            raise UnifiedReplayProjectionError(
                "Unified replay projection is missing Raw Archive context."
            )
        if self._state.evidence_selection is None:
            raise UnifiedReplayProjectionError(
                "Unified replay projection is missing evidence classification."
            )
        return build_unified_replay_projection(
            operation_id=self._state.operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            context_package=context_package,
            primary_model=self._state.primary_model,
            embedding_model=self._state.embedding_model,
            memory_context=self._state.memory_context,
            source_context=self._state.source_context,
            evidence_selection=self._state.evidence_selection,
        )

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
        replay_projection = self._replay_projection(
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            context_package=context_package,
        )

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
                replay_projection=replay_projection,
            )

        def before_provider() -> None:
            UnifiedReplayInputRepository(self._coordinator.database).store(
                operation_id=self._state.operation_id,
                chat_id=chat_id,
                processing_run_id=processing_run_id,
                projection=replay_projection,
            )
            if on_before_provider_call is not None:
                on_before_provider_call()

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
            on_before_provider_call=before_provider,
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


def _budget_from_package(package: ContextPackage) -> UnifiedLocalBudgetReport:
    try:
        configuration = json.loads(
            package.model_signature.context_configuration_json or "{}"
        )
    except json.JSONDecodeError as exc:
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage configuration is invalid JSON."
        ) from exc
    if not isinstance(configuration, dict):
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage configuration is not an object."
        )
    memory_budget = configuration.get("memory_context_budget")
    source_budget = configuration.get("source_context_budget")
    if (
        isinstance(memory_budget, bool)
        or not isinstance(memory_budget, int)
        or isinstance(source_budget, bool)
        or not isinstance(source_budget, int)
    ):
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage is missing retrieval budgets."
        )
    return UnifiedLocalBudgetReport(
        effective_context_limit=package.budget.effective_context_limit,
        memory_context_budget=memory_budget,
        source_context_budget=source_budget,
        estimated_input_tokens=package.token_estimates.estimated_input_tokens,
        context_tokens=package.token_estimates.context_tokens,
        output_reserve=package.budget.output_reserve,
        safety_margin=package.budget.safety_margin,
        estimated_total_tokens=package.token_estimates.estimated_total_tokens,
    )


def _context_configuration(package: ContextPackage) -> dict[str, Any]:
    try:
        configuration = json.loads(
            package.model_signature.context_configuration_json or "{}"
        )
    except json.JSONDecodeError as exc:
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage configuration is invalid JSON."
        ) from exc
    if not isinstance(configuration, dict):
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage configuration is not an object."
        )
    return cast(dict[str, Any], configuration)


class UnifiedLocalChatService(_LegacyUnifiedLocalChatService):
    """Run the mature Unified retrieval algorithm behind a durable send boundary."""

    def _replay_complete(
        self,
        *,
        status: GroundedRecoveryStatus,
    ) -> UnifiedLocalChatResult:
        if status.state is not GroundedRecoveryState.COMPLETE:
            raise UnifiedGroundedRecoveryRequiredError(status)
        result = status.provider_result
        identity = status.provider_identity
        receipt = status.receipt
        processing_run_id = status.processing_run_id
        if (
            result is None
            or identity is None
            or receipt is None
            or processing_run_id is None
        ):
            raise UnifiedReplayProjectionError(
                "Complete Unified recovery is missing durable replay state."
            )
        if (
            result.processing_run_id != processing_run_id
            or receipt.processing_run_id != processing_run_id
            or result.receipt_payload_json != receipt.payload_json
        ):
            raise UnifiedReplayProjectionError(
                "Complete Unified recovery has inconsistent run/receipt identity."
            )

        context_record = GroundedContextPackageRepository(
            self.model_runs.database
        ).load(status.operation_id)
        if context_record is None or context_record.chat_id != status.chat_id:
            raise UnifiedReplayProjectionError(
                "Complete Unified recovery is missing its exact ContextPackage."
            )
        package = context_record.package
        projection = load_unified_replay_projection(
            receipt_payload_json=receipt.payload_json,
            operation_id=status.operation_id,
            chat_id=status.chat_id,
            processing_run_id=processing_run_id,
            context_package=package,
            provider_id=identity.provider_id,
            model_id=identity.model_id,
        )

        run = self.model_runs.load_run(processing_run_id)
        if run.status != "succeeded" or run.finished_at_us is None:
            raise UnifiedReplayProjectionError(
                "Complete Unified recovery requires a succeeded ProcessingRun."
            )
        thread = self.chat_generation.chat.load_chat(status.chat_id)
        assistant_id = assistant_message_id_for_operation(status.operation_id)
        user_message = next(
            (item for item in thread.messages if item.message_id == status.operation_id),
            None,
        )
        assistant_message = next(
            (item for item in thread.messages if item.message_id == assistant_id),
            None,
        )
        if user_message is None or assistant_message is None:
            raise UnifiedReplayProjectionError(
                "Complete Unified recovery is missing its deterministic chat turns."
            )
        if assistant_message.content != result.assistant_content:
            raise UnifiedReplayProjectionError(
                "Complete Unified assistant turn conflicts with provider result."
            )

        grounding_contract = _LegacyUnifiedLocalChatService._grounding_contract(
            memory_context=projection.memory_context,
            source_context=projection.source_context,
            evidence_selection=projection.evidence_selection,
            allow_model_prior=_allow_model_prior(package),
        )
        public_text = strip_durable_provenance_manifest(result.assistant_content)
        grounding_report = validate_grounded_answer(
            public_text,
            contract=grounding_contract,
        )
        generation = ChatGenerationResult(
            user_message=user_message,
            assistant_message=assistant_message,
            model=projection.primary_model,
            grounding_report=grounding_report,
        )
        return UnifiedLocalChatResult(
            generation=generation,
            memory_context=projection.memory_context,
            source_context=projection.source_context,
            context_package=package,
            processing_run=run,
            embedding_model=projection.embedding_model,
            evidence_selection=projection.evidence_selection,
            budget=_budget_from_package(package),
        )

    def _resume_from_checkpoint(
        self,
        *,
        coordinator: GroundedSendCoordinator,
        status: GroundedRecoveryStatus,
        fingerprint: ChatRequestFingerprint,
        retrieval_query_override: str | None,
        on_delta: Callable[[str], None] | None,
    ) -> UnifiedLocalChatResult:
        if status.state is not GroundedRecoveryState.RESUMABLE:
            raise UnifiedGroundedRecoveryRequiredError(status)
        processing_run_id = status.processing_run_id
        if processing_run_id is None:
            raise UnifiedGroundedRecoveryRequiredError(status)
        context_record = GroundedContextPackageRepository(
            self.model_runs.database
        ).load(status.operation_id)
        if context_record is None or context_record.chat_id != status.chat_id:
            raise UnifiedGroundedRecoveryRequiredError(status)
        try:
            checkpoint = UnifiedReplayInputRepository(
                self.model_runs.database
            ).load(status.operation_id)
        except UnifiedReplayInputSchemaError as exc:
            raise UnifiedReplayProjectionError(
                "Unified resumable replay checkpoint failed integrity validation."
            ) from exc
        if (
            checkpoint is None
            or checkpoint.chat_id != status.chat_id
            or checkpoint.processing_run_id != processing_run_id
            or checkpoint.context_package_request_id
            != context_record.package.request_id
        ):
            raise UnifiedGroundedRecoveryRequiredError(status)

        thread = self.chat_generation.chat.load_chat(status.chat_id)
        user_message = next(
            (item for item in thread.messages if item.message_id == status.operation_id),
            None,
        )
        if user_message is None or user_message.actor_id is None:
            raise UnifiedReplayProjectionError(
                "Unified resumable operation is missing its durable trigger user."
            )
        projection = checkpoint.projection
        state = _UnifiedDurableCallState(
            operation_id=status.operation_id,
            chat_id=status.chat_id,
            fingerprint=fingerprint,
            user_actor_id=user_message.actor_id,
            retrieval_query_override=retrieval_query_override,
            processing_run_id=processing_run_id,
            context_configuration=_context_configuration(context_record.package),
            primary_model=projection.primary_model,
            embedding_model=projection.embedding_model,
            embedding_model_captured=True,
            memory_context=projection.memory_context,
            source_context=projection.source_context,
            evidence_selection=projection.evidence_selection,
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
        grounding_contract = _LegacyUnifiedLocalChatService._grounding_contract(
            memory_context=projection.memory_context,
            source_context=projection.source_context,
            evidence_selection=projection.evidence_selection,
            allow_model_prior=_allow_model_prior(context_record.package),
        )
        durable_generation.send_context_package(
            chat_id=status.chat_id,
            user_message=user_message,
            context_package=context_record.package,
            operation_id=status.operation_id,
            on_delta=on_delta,
            grounding_contract=grounding_contract,
        )
        coordinator.finalize_recorded_result(
            operation_id=status.operation_id,
            chat_id=status.chat_id,
            fingerprint=fingerprint,
        )
        complete = coordinator.recover(
            operation_id=status.operation_id,
            chat_id=status.chat_id,
            fingerprint=fingerprint,
        )
        if complete.state is not GroundedRecoveryState.COMPLETE:
            raise UnifiedGroundedRecoveryRequiredError(complete)
        return self._replay_complete(status=complete)

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
        if recovery.state in {
            GroundedRecoveryState.RESULT_AVAILABLE,
            GroundedRecoveryState.FINALIZATION_REQUIRED,
        }:
            coordinator.finalize_recorded_result(
                operation_id=resolved_operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
            recovery = coordinator.recover(
                operation_id=resolved_operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
        if recovery.state is GroundedRecoveryState.COMPLETE:
            return self._replay_complete(status=recovery)
        if recovery.state is GroundedRecoveryState.RESUMABLE:
            return self._resume_from_checkpoint(
                coordinator=coordinator,
                status=recovery,
                fingerprint=fingerprint,
                retrieval_query_override=normalized_retrieval_query,
                on_delta=on_delta,
            )
        if recovery.state is not GroundedRecoveryState.ABSENT:
            raise UnifiedGroundedRecoveryRequiredError(recovery)

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
            embedding_provider=cast(
                LMStudioEmbeddingProvider,
                _CapturingEmbeddingProvider(self.embedding_provider, state),
            ),
            hybrid_retrieval=self.hybrid_retrieval,
            memory_context_builder=cast(
                ContextBuilderService,
                _CapturingMemoryContextBuilder(self.memory_context_builder, state),
            ),
            evidence_policy=cast(
                MemoryEvidencePolicy,
                _CapturingEvidencePolicy(self.evidence_policy, state),
            ),
            personal_memory=self.personal_memory,
            archive_retrieval=self.archive_retrieval,
            source_context_builder=cast(
                SourceContextBuilderService,
                _CapturingSourceContextBuilder(self.source_context_builder, state),
            ),
            context_packages=self.context_packages,
            model_runs=durable_model_runs,
        )
        delegated.send_message(
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
        coordinator.finalize_recorded_result(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        complete = coordinator.recover(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if complete.state is not GroundedRecoveryState.COMPLETE:
            raise UnifiedGroundedRecoveryRequiredError(complete)
        return self._replay_complete(status=complete)


def _allow_model_prior(package: ContextPackage) -> bool:
    configuration = _context_configuration(package)
    value = configuration.get("allow_model_prior")
    if not isinstance(value, bool):
        raise UnifiedReplayProjectionError(
            "Unified replay ContextPackage is missing allow_model_prior."
        )
    return value
