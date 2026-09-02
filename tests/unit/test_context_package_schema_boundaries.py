from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any, cast

import pytest

from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextPackage,
    ContextPackageBudget,
    ContextPackageError,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _model_signature() -> ModelSignature:
    return ModelSignature(
        model_signature_id=uuid.UUID("12345678-1234-4234-8234-123456789abc"),
        provider="lm-studio",
        model_identifier="test-model",
        model_revision=None,
        quantization=None,
        generation_parameters_json="{}",
        context_configuration_json=None,
        signature_hash=b"\x00" * 32,
        created_at_us=0,
    )


def _build_structured_package(
    *,
    schema_id: object = "test.schema.v1",
    schema: object = None,
) -> ContextPackage:
    structured_schema = (
        {"type": "object", "properties": {"answer": {"type": "string"}}}
        if schema is None
        else schema
    )
    return ContextPackageService.build_from_sections(
        model_signature=_model_signature(),
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2048,
            output_reserve=1024,
            safety_margin=128,
        ),
        sections=(
            ContextSection(
                name="request",
                role="user",
                content="Return structured output.",
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
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=0,
            estimated_total_tokens=0,
        ),
        snapshot_commit_seq=0,
        structured_schema_id=cast(Any, schema_id),
        structured_schema=cast(Any, structured_schema),
    )


def test_structured_schema_valid_roundtrip_is_preserved() -> None:
    package = _build_structured_package()

    assert package.structured_schema() == {
        "properties": {"answer": {"type": "string"}},
        "type": "object",
    }
    assert package.structured_schema_id == "test.schema.v1"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_builder_rejects_non_finite_schema_numbers(value: float) -> None:
    with pytest.raises(ContextPackageError, match="strict JSON-serializable"):
        _build_structured_package(schema={"limit": value})


def test_builder_translates_non_serializable_schema_value() -> None:
    with pytest.raises(ContextPackageError, match="strict JSON-serializable"):
        _build_structured_package(schema={"sentinel": object()})


def test_builder_rejects_non_text_schema_id_with_contract_error() -> None:
    with pytest.raises(ContextPackageError, match="schema ID must be text"):
        _build_structured_package(schema_id=7)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_reader_rejects_non_standard_json_constants(constant: str) -> None:
    package = _build_structured_package()
    corrupted = replace(
        package,
        structured_schema_json=f'{{"limit":{constant}}}',
    )

    with pytest.raises(ContextPackageError, match="structured schema JSON is invalid"):
        corrupted.structured_schema()


@pytest.mark.parametrize(
    ("schema_id", "schema_json"),
    [("test.schema.v1", None), (None, '{"type":"object"}')],
)
def test_run_snapshot_rejects_half_present_schema_metadata(
    schema_id: str | None,
    schema_json: str | None,
) -> None:
    package = replace(
        _build_structured_package(),
        structured_schema_id=schema_id,
        structured_schema_json=schema_json,
    )

    with pytest.raises(ContextPackageError, match="requires both schema ID and schema JSON"):
        package.run_snapshot()


def test_reader_and_snapshot_reject_non_text_persisted_schema_json() -> None:
    package = replace(
        _build_structured_package(),
        structured_schema_json=cast(Any, 42),
    )

    with pytest.raises(ContextPackageError, match="metadata must be text"):
        package.structured_schema()
    with pytest.raises(ContextPackageError, match="metadata must be text"):
        package.run_snapshot()
