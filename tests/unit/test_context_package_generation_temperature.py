from __future__ import annotations

import uuid

import pytest

from athena.retrieval.context_package import (
    ContextModelSignature,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageError,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _package(generation_parameters_json: str) -> ContextPackage:
    return ContextPackage(
        request_id=uuid.uuid4(),
        model_signature=ContextModelSignature(
            model_signature_id=uuid.uuid4(),
            provider="lm_studio",
            model_identifier="model",
            model_revision=None,
            quantization=None,
            generation_parameters_json=generation_parameters_json,
            context_configuration_json=None,
            signature_hash_hex="00" * 32,
        ),
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=3000,
            output_reserve=512,
            safety_margin=128,
        ),
        sections=(),
        included_refs=(),
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
            current_user_tokens=0,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=0,
            estimated_total_tokens=640,
        ),
        snapshot_commit_seq=0,
    )


def test_generation_temperature_contains_extreme_integer_overflow() -> None:
    package = _package('{"temperature":' + ("9" * 400) + "}")

    with pytest.raises(ContextPackageError, match="temperature must be finite"):
        package.generation_temperature()


@pytest.mark.parametrize("value", ["0", "0.5", "2"])
def test_generation_temperature_accepts_supported_boundaries(value: str) -> None:
    package = _package('{"temperature":' + value + "}")

    temperature = package.generation_temperature()

    assert temperature is not None
    assert 0.0 <= temperature <= 2.0
