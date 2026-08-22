from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_request_context import (
    GroundedRequestContextBindingError,
    validate_grounded_request_context_binding,
)
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _package(
    operation_id: uuid.UUID,
    *,
    generation_parameters_json: str,
):
    signature = ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization="Q4_K_M",
        generation_parameters_json=generation_parameters_json,
        context_configuration_json='{"context_package_version":1}',
        signature_hash=b"s" * 32,
        created_at_us=1,
    )
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="current_user",
                role="user",
                content="hello",
                included_ref_ids=("CURRENT-USER",),
            ),
        ),
        included_refs=(
            ContextIncludedRef(
                ref_id="CURRENT-USER",
                entity_type="chat_message",
                entity_id=operation_id,
                revision_id=uuid.uuid4(),
            ),
        ),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=0,
            conversation_included_count=0,
            conversation_excluded_count=0,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1210,
        ),
        snapshot_commit_seq=1,
    )


def _fingerprint(
    chat_id: uuid.UUID,
    *,
    temperature: float | None,
    reasoning_mode: str | None,
):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=temperature,
        reasoning_mode=reasoning_mode,
        retrieval_configuration={},
    )


def test_none_temperature_cannot_gain_sampling_temperature() -> None:
    with pytest.raises(
        GroundedRequestContextBindingError,
        match="temperature conflicts",
    ):
        validate_grounded_request_context_binding(
            package=_package(
                uuid.uuid4(),
                generation_parameters_json=(
                    '{"max_output_tokens":1000,"reasoning_mode":"off",'
                    '"temperature":0.7}'
                ),
            ),
            fingerprint=_fingerprint(
                uuid.uuid4(),
                temperature=None,
                reasoning_mode="off",
            ),
        )


def test_none_reasoning_mode_cannot_become_explicit_off() -> None:
    with pytest.raises(
        GroundedRequestContextBindingError,
        match="reasoning mode conflicts",
    ):
        validate_grounded_request_context_binding(
            package=_package(
                uuid.uuid4(),
                generation_parameters_json=(
                    '{"max_output_tokens":1000,"reasoning_mode":"off"}'
                ),
            ),
            fingerprint=_fingerprint(
                uuid.uuid4(),
                temperature=None,
                reasoning_mode=None,
            ),
        )


def test_matching_none_optional_controls_remain_valid() -> None:
    validate_grounded_request_context_binding(
        package=_package(
            uuid.uuid4(),
            generation_parameters_json='{"max_output_tokens":1000}',
        ),
        fingerprint=_fingerprint(
            uuid.uuid4(),
            temperature=None,
            reasoning_mode=None,
        ),
    )
