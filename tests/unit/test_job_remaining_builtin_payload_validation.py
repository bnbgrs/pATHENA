from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

import pytest

from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

MODEL_SIGNATURE_ID = str(uuid.UUID("44444444-4444-4444-8444-444444444444"))
PROJECT_ID = str(uuid.UUID("11111111-1111-4111-8111-111111111111"))
SOURCE_ID = str(uuid.UUID("22222222-2222-4222-8222-222222222222"))
PayloadFactory = Callable[[], tuple[dict[str, Any], dict[str, Any]]]


def _embedding_rebuild() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"model_id": "local-embedding-model"},
        {
            "pipeline_version": "embedding-rebuild-v1",
            "model_id": "local-embedding-model",
            "model_signature_id": MODEL_SIGNATURE_ID,
            "model_signature_sha256": "ab" * 32,
            "corpus": "active-semantic-chunks",
        },
    )


def _research_exhaustive() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "mode": "local_exhaustive",
            "query": "What evidence supports the claim?",
            "domains": ["Example.com", "example.org"],
            "project_ids": [PROJECT_ID],
            "source_types": ["document", "web_snapshot"],
            "explicit_source_ids": [SOURCE_ID],
            "time_start_us": 0,
            "time_end_us": 1_000_000,
            "internet_scope": None,
            "coverage_target": 0.85,
        },
        {
            "pipeline_version": "exhaustive-research-orchestration-v2",
            "snapshot_commit_seq": 42,
            "coverage_formula_id": "eligible-success-or-irrelevant-v1",
            "candidate_dedup_id": "source-content-sha256-v1",
            "requested_model_id": "local-research-model",
            "context_limit": 32768,
            "output_reserve": 4096,
            "safety_margin": 512,
            "max_hierarchy_depth": 12,
        },
    )


def _mutate(
    factory: PayloadFactory,
    side: str,
    field: str,
    value: Any,
    *,
    add: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    scope, config = factory()
    target = scope if side == "scope" else config
    target[field] = value
    if add:
        assert field not in (set(scope) if target is config else set(config))
    return scope, config


EMBEDDING_INVALID = [
    pytest.param(*_mutate(_embedding_rebuild, "scope", "model_id", ""), id="model-empty"),
    pytest.param(*_mutate(_embedding_rebuild, "scope", "extra", 1, add=True), id="scope-extra"),
    pytest.param(*_mutate(_embedding_rebuild, "config", "pipeline_version", "v0"), id="pipeline"),
    pytest.param(*_mutate(_embedding_rebuild, "config", "model_id", "other"), id="model-mismatch"),
    pytest.param(*_mutate(_embedding_rebuild, "config", "model_signature_id", "bad"), id="signature-id"),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "model_signature_sha256", "zz" * 32),
        id="signature-hex",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "model_signature_sha256", "ab" * 31),
        id="signature-length",
    ),
    pytest.param(*_mutate(_embedding_rebuild, "config", "corpus", "other"), id="corpus"),
    pytest.param(*_mutate(_embedding_rebuild, "config", "extra", True, add=True), id="config-extra"),
]


RESEARCH_INVALID = [
    pytest.param(*_mutate(_research_exhaustive, "scope", "mode", "local_plus_web"), id="mode"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "query", ""), id="query-empty"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "query", " padded "), id="query-canonical"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "domains", "example.com"), id="domains-type"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "domains", [" padded "]), id="domains-canonical"),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "domains", ["example.org", "Example.com"]),
        id="domains-order",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "domains", ["Example.com", "Example.com"]),
        id="domains-duplicate",
    ),
    pytest.param(*_mutate(_research_exhaustive, "scope", "project_ids", ["bad"]), id="project-id"),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "project_ids", [PROJECT_ID.upper()]),
        id="project-id-canonical",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "source_types", ["web_snapshot", "document"]),
        id="source-type-order",
    ),
    pytest.param(*_mutate(_research_exhaustive, "scope", "source_types", ["unknown"]), id="source-type-enum"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "explicit_source_ids", ["bad"]), id="source-id"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "time_start_us", True), id="start-bool"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "time_end_us", -1), id="end-negative"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "time_end_us", 0), id="time-order"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "internet_scope", {}), id="internet-scope"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "coverage_target", True), id="coverage-bool"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "coverage_target", 1), id="coverage-int"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "coverage_target", 0.0), id="coverage-zero"),
    pytest.param(*_mutate(_research_exhaustive, "scope", "coverage_target", 1.01), id="coverage-high"),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "coverage_target", float("nan")),
        id="coverage-nan",
    ),
    pytest.param(*_mutate(_research_exhaustive, "scope", "extra", 1, add=True), id="scope-extra"),
    pytest.param(*_mutate(_research_exhaustive, "config", "pipeline_version", "v1"), id="pipeline"),
    pytest.param(*_mutate(_research_exhaustive, "config", "snapshot_commit_seq", True), id="snapshot-bool"),
    pytest.param(*_mutate(_research_exhaustive, "config", "snapshot_commit_seq", -1), id="snapshot-negative"),
    pytest.param(*_mutate(_research_exhaustive, "config", "coverage_formula_id", "other"), id="coverage-formula"),
    pytest.param(*_mutate(_research_exhaustive, "config", "candidate_dedup_id", "other"), id="candidate-dedup"),
    pytest.param(*_mutate(_research_exhaustive, "config", "requested_model_id", ""), id="model-empty"),
    pytest.param(*_mutate(_research_exhaustive, "config", "requested_model_id", " padded "), id="model-canonical"),
    pytest.param(*_mutate(_research_exhaustive, "config", "context_limit", True), id="context-bool"),
    pytest.param(*_mutate(_research_exhaustive, "config", "context_limit", 0), id="context-zero"),
    pytest.param(*_mutate(_research_exhaustive, "config", "output_reserve", False), id="reserve-bool"),
    pytest.param(*_mutate(_research_exhaustive, "config", "output_reserve", 0), id="reserve-zero"),
    pytest.param(*_mutate(_research_exhaustive, "config", "safety_margin", True), id="margin-bool"),
    pytest.param(*_mutate(_research_exhaustive, "config", "safety_margin", -1), id="margin-negative"),
    pytest.param(*_mutate(_research_exhaustive, "config", "max_hierarchy_depth", False), id="depth-bool"),
    pytest.param(*_mutate(_research_exhaustive, "config", "max_hierarchy_depth", 0), id="depth-zero"),
    pytest.param(*_mutate(_research_exhaustive, "config", "extra", 1, add=True), id="config-extra"),
]


@pytest.mark.parametrize("scope,config", EMBEDDING_INVALID)
def test_embedding_rebuild_rejects_malformed_persistent_contract(
    scope: dict[str, Any], config: dict[str, Any]
) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            "embedding.rebuild",
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize("scope,config", RESEARCH_INVALID)
def test_research_exhaustive_rejects_malformed_persistent_contract(
    scope: dict[str, Any], config: dict[str, Any]
) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            "research.exhaustive",
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize(
    "job_type,factory",
    [
        pytest.param("embedding.rebuild", _embedding_rebuild, id="embedding"),
        pytest.param("research.exhaustive", _research_exhaustive, id="research"),
    ],
)
def test_remaining_executable_builtin_contracts_accept_current_payload(
    job_type: str, factory: PayloadFactory
) -> None:
    scope, config = factory()
    validate_builtin_job_payload(
        job_type,
        requested_scope=scope,
        pinned_configuration=config,
    )


def test_research_exhaustive_accepts_nullable_current_options_and_empty_filters() -> None:
    scope, config = _research_exhaustive()
    scope["domains"] = []
    scope["project_ids"] = []
    scope["source_types"] = []
    scope["explicit_source_ids"] = []
    scope["time_start_us"] = None
    scope["time_end_us"] = None
    config["requested_model_id"] = None
    config["context_limit"] = None
    config["output_reserve"] = None
    config["safety_margin"] = None

    validate_builtin_job_payload(
        "research.exhaustive",
        requested_scope=scope,
        pinned_configuration=config,
    )


UNSUPPORTED = (
    "source.represent",
    "source.chunk",
    "search.rebuild",
    "integrity.sweep",
)


@pytest.mark.parametrize("job_type", UNSUPPORTED)
def test_registered_builtins_without_executable_worker_are_fail_closed(job_type: str) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError, match="no executable durable worker"):
        validate_builtin_job_payload(
            job_type,
            requested_scope={},
            pinned_configuration={},
        )


@dataclass
class _FakeChat:
    actor_calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.actor_calls += 1
        return uuid.UUID("66666666-6666-4666-8666-666666666666")


@dataclass
class _FakeRepository:
    create_calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> object:
        self.create_calls.append(copy.deepcopy(kwargs))
        return object()


def _service_invalid_cases() -> list[Any]:
    embedding_scope, embedding_config = _embedding_rebuild()
    embedding_scope["model_id"] = ""
    research_scope, research_config = _research_exhaustive()
    research_scope["coverage_target"] = True
    return [
        pytest.param("embedding.rebuild", embedding_scope, embedding_config, id="embedding"),
        pytest.param("research.exhaustive", research_scope, research_config, id="research-bool"),
        *[pytest.param(job_type, {}, {}, id=job_type) for job_type in UNSUPPORTED],
    ]


@pytest.mark.parametrize("job_type,scope,config", _service_invalid_cases())
def test_remaining_builtin_failures_happen_before_actor_or_repository_write(
    job_type: str,
    scope: dict[str, Any],
    config: dict[str, Any],
) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=job_type,
            requested_scope=scope,
            pinned_configuration=config,
        )

    assert chat.actor_calls == 0
    assert repository.create_calls == []


@pytest.mark.parametrize(
    "job_type,factory",
    [
        pytest.param("embedding.rebuild", _embedding_rebuild, id="embedding"),
        pytest.param("research.exhaustive", _research_exhaustive, id="research"),
    ],
)
def test_remaining_valid_builtin_contracts_persist_canonical_json(
    job_type: str, factory: PayloadFactory
) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = factory()

    service.create(
        job_type=job_type,
        requested_scope=scope,
        pinned_configuration=config,
    )

    assert chat.actor_calls == 1
    assert len(repository.create_calls) == 1
    persisted = repository.create_calls[0]
    assert json.loads(persisted["requested_scope_json"]) == scope
    assert json.loads(persisted["pinned_configuration_json"]) == config
