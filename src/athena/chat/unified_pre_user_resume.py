"""Deterministic ContextPackage materialization from a frozen Unified send plan."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.direct import (
    _estimate_persisted_messages,
    _prior_chat_sections,
    _select_recent_conversation_window,
)
from athena.chat.grounding import GroundingContract, render_grounding_instructions
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified_legacy import (
    _EPISTEMIC_GROUNDING_VERSION,
    _EPISTEMIC_INTERPRETATION,
    _RESPONSE_LANGUAGE_INSTRUCTION,
    _RESPONSE_LANGUAGE_POLICY_VERSION,
    UnifiedLocalChatService as _LegacyUnifiedLocalChatService,
    _render_epistemic_context,
)
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_pre_user_transition import UnifiedPreUserTransitionService
from athena.chat.unified_send_plan import UnifiedSendPlanRecord
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import estimate_tokens
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


class UnifiedPreUserResumeError(RuntimeError):
    """A frozen pre-user operation cannot be reconstructed exactly enough to resume."""


@dataclass(frozen=True, slots=True)
class UnifiedPreUserResumeMaterialization:
    plan: UnifiedSendPlanRecord
    user_message: ChatMessage
    package: ContextPackage
    grounding_contract: GroundingContract
    context_configuration: dict[str, Any]


def _json_object(raw: str | None, *, label: str) -> dict[str, Any]:
    try:
        decoded = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise UnifiedPreUserResumeError(f"{label} is invalid JSON.") from exc
    if not isinstance(decoded, dict):
        raise UnifiedPreUserResumeError(f"{label} must be a JSON object.")
    return cast(dict[str, Any], decoded)


def _required_int(configuration: dict[str, Any], key: str, *, minimum: int = 0) -> int:
    value = configuration.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise UnifiedPreUserResumeError(
            f"Unified pre-user ModelSignature has invalid {key!r}."
        )
    return value


class UnifiedPreUserResumeMaterializer:
    """Build the post-user ContextPackage without rerunning mutable retrieval."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.inspector = UnifiedPreUserRecoveryInspector(database)
        self.transitions = UnifiedPreUserTransitionService(database)
        self.context_packages = ContextPackageService(database)
        self.model_runs = ModelRunRepository(database)
        self.chats = ChatRepository(database)

    def materialize(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        content: str,
        fingerprint: ChatRequestFingerprint,
    ) -> UnifiedPreUserResumeMaterialization:
        status = self.inspector.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if status.state is not UnifiedPreUserRecoveryState.READY or status.plan is None:
            raise UnifiedPreUserResumeError(
                "Unified pre-user resume requires a READY frozen plan; "
                f"state={status.state.value}."
            )
        plan = status.plan
        chat_thread = self.chats.load_chat(chat_id)

        signature = self.model_runs.load_signature(plan.model_signature_id)
        configuration = _json_object(
            signature.context_configuration_json,
            label="Unified pre-user ModelSignature context configuration",
        )
        generation = _json_object(
            signature.generation_parameters_json,
            label="Unified pre-user ModelSignature generation parameters",
        )
        if configuration.get("mode") != "unified_local_chat":
            raise UnifiedPreUserResumeError(
                "Unified pre-user ModelSignature does not describe Unified Local chat."
            )
        if configuration.get("context_package_version") != 1:
            raise UnifiedPreUserResumeError(
                "Unified pre-user ContextPackage version is unsupported."
            )
        if configuration.get("epistemic_grounding_version") != _EPISTEMIC_GROUNDING_VERSION:
            raise UnifiedPreUserResumeError(
                "Unified pre-user epistemic grounding policy version drifted."
            )
        if configuration.get("response_language_policy_version") != _RESPONSE_LANGUAGE_POLICY_VERSION:
            raise UnifiedPreUserResumeError(
                "Unified pre-user response-language policy version drifted."
            )

        max_recent_turns = _required_int(
            configuration,
            "max_recent_conversation_turns",
            minimum=1,
        )
        effective_context_limit = _required_int(
            configuration,
            "effective_context_limit",
            minimum=1,
        )
        memory_budget = _required_int(configuration, "memory_context_budget", minimum=1)
        source_budget = _required_int(configuration, "source_context_budget", minimum=1)
        safety_margin = _required_int(configuration, "safety_margin")
        output_reserve_raw = generation.get("max_output_tokens")
        if (
            isinstance(output_reserve_raw, bool)
            or not isinstance(output_reserve_raw, int)
            or output_reserve_raw < 1
        ):
            raise UnifiedPreUserResumeError(
                "Unified pre-user ModelSignature has invalid output reserve."
            )
        output_reserve = output_reserve_raw
        allow_model_prior = configuration.get("allow_model_prior")
        if not isinstance(allow_model_prior, bool):
            raise UnifiedPreUserResumeError(
                "Unified pre-user ModelSignature is missing allow_model_prior."
            )

        recent_messages = _select_recent_conversation_window(
            chat_thread.messages,
            max_turns=max_recent_turns,
            include_assistant=False,
        )
        prior_sections, prior_refs = _prior_chat_sections(recent_messages)
        conversation_tokens = _estimate_persisted_messages(recent_messages)
        projection = plan.projection
        grounding_contract = _LegacyUnifiedLocalChatService._grounding_contract(
            memory_context=projection.memory_context,
            source_context=projection.source_context,
            evidence_selection=projection.evidence_selection,
            allow_model_prior=allow_model_prior,
        )
        epistemic_context = _render_epistemic_context(
            memory_context=projection.memory_context,
            evidence_selection=projection.evidence_selection,
        )
        system_text = (
            render_grounding_instructions(grounding_contract)
            + _EPISTEMIC_INTERPRETATION
            + _RESPONSE_LANGUAGE_INSTRUCTION
            + "\nATHENA CANONICAL EPISTEMIC METADATA\n"
            + epistemic_context
            + "\n\nATHENA LOCAL MEMORY / KNOWLEDGE CONTEXT\n"
            + projection.memory_context.rendered_text
            + "\n\nATHENA RAW ARCHIVE CONTEXT\n"
            + projection.source_context.rendered_text
        )
        current_user_tokens = estimate_tokens(content)
        system_tokens = estimate_tokens(system_text)
        estimated_input_tokens = conversation_tokens + current_user_tokens + system_tokens
        estimated_total_tokens = estimated_input_tokens + output_reserve + safety_margin
        if estimated_total_tokens > effective_context_limit:
            raise UnifiedPreUserResumeError(
                "Unified pre-user replay no longer fits its pinned model context."
            )

        transition = self.transitions.start(
            operation_id=operation_id,
            chat_id=chat_id,
            content=content,
            fingerprint=fingerprint,
        )
        if transition.plan != plan:
            raise UnifiedPreUserResumeError(
                "Unified pre-user plan changed while transitioning to the user commit."
            )

        system_refs = _LegacyUnifiedLocalChatService._system_package_refs(
            memory_context=projection.memory_context,
            source_context=projection.source_context,
        )
        current_ref = ContextIncludedRef(
            ref_id="CURRENT-USER",
            entity_type="chat_message",
            entity_id=transition.user_message.message_id,
            revision_id=transition.user_message.revision_id,
        )
        sections = (
            ContextSection(
                name="unified_local_context",
                role="system",
                content=system_text,
                included_ref_ids=tuple(item.ref_id for item in system_refs),
            ),
            *prior_sections,
            ContextSection(
                name="current_user",
                role="user",
                content=content,
                included_ref_ids=(current_ref.ref_id,),
            ),
        )
        retrieval_candidate_count = (
            len(projection.evidence_selection.results)
            + len(projection.source_context.items)
            + projection.source_context.omitted_count
        )
        retrieval_included_count = (
            len(projection.memory_context.items) + len(projection.source_context.items)
        )
        memory_candidate_count = (
            len(projection.memory_context.memory_items)
            + projection.memory_context.omitted_memory_count
        )
        package = self.context_packages.build_from_sections(
            model_signature=signature,
            budget=ContextPackageBudget(
                effective_context_limit=effective_context_limit,
                context_budget=memory_budget + source_budget,
                output_reserve=output_reserve,
                safety_margin=safety_margin,
            ),
            sections=sections,
            included_refs=(*system_refs, *prior_refs, current_ref),
            excluded_candidate_summary=ExcludedCandidateSummary(
                retrieval_candidate_count=retrieval_candidate_count,
                retrieval_included_count=retrieval_included_count,
                retrieval_excluded_count=(
                    retrieval_candidate_count - retrieval_included_count
                ),
                memory_candidate_count=memory_candidate_count,
                memory_included_count=len(projection.memory_context.memory_items),
                memory_excluded_count=projection.memory_context.omitted_memory_count,
                conversation_candidate_count=len(chat_thread.messages),
                conversation_included_count=len(recent_messages),
                conversation_excluded_count=(
                    len(chat_thread.messages) - len(recent_messages)
                ),
            ),
            token_estimates=ContextTokenEstimates(
                conversation_tokens=conversation_tokens,
                current_user_tokens=current_user_tokens,
                system_tokens=system_tokens,
                context_tokens=(
                    projection.memory_context.estimated_tokens
                    + projection.source_context.estimated_tokens
                ),
                estimated_input_tokens=estimated_input_tokens,
                estimated_total_tokens=estimated_total_tokens,
            ),
            snapshot_commit_seq=transition.package_snapshot_commit_seq,
        )
        return UnifiedPreUserResumeMaterialization(
            plan=plan,
            user_message=transition.user_message,
            package=package,
            grounding_contract=grounding_contract,
            context_configuration=configuration,
        )
