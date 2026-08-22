"""Unified Local chat extension for the pre-user crash window."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified import UnifiedLocalChatService as _DurableUnifiedLocalChatService
from athena.chat.unified import (
    UnifiedGroundedRecoveryRequiredError,
    UnifiedLocalChatResult,
    _DurableUnifiedModelRunRepository,
    _DurableUnifiedUserChatService,
    _UnifiedDurableCallState,
    _UnifiedDurableGenerationAdapter,
)
from athena.chat.unified_durable import build_unified_grounded_fingerprint
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_pre_user_resume import (
    UnifiedPreUserResumeMaterialization,
    UnifiedPreUserResumeMaterializer,
)
from athena.common.ids import new_uuid7
from athena.memory.models import MemoryScopeKind
from athena.retrieval.context import ContextBuilderError


class UnifiedPreUserRecoveryRequiredError(RuntimeError):
    """A frozen pre-user operation cannot safely enter a new retrieval cycle."""


class UnifiedLocalChatService(_DurableUnifiedLocalChatService):
    """Extend the durable Unified service with recovery before the user commit."""

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
            retrieval_snapshot_commit_seq=plan.retrieval_snapshot_commit_seq,
            model_signature_id=plan.model_signature_id,
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
                on_before_provider_call=lambda: self.source_context_builder.verify_bundle(
                    projection.source_context
                ),
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
                coordinator=GroundedSendCoordinator(self.model_runs.database),
                materialized=materialized,
                fingerprint=fingerprint,
                on_delta=on_delta,
            )
        if pre_user.state is UnifiedPreUserRecoveryState.CONFLICT:
            raise UnifiedPreUserRecoveryRequiredError(
                pre_user.reason or "Unified pre-user recovery is conflicted."
            )

        return super().send_message(
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
            operation_id=resolved_operation_id,
        )
