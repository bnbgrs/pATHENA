"""Snapshot-pinned persistent direct chat orchestration."""

from __future__ import annotations

import math
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from athena.chat.generation import ChatGenerationResult, ChatGenerationService
from athena.chat.models import ChatMessage, MessageType
from athena.chat.provenance import (
    strip_model_facing_assistant_trace,
    strip_turn_local_grounding_markers,
)
from athena.chat.send_identity import SendOperationState, SendOperationStateError
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ProcessingRun
from athena.retrieval.context import ContextBuilderError, estimate_tokens
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextRole,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)

_DEFAULT_RECENT_CONVERSATION_TURNS = 8
_MAX_RECENT_CONVERSATION_TURNS = 100
_DEFAULT_OUTPUT_RESERVE = 2048
_DEFAULT_SAFETY_MARGIN = 256
_MESSAGE_WRAPPER_ESTIMATE = 6


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContextBuilderError(f"{label} must be an integer.")
    if value < 1:
        raise ContextBuilderError(f"{label} must be positive.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContextBuilderError(f"{label} must be an integer.")
    if value < 0:
        raise ContextBuilderError(f"{label} must not be negative.")
    return value


def _bounded_positive_int(value: object, *, label: str, maximum: int) -> int:
    validated = _positive_int(value, label)
    if validated > maximum:
        raise ContextBuilderError(f"{label} must be between 1 and {maximum}.")
    return validated


def _optional_temperature(value: object | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContextBuilderError("Temperature must be numeric when provided.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ContextBuilderError("Temperature must be finite.") from exc
    if not math.isfinite(normalized):
        raise ContextBuilderError("Temperature must be finite.")
    if not 0.0 <= normalized <= 2.0:
        raise ContextBuilderError(
            "Temperature must be between 0.0 and 2.0."
        )
    return normalized


@dataclass(frozen=True, slots=True)
class DirectChatGenerationResult:
    generation: ChatGenerationResult
    context_package: ContextPackage
    processing_run: ProcessingRun


class DirectChatService:
    """Generate ordinary persistent chat exclusively from one ContextPackage."""

    def __init__(
        self,
        *,
        chat_generation: ChatGenerationService,
        context_packages: ContextPackageService,
        model_runs: ModelRunRepository,
    ) -> None:
        self.chat_generation = chat_generation
        self.context_packages = context_packages
        self.model_runs = model_runs

    def send_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        requested_model_id: str | None = None,
        operation_id: uuid.UUID | None = None,
        max_recent_conversation_turns: int = _DEFAULT_RECENT_CONVERSATION_TURNS,
        effective_context_limit: int | None = None,
        output_reserve: int = _DEFAULT_OUTPUT_RESERVE,
        safety_margin: int = _DEFAULT_SAFETY_MARGIN,
        temperature: float | None = None,
        reasoning_mode: str | None = "off",
        on_delta: Callable[[str], None] | None = None,
    ) -> DirectChatGenerationResult:
        validated_turns = _bounded_positive_int(
            max_recent_conversation_turns,
            label="Recent conversation turns",
            maximum=_MAX_RECENT_CONVERSATION_TURNS,
        )
        validated_output_reserve = _positive_int(
            output_reserve,
            "Output reserve",
        )
        validated_safety_margin = _nonnegative_int(
            safety_margin,
            "Safety margin",
        )
        validated_temperature = _optional_temperature(temperature)
        if reasoning_mode not in {None, "off"}:
            raise ContextBuilderError(
                "Reasoning mode must be None or 'off'."
            )

        if operation_id is not None:
            operation_status = self.chat_generation.chat.inspect_send_operation(
                chat_id=chat_id,
                operation_id=operation_id,
                content=content,
            )

            if operation_status.state is not SendOperationState.ABSENT:
                raise SendOperationStateError(
                    operation_status
                )

        model = self.chat_generation.select_model(requested_model_id)
        context_limit = _resolve_context_limit(
            model=model,
            requested_limit=effective_context_limit,
        )
        effective_output_reserve = _resolve_output_reserve(
            requested_reserve=validated_output_reserve,
            context_limit=context_limit,
            safety_margin=validated_safety_margin,
        )
        retrieval_snapshot_commit_seq = self.context_packages.current_commit_seq()
        thread = self.chat_generation.chat.load_chat(chat_id)
        recent_messages = _select_recent_conversation_window(
            thread.messages,
            max_turns=validated_turns,
        )
        prior_sections, prior_refs = _prior_chat_sections(recent_messages)
        conversation_tokens = _estimate_persisted_messages(recent_messages)
        current_user_tokens = estimate_tokens(content) + _MESSAGE_WRAPPER_ESTIMATE
        estimated_input_tokens = conversation_tokens + current_user_tokens
        estimated_total_tokens = (
            estimated_input_tokens
            + effective_output_reserve
            + validated_safety_margin
        )
        if estimated_total_tokens > context_limit:
            raise ContextBuilderError(
                "Recent conversation plus current input, output reserve and safety "
                "margin exceed the active model context."
            )

        self.context_packages.assert_snapshot_current(
            retrieval_snapshot_commit_seq,
            phase="post-direct-context-build",
        )

        context_configuration = {
            "context_package_version": 1,
            "mode": "direct_chat",
            "effective_context_limit": context_limit,
            "max_recent_conversation_turns": validated_turns,
            "safety_margin": validated_safety_margin,
        }
        generation_parameters: dict[str, object] = {
            "max_output_tokens": effective_output_reserve,
            "reasoning_mode": reasoning_mode,
        }
        if validated_temperature is not None:
            generation_parameters["temperature"] = validated_temperature
        signature = self.model_runs.get_or_create_signature(
            model=model,
            generation_parameters=generation_parameters,
            context_configuration=context_configuration,
        )

        user_message = self.chat_generation.chat.add_user_message(
            chat_id=chat_id,
            content=content,
            operation_id=operation_id,
        )
        package_snapshot_commit_seq = self.context_packages.assert_user_commit_follows(
            retrieval_snapshot_commit_seq,
            user_message,
        )

        current_ref = ContextIncludedRef(
            ref_id="CURRENT-USER",
            entity_type="chat_message",
            entity_id=user_message.message_id,
            revision_id=user_message.revision_id,
        )
        sections = (
            *prior_sections,
            ContextSection(
                name="current_user",
                role="user",
                content=content,
                included_ref_ids=(current_ref.ref_id,),
            ),
        )
        included_refs = (*prior_refs, current_ref)
        excluded = ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=len(thread.messages),
            conversation_included_count=len(recent_messages),
            conversation_excluded_count=len(thread.messages) - len(recent_messages),
        )
        token_estimates = ContextTokenEstimates(
            conversation_tokens=conversation_tokens,
            current_user_tokens=current_user_tokens,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=estimated_input_tokens,
            estimated_total_tokens=estimated_total_tokens,
        )
        package = self.context_packages.build_from_sections(
            model_signature=signature,
            budget=ContextPackageBudget(
                effective_context_limit=context_limit,
                context_budget=0,
                output_reserve=effective_output_reserve,
                safety_margin=validated_safety_margin,
            ),
            sections=sections,
            included_refs=included_refs,
            excluded_candidate_summary=excluded,
            token_estimates=token_estimates,
            snapshot_commit_seq=package_snapshot_commit_seq,
        )

        if user_message.actor_id is None:
            raise RuntimeError("Persisted user message has no actor for ProcessingRun.")
        processing_run = self.model_runs.start_run(
            run_type="chat.direct_context_package",
            trigger_actor_id=user_message.actor_id,
            pipeline_version="direct-chat-context-package-v1",
            input_snapshot=package.run_snapshot(),
            configuration=context_configuration,
            model_signature_id=signature.model_signature_id,
            prompt_template_id="direct-chat",
            prompt_template_version="1",
        )

        try:
            generation = self.chat_generation.send_context_package(
                chat_id=chat_id,
                user_message=user_message,
                context_package=package,
                operation_id=operation_id,
                on_delta=on_delta,
                on_before_provider_call=lambda: self.context_packages.assert_snapshot_current(
                    package.snapshot_commit_seq,
                    phase="immediately-before-primary-model-call",
                ),
            )
        except KeyboardInterrupt:
            self.model_runs.finish_run(
                processing_run.processing_run_id,
                status="cancelled",
            )
            raise
        except Exception as exc:
            self.model_runs.finish_run(
                processing_run.processing_run_id,
                status="failed",
                error_detail=f"{type(exc).__name__}: {exc}"[:4000],
            )
            raise

        processing_run = self.model_runs.finish_run(
            processing_run.processing_run_id,
            status="succeeded",
        )
        return DirectChatGenerationResult(
            generation=generation,
            context_package=package,
            processing_run=processing_run,
        )


def _select_recent_conversation_window(
    messages: tuple[ChatMessage, ...],
    *,
    max_turns: int,
    include_assistant: bool = True,
) -> tuple[ChatMessage, ...]:
    """Select recent conversation with optional Assistant projection.

    Direct chat retains complete conversational history by default.

    Grounded paths exclude historical Assistant prose so a prior generated
    answer cannot silently become evidence under a later grounding contract.
    Historical User turns remain available for conversational continuity.
    """

    validated_turns = _bounded_positive_int(
        max_turns,
        label="Recent conversation turns",
        maximum=_MAX_RECENT_CONVERSATION_TURNS,
    )

    if not messages:
        return ()

    selected_reversed: list[ChatMessage] = []
    user_turns = 0

    for message in reversed(messages):
        if message.message_type is MessageType.USER:
            selected_reversed.append(
                message
            )

            user_turns += 1

            if user_turns >= validated_turns:
                break

            continue

        if message.message_type is MessageType.ASSISTANT:
            if include_assistant:
                selected_reversed.append(
                    message
                )

            continue

        # Preserve unexpected message kinds so downstream validation
        # continues to fail closed rather than hiding invalid state.
        selected_reversed.append(
            message
        )

    return tuple(
        reversed(
            selected_reversed
        )
    )


def _prior_chat_sections(
    messages: tuple[ChatMessage, ...],
) -> tuple[tuple[ContextSection, ...], tuple[ContextIncludedRef, ...]]:
    sections: list[ContextSection] = []
    refs: list[ContextIncludedRef] = []
    for index, message in enumerate(messages, start=1):
        if message.content is None:
            raise ContextBuilderError(
                "Protected or unavailable chat content cannot enter a ContextPackage."
            )
        role: ContextRole
        if message.message_type is MessageType.USER:
            role = "user"
            content = strip_turn_local_grounding_markers(
                message.content
            )
        elif message.message_type is MessageType.ASSISTANT:
            role = "assistant"
            content = strip_model_facing_assistant_trace(
                message.content
            )
        else:
            raise ContextBuilderError(
                f"Unsupported conversation message type {message.message_type.value!r}."
            )
        ref_id = f"CHAT-HIST-{index:03d}"
        refs.append(
            ContextIncludedRef(
                ref_id=ref_id,
                entity_type="chat_message",
                entity_id=message.message_id,
                revision_id=message.revision_id,
            )
        )
        sections.append(
            ContextSection(
                name="conversation",
                role=role,
                content=content,
                included_ref_ids=(ref_id,),
            )
        )
    return tuple(sections), tuple(refs)


def _estimate_persisted_messages(messages: tuple[ChatMessage, ...]) -> int:
    total = 0
    for message in messages:
        if message.content is not None:
            total += estimate_tokens(message.content) + _MESSAGE_WRAPPER_ESTIMATE
    return total


def _resolve_output_reserve(
    *,
    requested_reserve: int,
    context_limit: int,
    safety_margin: int,
) -> int:
    """Cap generation output so a small loaded context still has prompt room."""

    usable_context = context_limit - safety_margin
    if usable_context < 2:
        raise ContextBuilderError(
            "Active model context is too small after applying the safety margin."
        )
    prompt_balanced_ceiling = max(1, usable_context // 2)
    return min(requested_reserve, prompt_balanced_ceiling)


def _resolve_context_limit(
    *,
    model: ModelInfo,
    requested_limit: int | None,
) -> int:
    reported_effective = model.loaded_context_length
    if requested_limit is None:
        if reported_effective is None:
            raise ContextBuilderError(
                "Active model did not report its loaded runtime context; provide an "
                "explicit effective context limit instead of assuming the model maximum."
            )
        return reported_effective
    validated_limit = _positive_int(
        requested_limit,
        "Effective context limit",
    )
    if model.context_capacity is not None and validated_limit > model.context_capacity:
        raise ContextBuilderError(
            "Requested effective context limit exceeds the model maximum capacity."
        )
    if (
        model.loaded_context_length is not None
        and validated_limit > model.loaded_context_length
    ):
        raise ContextBuilderError(
            "Requested effective context limit exceeds the currently loaded "
            "LM Studio context."
        )
    return validated_limit
