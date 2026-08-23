from __future__ import annotations

import uuid

import pytest

from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _signature(revision: str | None) -> ModelSignature:
    return ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=revision,
        quantization="Q4_K_M",
        generation_parameters_json='{"max_output_tokens":64,"reasoning_mode":"off"}',
        context_configuration_json=None,
        signature_hash=b"r" * 32,
        created_at_us=1,
    )


def _package(revision: str | None):
    return ContextPackageService.build_from_sections(
        model_signature=_signature(revision),
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=3500,
            output_reserve=64,
            safety_margin=128,
        ),
        sections=(
            ContextSection(
                name="system",
                role="system",
                content="system input",
                included_ref_ids=(),
            ),
        ),
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
            system_tokens=10,
            context_tokens=10,
            estimated_input_tokens=10,
            estimated_total_tokens=74,
        ),
        snapshot_commit_seq=0,
    )


@pytest.mark.parametrize("revision", [None, "build-2026-08-23.1"])
def test_context_package_preserves_model_revision(revision: str | None) -> None:
    package = _package(revision)

    assert package.model_signature.model_revision == revision
    assert package.run_snapshot()["model_signature"]["model_revision"] == revision
