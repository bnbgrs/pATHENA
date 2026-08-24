from __future__ import annotations

import copy
import math
import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

ANALYSIS_ID = str(uuid.UUID("11111111-1111-4111-8111-111111111111"))
ARTIFACT_ID = str(uuid.UUID("22222222-2222-4222-8222-222222222222"))
SIGNATURE_ID = str(uuid.UUID("33333333-3333-4333-8333-333333333333"))


def _valid() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"analysis_id": ANALYSIS_ID, "final_artifact_id": ARTIFACT_ID},
        {
            "pipeline_version": "source-analysis-knowledge-extraction/3",
            "model_id": "local-model",
            "model_signature_id": SIGNATURE_ID,
            "model_signature_sha256": "ab" * 32,
            "model": {"id": "local-model"},
            "effective_context_limit": 8192,
            "provider_context_length": 8192,
            "output_reserve": 2048,
            "safety_margin": 256,
            "token_estimator": "utf8-bytes-div3-v1",
            "max_hierarchy_depth": 16,
            "prompt_template_id": "athena.source_analysis_knowledge_extraction_hierarchical",
            "prompt_template_version": "6",
            "source_extraction_schema_id": "athena_source_analysis_knowledge_extraction_v1",
            "merge_schema_id": "athena_source_extraction_semantic_dedup_v3",
            "pair_audit_schema_id": "athena_source_extraction_pair_batch_audit_v1",
            "provider_transport": "lmstudio-controlled-structured-v1",
            "reasoning_mode": "off",
            "temperature": 0.0,
            "top_p": 0.95,
            "top_k": 40,
            "min_p": 0.05,
            "repeat_penalty": 1.1,
            "store": False,
            "structured_contract_version": "athena.controlled_structured_json/1",
            "structured_validation": "athena_stage_parser_v1",
            "provider_instance_policy": "initial_context_then_runtime_instance_reuse_v1",
        },
    )


def _mutate(
    side: str,
    field: str | None,
    value: Any,
    *,
    delete: bool = False,
    add: bool = False,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    scope, config = _valid()
    target = scope if side == "scope" else config
    if field is None:
        if side == "scope":
            scope = value
        else:
            config = value
    elif delete:
        target.pop(field, None)
    elif add:
        target[field] = value
    else:
        target[field] = value
    return scope, config


CASES = [
    pytest.param(*_mutate("scope", None, None), id="scope-required"),
    pytest.param(*_mutate("scope", "analysis_id", None, delete=True), id="analysis-required"),
    pytest.param(*_mutate("scope", "final_artifact_id", None, delete=True), id="artifact-required"),
    pytest.param(*_mutate("scope", "extra", 1, add=True), id="scope-extra"),
    pytest.param(*_mutate("scope", "analysis_id", "bad"), id="analysis-uuid"),
    pytest.param(*_mutate("scope", "final_artifact_id", "bad"), id="artifact-uuid"),
    pytest.param(*_mutate("config", None, None), id="config-required"),
    pytest.param(*_mutate("config", "pipeline_version", None, delete=True), id="config-missing"),
    pytest.param(*_mutate("config", "extra", 1, add=True), id="config-extra"),
    pytest.param(*_mutate("config", "pipeline_version", "source-analysis-knowledge-extraction/2"), id="pipeline"),
    pytest.param(*_mutate("config", "model_id", ""), id="model-id"),
    pytest.param(*_mutate("config", "model_signature_id", "bad"), id="signature-uuid"),
    pytest.param(*_mutate("config", "model_signature_sha256", "zz" * 32), id="signature-hex"),
    pytest.param(*_mutate("config", "model_signature_sha256", "ab" * 31), id="signature-length"),
    pytest.param(*_mutate("config", "model", {}), id="model-empty"),
    pytest.param(*_mutate("config", "model", "not-object"), id="model-type"),
    pytest.param(*_mutate("config", "effective_context_limit", True), id="context-bool"),
    pytest.param(*_mutate("config", "effective_context_limit", 63), id="context-minimum"),
    pytest.param(*_mutate("config", "provider_context_length", 4096), id="provider-context-match"),
    pytest.param(*_mutate("config", "output_reserve", False), id="reserve-bool"),
    pytest.param(*_mutate("config", "output_reserve", 0), id="reserve-positive"),
    pytest.param(*_mutate("config", "safety_margin", True), id="margin-bool"),
    pytest.param(*_mutate("config", "safety_margin", -1), id="margin-nonnegative"),
    pytest.param(*_mutate("config", "effective_context_limit", 2304), id="budget-positive"),
    pytest.param(*_mutate("config", "max_hierarchy_depth", False), id="depth-bool"),
    pytest.param(*_mutate("config", "max_hierarchy_depth", 0), id="depth-positive"),
    pytest.param(*_mutate("config", "token_estimator", "other"), id="token-estimator"),
    pytest.param(*_mutate("config", "prompt_template_id", "other"), id="prompt-id"),
    pytest.param(*_mutate("config", "prompt_template_version", "5"), id="prompt-version"),
    pytest.param(*_mutate("config", "source_extraction_schema_id", "other"), id="extraction-schema"),
    pytest.param(*_mutate("config", "merge_schema_id", "other"), id="merge-schema"),
    pytest.param(*_mutate("config", "pair_audit_schema_id", "other"), id="audit-schema"),
    pytest.param(*_mutate("config", "provider_transport", ""), id="transport-empty"),
    pytest.param(*_mutate("config", "reasoning_mode", "on"), id="reasoning"),
    pytest.param(*_mutate("config", "temperature", True), id="temperature-bool"),
    pytest.param(*_mutate("config", "temperature", math.inf), id="temperature-finite"),
    pytest.param(*_mutate("config", "temperature", 0.2), id="temperature-pinned"),
    pytest.param(*_mutate("config", "top_p", 0.9), id="top-p"),
    pytest.param(*_mutate("config", "top_k", True), id="top-k-bool"),
    pytest.param(*_mutate("config", "top_k", 41), id="top-k-pinned"),
    pytest.param(*_mutate("config", "min_p", 0.0), id="min-p"),
    pytest.param(*_mutate("config", "repeat_penalty", 1.0), id="repeat-penalty"),
    pytest.param(*_mutate("config", "store", 0), id="store-type"),
    pytest.param(*_mutate("config", "store", True), id="store-pinned"),
    pytest.param(*_mutate("config", "structured_contract_version", "other"), id="structured-contract"),
    pytest.param(*_mutate("config", "structured_validation", "other"), id="structured-validation"),
    pytest.param(*_mutate("config", "provider_instance_policy", "other"), id="provider-instance-policy"),
]


@pytest.mark.parametrize("scope,config", CASES)
def test_source_extract_payload_rejects_each_invalid_contract(
    scope: dict[str, Any] | None,
    config: dict[str, Any] | None,
) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            "source.extract",
            requested_scope=scope,
            pinned_configuration=config,
        )


def test_source_extract_payload_accepts_current_pinned_contract() -> None:
    scope, config = _valid()
    validate_builtin_job_payload(
        "source.extract",
        requested_scope=scope,
        pinned_configuration=config,
    )


@dataclass
class _Chat:
    calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.calls += 1
        return uuid.UUID("44444444-4444-4444-8444-444444444444")


@dataclass
class _Repository:
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> object:
        self.calls.append(copy.deepcopy(kwargs))
        return object()


@pytest.mark.parametrize("scope,config", CASES)
def test_source_extract_invalid_contract_never_reaches_actor_or_repository(
    scope: dict[str, Any] | None,
    config: dict[str, Any] | None,
) -> None:
    chat = _Chat()
    repository = _Repository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type="source.extract",
            requested_scope=scope,
            pinned_configuration=config,
        )

    assert chat.calls == 0
    assert repository.calls == []
