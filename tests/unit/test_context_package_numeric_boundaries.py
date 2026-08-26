from __future__ import annotations

import json
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


def _package_with_generation_parameters(parameters: dict[str, object]) -> ContextPackage:
    return ContextPackage(
        request_id=uuid.UUID("12345678-1234-4234-8234-123456789abc"),
        model_signature=ContextModelSignature(
            model_signature_id=uuid.UUID("22345678-1234-4234-8234-123456789abc"),
            provider="lm-studio",
            model_identifier="test-model",
            model_revision=None,
            quantization=None,
            generation_parameters_json=json.dumps(parameters),
            context_configuration_json=None,
            signature_hash_hex="00" * 32,
        ),
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2048,
            output_reserve=1024,
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
            estimated_total_tokens=0,
        ),
        snapshot_commit_seq=0,
    )


def test_generation_temperature_translates_huge_integer_overflow() -> None:
    package = _package_with_generation_parameters({"temperature": 10**400})

    with pytest.raises(ContextPackageError, match="finite and between"):
        package.generation_temperature()


def test_generation_temperature_preserves_finite_values() -> None:
    package = _package_with_generation_parameters({"temperature": 0.75})

    assert package.generation_temperature() == 0.75
