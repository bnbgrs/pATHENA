"""Unified Local chat with durable recovery before the current-user commit."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.service import ChatService
from athena.chat.unified import (
    UnifiedGroundedRecoveryRequiredError,
    UnifiedLocalChatResult,
    UnifiedLocalChatService as _DurableUnifiedLocalChatService,
    _CapturingEmbeddingProvider,
    _CapturingEvidencePolicy,
    _CapturingMemoryContextBuilder,
    _CapturingSourceContextBuilder,
    _DurableUnifiedModelRunRepository,
    _DurableUnifiedUserChatService,
    _UnifiedDurableCallState,
    _UnifiedDurableGenerationAdapter,
)
from athena.chat.unified_durable import build_unified_grounded_fingerprint
from athena.chat.unified_legacy import UnifiedLocalChatService as _LegacyUnifiedLocalChatService
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_pre_user_resume import (
    UnifiedPreUserResumeMaterialization,
    UnifiedPreUserResumeMaterializer,
)
from athena.chat.unified_send_plan import UnifiedSendPlanRepository
from athena.common.ids import new_uuid7
from athena.memory.models import MemoryScopeKind
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
from athena.retrieval.context import ContextBuilderError, ContextBuilderService
from athena.retrieval.context_package import ContextPackageService
from athena.retrieval.evidence import MemoryEvidencePolicy
from athena.retrieval.source_context import SourceContextBuilderService


class UnifiedPreUserRecoveryRequiredError(RuntimeError):
    """A frozen pre-user operation cannot safely enter a new retrieval cycle."""


@dataclass(slots=True)
class _PreUserCapture:
    retrieval_snapshot_commit_seq: int | None = None
    model_signature_id: uuid.UUID | None = None


class _CapturingContextPackageService(ContextPackageService):
    def __init__(self, base: ContextPackageService, capture: _PreUserCapture) -> None:
        super().__init__(base.database)
        self._base = base
        self._capture = capture

    def current_commit_seq(self) -> int:
        value = self._base.current_commit_seq()
        if self._capture.retrieval_snapshot_commit_seq is not None:
            raise RuntimeError("Unified retrieval snapshot was pinned more than once.")
        self._capture.retrieval_snapshot_commit_seq = value
        return value

    def assert_snapshot_current(self, expected_commit_seq: int, *, phase: str) -> None:
        self._base.assert_snapshot_current(expected_commit_seq, phase=phase)

    def assert_user_commit_follows(
        self,
        previous_commit_seq: int,
        user_message: ChatMessage,
    ) -> int:
        return self._base.assert_user_commit_follows(previous_commit_seq, user_message)


class _PlanCapturingModelRuns(_DurableUnifiedModelRunRepository):
    def __init__(
        self,
        base: ModelRunRepository,
        *,
        coordinator: GroundedSendCoordinator,
        state: _UnifiedDurableCallState,
        capture: _PreUserCapture,
    ) -> None:
        super().__init__(base, coordinator=coordinator, state=state)
        self._capture = capture

    def get_or_create_signature(
        self,
        *,
        model: ModelInfo,
        generation_parameters: Mapping[str, Any],
        context_configuration: Mapping[str, Any] | None = None,
    ) -> ModelSignature:
        signature = super().get_or_create_signature(
            model=model,
            generation_parameters=generation_parameters,
            context_configuration=context_configuration,
        )
        if (
            context_configuration is not None
            and context_configuration.get("mode") == "unified_local_chat"
        ):
            if self._capture.model_signature_id is not None:
                raise RuntimeError("Unified ModelSignature was pinned more than once.")
            self._capture.model_signature_id = signature.model_signature_id
        return signature


class _PlanDurableUserChatService(_DurableUnifiedUserChatService):
    def __init__(
        self,
        base: ChatService,
        *,
        coordinator: GroundedSendCoordinator,
        state: _UnifiedDurableCallState,
        capture: _PreUserCapture,
    ) -> None:
        super().__init__(base, coordinator=coordinator, state=state)
        self._capture = capture

    def add_user_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        operation_id: uuid.UUID | None = None,
    ) -> ChatMessage:
        state = self._state
        snapshot_seq = self._capture.retrieval_snapshot_commit_seq
        model_signature_id = self._capture.model_signature_id
        if snapshot_seq is None or model_signature_id is None:
            raise RuntimeError(
                "Unified user commit reached durability before snapshot/signature capture."
            )
        if state.primary_model is None:
            raise RuntimeError("Unified pre-user plan is missing its primary model.")
        if not state.embedding_model_captured:
            raise RuntimeError("Unified pre-user plan is missing embedding resolution.")
        if state.memory_context is None or state.source_context is None:
            raise RuntimeError("Unified pre-user plan is missing frozen retrieval context.")
        if state.evidence_selection is None:
            raise RuntimeError("Unified pre-user plan is missing evidence classification.")
        UnifiedSendPlanRepository(self._coordinator.database).store(
            operation_id=state.operation_id,
            chat_id=chat_id,
            fingerprint=state.fingerprint,
            user_actor_id=state.user_actor_id,
            retrieval_snapshot_commit_seq=snapshot_seq,
            model_signature_id=model_signature_id,
            retrieval_query_override=state.retrieval_query_override,
            primary_model=state.primary_model,
            embedding_model=state.embedding_model,
            memory_context=state.memory_context,
            source_context=state.source_context,
            evidence_selection=state.evidence_selection,
        )
        return super().add_user_message(
            chat_id=chat_id,
            content=content,
            operation_id=operation_id,
        )


class UnifiedLocalChatService(_DurableUnifiedLocalChatService):
    """Durable Unified service including the pre-user crash window."""

    def _complete_materialized_pre_user(
        self,
        *,
        coordinator: GroundedSendCoordinator,
        materialized: UnifiedPreUserResumeMaterialization,
        fingerprint: ChatRequestFingerprint,
        on_delta: Callable[[str], None] | None,
    ) -> UnifiedLocalChatResult:
        plan = materialized.plan
        projection = plan.projection
        state = _UnifiedDurableCallState(
            operation_id=plan.operation_id,
            chat_id=plan.chat_id,
            fingerprint=fingerprint,
            user_actor_id=plan.user_actor_id,
            retrieval_query_override=plan.retrieval_query_override,
            context_configuration=materialized.context_configuration,
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
        durable_model_runs = _DurableUnifiedModelRunRepository(
            self.model_runs,
            coordinator=coordinator,
            state=state,
        )
        durable_generation = _UnifiedDurableGenerationAdapter(
            self.chat_generation,
            durable_chat,
            coordinator=coordinator,
            state=state,
        )
        run_snapshot = materialized.package.run_snapshot()
        if plan.retrieval_query_override is not None:
            run_snapshot = {
                **run_snapshot,
                "retrieval_query_override": plan.retrieval_query_override,
            }
        processing_run = durable_model_runs.start_run(
            run_type="chat.unified_local_context_package",
            trigger_actor_id=plan.user_actor_id,
            pipeline_version="unified-local-chat-context-package-v1",
            input_snapshot=run_snapshot,
            configuration=materialized.context_configuration,
            model_signature_id=plan.model_signature_id,
            prompt_template_id="unified-local-grounding",
            prompt_template_version="1",
        )
        try:
            durable_generation.send_context_package(
                chat_id=plan.chat_id,
                user_message=materialized.user_message,
                context_package=materialized.package,
                operation_id=plan.operation_id,
                on_delta=on_delta,
                grounding_contract=materialized.grounding_contract,
            )
        except KeyboardInterrupt:
            durable_model_runs.finish_run(
                processing_run.processing_run_id,
                status="cancelled",
            )
            raise
        except Exception as exc:
            durable_model_runs.finish_run(
                processing_run.processing_run_id,
                status="failed",
                error_detail=f"{type(exc).__name__}: {exc}"[:4000],
            )
            raise
        durable_model_runs.finish_run(
            processing_run.processing_run_id,
            status="succeeded",
        )
        coordinator.finalize_recorded_result(
            operation_id=plan.operation_id,
            chat_id=plan.chat_id,
            fingerprint=fingerprint,
        )
        complete = coordinator.recover(
            operation_id=plan.operation_id,
            chat_id=plan.chat_id,
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

        pre_user = UnifiedPreUserRecoveryInspector(self.model_runs.database).inspect(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if pre_user.state is UnifiedPreUserRecoveryState.READY:
            materialized = UnifiedPreUserResumeMaterializer(
                self.model_runs.database
            ).materialize(
                operation_id=resolved_operation_id,
                chat_id=chat_id,
                content=content,
                fingerprint=fingerprint,
            )
            return self._complete_materialized_pre_user(
                coordinator=coordinator,
                materialized=materialized,
                fingerprint=fingerprint,
                on_delta=on_delta,
            )
        if pre_user.state is not UnifiedPreUserRecoveryState.ABSENT:
            raise UnifiedPreUserRecoveryRequiredError(
                pre_user.reason
                or f"Unified pre-user recovery state is {pre_user.state.value}."
            )

        user_actor_id = self.chat_generation.chat.ensure_local_user()
        state = _UnifiedDurableCallState(
            operation_id=resolved_operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            user_actor_id=user_actor_id,
            retrieval_query_override=normalized_retrieval_query,
        )
        capture = _PreUserCapture()
        durable_chat = _PlanDurableUserChatService(
            self.chat_generation.chat,
            coordinator=coordinator,
            state=state,
            capture=capture,
        )
        durable_generation = _UnifiedDurableGenerationAdapter(
            self.chat_generation,
            durable_chat,
            coordinator=coordinator,
            state=state,
        )
        durable_model_runs = _PlanCapturingModelRuns(
            self.model_runs,
            coordinator=coordinator,
            state=state,
            capture=capture,
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
            context_packages=cast(
                ContextPackageService,
                _CapturingContextPackageService(self.context_packages, capture),
            ),
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
