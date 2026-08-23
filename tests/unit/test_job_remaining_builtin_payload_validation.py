from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

MODEL_SIGNATURE_ID = str(uuid.UUID("44444444-4444-4444-8444-444444444444"))
SOURCE_ID = str(uuid.UUID("11111111-1111-4111-8111-111111111111"))


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
            "query": "What evidence supports the claim?",
            "coverage_threshold": 0.85,
            "time_limit_seconds": 3600,
            "source_domains": ["example.com"],
            "source_ids": [SOURCE_ID],
            "source_types": ["document", "web_snapshot"],
            "retrieval_limit": 100,
            "candidate_limit": 500,
        },
        {
            "pipeline_version": "research-exhaustive-v1",
            "model_id": "local-research-model",
            "model_signature_id": MODEL_SIGNATURE_ID,
            "model_signature_sha256": "cd" * 32,
            "effective_context_limit": 32768,
            "output_reserve": 4096,
            "safety_margin": 512,
            "token_estimator": "utf8-bytes-div3-v1",
            "max_hierarchy_depth": 12,
        },
    )


def _mutate(
    factory,
    side: str,
    field: str,
    value: Any,
    *,
    delete: bool = False,
    add: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    scope, config = factory()
    target = scope if side == "scope" else config
    if delete:
        target.pop(field, None)
    elif add:
        target[field] = value
    else:
        target[field] = value
    return scope, config


EMBEDDING_INVALID = [
    pytest.param(
        *_mutate(_embedding_rebuild, "scope", "model_id", ""),
        id="scope-model-empty",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "scope", "extra", 1, add=True),
        id="scope-extra",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "pipeline_version", "v0"),
        id="pipeline",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "model_id", "other"),
        id="model-mismatch",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "model_signature_id", "bad"),
        id="signature-id",
    ),
    pytest.param(
        *_mutate(
            _embedding_rebuild,
            "config",
            "model_signature_sha256",
            "zz" * 32,
        ),
        id="signature-hex",
    ),
    pytest.param(
        *_mutate(
            _embedding_rebuild,
            "config",
            "model_signature_sha256",
            "ab" * 31,
        ),
        id="signature-length",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "corpus", "other"),
        id="corpus",
    ),
    pytest.param(
        *_mutate(_embedding_rebuild, "config", "extra", True, add=True),
        id="config-extra",
    ),
]


RESEARCH_INVALID = [
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "query", ""),
        id="query-empty",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "query", " padded "),
        id="query-canonical",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "coverage_threshold", True),
        id="coverage-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "coverage_threshold", 1),
        id="coverage-int",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "coverage_threshold", 0.0),
        id="coverage-zero",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "coverage_threshold", 1.01),
        id="coverage-high",
    ),
    pytest.param(
        *_mutate(
            _research_exhaustive,
            "scope",
            "coverage_threshold",
            float("nan"),
        ),
        id="coverage-nan",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "time_limit_seconds", False),
        id="time-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "time_limit_seconds", 0),
        id="time-zero",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "source_domains", "example.com"),
        id="domains-type",
    ),
    pytest.param(
        *_mutate(
            _research_exhaustive,
            "scope",
            "source_domains",
            [" Example.com"],
        ),
        id="domains-canonical",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "source_ids", ["bad"]),
        id="source-id",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "source_types", ["DOCUMENT"]),
        id="source-type-canonical",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "source_types", ["unknown"]),
        id="source-type-enum",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "retrieval_limit", True),
        id="retrieval-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "candidate_limit", 0),
        id="candidate-zero",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "scope", "extra", 1, add=True),
        id="scope-extra",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "pipeline_version", "v0"),
        id="pipeline",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "model_id", ""),
        id="model-empty",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "model_signature_id", "bad"),
        id="signature-id",
    ),
    pytest.param(
        *_mutate(
            _research_exhaustive,
            "config",
            "model_signature_sha256",
            "CD" * 32,
        ),
        id="signature-case",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "effective_context_limit", True),
        id="context-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "effective_context_limit", 63),
        id="context-min",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "output_reserve", False),
        id="reserve-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "safety_margin", True),
        id="margin-bool",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "max_hierarchy_depth", 0),
        id="depth-zero",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "effective_context_limit", 4608),
        id="budget-zero",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "token_estimator", "other"),
        id="token-estimator",
    ),
    pytest.param(
        *_mutate(_research_exhaustive, "config", "extra", 1, add=True),
        id="config-extra",
    ),
]


@pytest.mark.parametrize("scope,config", EMBEDDING_INVALID)
def test_embedding_rebuild_rejects_malformed_persistent_contract(
    scope: dict[str, Any],
    config: dict[str, Any],
) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            "embedding.rebuild",
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize("scope,config", RESEARCH_INVALID)
def test_research_exhaustive_rejects_malformed_persistent_contract(
    scope: dict[str, Any],
    config: dict[str, Any],
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
    job_type: str,
    factory,
) -> None:
    scope, config = factory()
    validate_builtin_job_payload(
        job_type,
        requested_scope=scope,
        pinned_configuration=config,
    )


def test_research_exhaustive_accepts_unlimited_time_and_empty_filters() -> None:
    scope, config = _research_exhaustive()
    scope["time_limit_seconds"] = None
    scope["source_domains"] = []
    scope["source_ids"] = []
    scope["source_types"] = []

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
def test_registered_builtins_without_executable_worker_are_fail_closed(
    job_type: str,
) -> None:
    with pytest.raises(
        BuiltinJobPayloadValidationError,
        match="no executable durable worker",
    ):
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
    research_scope["coverage_threshold"] = True
    return [
        pytest.param(
            "embedding.rebuild",
            embedding_scope,
            embedding_config,
            id="embedding",
        ),
        pytest.param(
            "research.exhaustive",
            research_scope,
            research_config,
            id="research-bool",
        ),
        *[
            pytest.param(job_type, {}, {}, id=job_type)
            for job_type in UNSUPPORTED
        ],
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
    job_type: str,
    factory,
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
