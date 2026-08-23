from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.service import DurableJobService, InvalidJobPayloadError

ANALYSIS_ID = str(uuid.UUID("11111111-1111-4111-8111-111111111111"))
ARTIFACT_ID = str(uuid.UUID("22222222-2222-4222-8222-222222222222"))
SIGNATURE_ID = str(uuid.UUID("33333333-3333-4333-8333-333333333333"))


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
        self.calls.append(kwargs)
        return object()


def _source_extract_payload() -> tuple[dict[str, Any], dict[str, Any]]:
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


@pytest.mark.parametrize(
    "nested_value",
    [
        ("tuple-is-not-json",),
        {"set-is-not-json"},
        b"bytes-are-not-json",
        uuid.UUID("55555555-5555-4555-8555-555555555555"),
        float("nan"),
        float("inf"),
    ],
)
def test_nested_invalid_create_json_fails_before_actor_and_repository(
    nested_value: Any,
) -> None:
    scope, config = _source_extract_payload()
    # The source.extract contract intentionally treats model as an opaque,
    # non-empty object snapshot. The common durable JSON boundary must still
    # recursively reject values that JSON would coerce or cannot represent.
    config["model"] = {"id": "local-model", "nested": nested_value}
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


def test_valid_nested_model_snapshot_reaches_actor_and_repository_once() -> None:
    scope, config = _source_extract_payload()
    config["model"] = {
        "id": "local-model",
        "metadata": {"family": "local", "quantized": True},
        "aliases": ["primary", "analysis"],
    }
    chat = _Chat()
    repository = _Repository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]

    service.create(
        job_type="source.extract",
        requested_scope=scope,
        pinned_configuration=config,
    )

    assert chat.calls == 1
    assert len(repository.calls) == 1
