from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.service import DurableJobService, InvalidJobPayloadError


SOURCE_ID = str(uuid.UUID("11111111-1111-4111-8111-111111111111"))
REPRESENTATION_ID = str(uuid.UUID("22222222-2222-4222-8222-222222222222"))
WORK_ID = str(uuid.UUID("33333333-3333-4333-8333-333333333333"))
MODEL_SIGNATURE_ID = str(uuid.UUID("44444444-4444-4444-8444-444444444444"))
TARGET_ID = str(uuid.UUID("55555555-5555-4555-8555-555555555555"))


def _source_process() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"source_id": SOURCE_ID},
        {
            "pipeline_version": "source-process-v2",
            "text_parser": "athena.native_text@1",
            "pdf_parser": "pdf@1",
            "docx_parser": "docx@1",
            "html_parser": "html@1",
            "chunking_profile": "default",
            "chunk_batch_size": 32,
            "embedding_policy": "deferred",
        },
    )


def _source_analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "source_id": SOURCE_ID,
            "representation_id": REPRESENTATION_ID,
            "question": "What does the source establish?",
        },
        {
            "pipeline_version": "source-analysis-v1",
            "model_id": "local-model",
            "model_signature_id": MODEL_SIGNATURE_ID,
            "model_signature_sha256": "ab" * 32,
            "effective_context_limit": 8192,
            "output_reserve": 2048,
            "safety_margin": 256,
            "token_estimator": "utf8-bytes-div3-v1",
            "max_hierarchy_depth": 12,
            "prompt_template_id": "athena.source_analysis",
            "prompt_template_version": "1",
        },
    )


def _backup_create() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"schedule_slot_us": 123456789, "target_id": TARGET_ID},
        {"pipeline_version": "backup-scheduler-v1", "quiet_hour_utc": 3},
    )


def _archive_replicate() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"target_role": "archive_root"},
        {"pipeline_version": "archive-replication-v1", "storage_retry_seconds": 60},
    )


VALID = {
    "source.process": _source_process,
    "source.analyze": _source_analyze,
    "backup.create": _backup_create,
    "archive.replicate": _archive_replicate,
}


def _case(
    job_type: str,
    side: str,
    field: str | None,
    value: Any,
    *,
    delete: bool = False,
    add: bool = False,
) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    scope, config = VALID[job_type]()
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
    return job_type, scope, config


INVALID_CASES = [
    pytest.param(*_case("source.process", "scope", None, None), id="process-scope-required"),
    pytest.param(*_case("source.process", "scope", "source_id", None, delete=True), id="process-source-required"),
    pytest.param(*_case("source.process", "scope", "extra", 1, add=True), id="process-scope-extra"),
    pytest.param(*_case("source.process", "scope", "source_id", "not-a-uuid"), id="process-source-uuid"),
    pytest.param(*_case("source.process", "scope", "source_id", SOURCE_ID.upper()), id="process-source-canonical-uuid"),
    pytest.param(*_case("source.process", "scope", "research_work_item_id", "bad", add=True), id="process-research-uuid"),
    pytest.param(*_case("source.process", "config", None, None), id="process-config-required"),
    pytest.param(*_case("source.process", "config", "pipeline_version", None, delete=True), id="process-config-missing"),
    pytest.param(*_case("source.process", "config", "extra", "x", add=True), id="process-config-extra"),
    pytest.param(*_case("source.process", "config", "pipeline_version", "source-process-v1"), id="process-pipeline"),
    pytest.param(*_case("source.process", "config", "text_parser", "other@1"), id="process-text-parser"),
    pytest.param(*_case("source.process", "config", "pdf_parser", ""), id="process-pdf-parser-empty"),
    pytest.param(*_case("source.process", "config", "docx_parser", "   "), id="process-docx-parser-empty"),
    pytest.param(*_case("source.process", "config", "html_parser", 9), id="process-html-parser-type"),
    pytest.param(*_case("source.process", "config", "chunking_profile", "other"), id="process-chunk-profile"),
    pytest.param(*_case("source.process", "config", "chunk_batch_size", True), id="process-batch-bool"),
    pytest.param(*_case("source.process", "config", "chunk_batch_size", 0), id="process-batch-positive"),
    pytest.param(*_case("source.process", "config", "chunk_batch_size", 31), id="process-batch-pinned"),
    pytest.param(*_case("source.process", "config", "embedding_policy", "eager"), id="process-embedding-policy"),
    pytest.param(*_case("source.analyze", "scope", None, None), id="analyze-scope-required"),
    pytest.param(*_case("source.analyze", "scope", "source_id", None, delete=True), id="analyze-source-required"),
    pytest.param(*_case("source.analyze", "scope", "representation_id", None, delete=True), id="analyze-representation-required"),
    pytest.param(*_case("source.analyze", "scope", "question", None, delete=True), id="analyze-question-required"),
    pytest.param(*_case("source.analyze", "scope", "extra", 1, add=True), id="analyze-scope-extra"),
    pytest.param(*_case("source.analyze", "scope", "source_id", "bad"), id="analyze-source-uuid"),
    pytest.param(*_case("source.analyze", "scope", "representation_id", "bad"), id="analyze-representation-uuid"),
    pytest.param(*_case("source.analyze", "scope", "research_work_item_id", "bad", add=True), id="analyze-research-uuid"),
    pytest.param(*_case("source.analyze", "scope", "question", ""), id="analyze-question-empty"),
    pytest.param(*_case("source.analyze", "scope", "question", " padded "), id="analyze-question-canonical"),
    pytest.param(*_case("source.analyze", "config", None, None), id="analyze-config-required"),
    pytest.param(*_case("source.analyze", "config", "pipeline_version", None, delete=True), id="analyze-config-missing"),
    pytest.param(*_case("source.analyze", "config", "extra", 1, add=True), id="analyze-config-extra"),
    pytest.param(*_case("source.analyze", "config", "pipeline_version", "source-analysis-v2"), id="analyze-pipeline"),
    pytest.param(*_case("source.analyze", "config", "model_id", ""), id="analyze-model-empty"),
    pytest.param(*_case("source.analyze", "config", "model_signature_id", "bad"), id="analyze-signature-uuid"),
    pytest.param(*_case("source.analyze", "config", "model_signature_sha256", "zz" * 32), id="analyze-signature-hex"),
    pytest.param(*_case("source.analyze", "config", "model_signature_sha256", "ab" * 31), id="analyze-signature-length"),
    pytest.param(*_case("source.analyze", "config", "model_signature_sha256", "AB" * 32), id="analyze-signature-case"),
    pytest.param(*_case("source.analyze", "config", "effective_context_limit", True), id="analyze-context-bool"),
    pytest.param(*_case("source.analyze", "config", "effective_context_limit", 63), id="analyze-context-minimum"),
    pytest.param(*_case("source.analyze", "config", "output_reserve", False), id="analyze-reserve-bool"),
    pytest.param(*_case("source.analyze", "config", "output_reserve", 0), id="analyze-reserve-positive"),
    pytest.param(*_case("source.analyze", "config", "safety_margin", True), id="analyze-margin-bool"),
    pytest.param(*_case("source.analyze", "config", "safety_margin", -1), id="analyze-margin-nonnegative"),
    pytest.param(*_case("source.analyze", "config", "max_hierarchy_depth", False), id="analyze-depth-bool"),
    pytest.param(*_case("source.analyze", "config", "max_hierarchy_depth", 0), id="analyze-depth-positive"),
    pytest.param(*_case("source.analyze", "config", "effective_context_limit", 2304), id="analyze-budget-zero"),
    pytest.param(*_case("source.analyze", "config", "token_estimator", "other"), id="analyze-token-estimator"),
    pytest.param(*_case("source.analyze", "config", "prompt_template_id", "other"), id="analyze-prompt-id"),
    pytest.param(*_case("source.analyze", "config", "prompt_template_version", "2"), id="analyze-prompt-version"),
    pytest.param(*_case("backup.create", "scope", None, None), id="backup-scope-required"),
    pytest.param(*_case("backup.create", "scope", "target_id", None, delete=True), id="backup-target-required"),
    pytest.param(*_case("backup.create", "scope", "schedule_slot_us", None, delete=True), id="backup-slot-required"),
    pytest.param(*_case("backup.create", "scope", "extra", 1, add=True), id="backup-scope-extra"),
    pytest.param(*_case("backup.create", "scope", "target_id", "bad"), id="backup-target-uuid"),
    pytest.param(*_case("backup.create", "scope", "schedule_slot_us", True), id="backup-slot-bool"),
    pytest.param(*_case("backup.create", "scope", "schedule_slot_us", -1), id="backup-slot-nonnegative"),
    pytest.param(*_case("backup.create", "config", None, None), id="backup-config-required"),
    pytest.param(*_case("backup.create", "config", "pipeline_version", "other"), id="backup-pipeline"),
    pytest.param(*_case("backup.create", "config", "quiet_hour_utc", True), id="backup-hour-bool"),
    pytest.param(*_case("backup.create", "config", "quiet_hour_utc", -1), id="backup-hour-min"),
    pytest.param(*_case("backup.create", "config", "quiet_hour_utc", 24), id="backup-hour-max"),
    pytest.param(*_case("archive.replicate", "scope", None, None), id="archive-scope-required"),
    pytest.param(*_case("archive.replicate", "scope", "target_role", "other"), id="archive-role"),
    pytest.param(*_case("archive.replicate", "scope", "extra", 1, add=True), id="archive-scope-extra"),
    pytest.param(*_case("archive.replicate", "config", None, None), id="archive-config-required"),
    pytest.param(*_case("archive.replicate", "config", "pipeline_version", "other"), id="archive-pipeline"),
    pytest.param(*_case("archive.replicate", "config", "storage_retry_seconds", True), id="archive-retry-bool"),
    pytest.param(*_case("archive.replicate", "config", "storage_retry_seconds", 0), id="archive-retry-positive"),
]


@pytest.mark.parametrize("job_type,scope,config", INVALID_CASES)
def test_builtin_payload_validator_rejects_each_invalid_contract(
    job_type: str,
    scope: dict[str, Any] | None,
    config: dict[str, Any] | None,
) -> None:
    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            job_type,
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize("job_type,factory", tuple(VALID.items()))
def test_builtin_payload_validator_accepts_current_worker_contract(
    job_type: str,
    factory,
) -> None:
    scope, config = factory()
    validate_builtin_job_payload(
        job_type,
        requested_scope=scope,
        pinned_configuration=config,
    )


def test_source_process_accepts_optional_research_work_item() -> None:
    scope, config = _source_process()
    scope["research_work_item_id"] = WORK_ID
    validate_builtin_job_payload(
        "source.process",
        requested_scope=scope,
        pinned_configuration=config,
    )


def test_source_analyze_accepts_optional_research_work_item() -> None:
    scope, config = _source_analyze()
    scope["research_work_item_id"] = WORK_ID
    validate_builtin_job_payload(
        "source.analyze",
        requested_scope=scope,
        pinned_configuration=config,
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


@pytest.mark.parametrize("job_type,scope,config", INVALID_CASES)
def test_durable_job_service_rejects_invalid_builtin_before_actor_or_write(
    job_type: str,
    scope: dict[str, Any] | None,
    config: dict[str, Any] | None,
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


@pytest.mark.parametrize("job_type,factory", tuple(VALID.items()))
def test_durable_job_service_persists_valid_contract_as_canonical_json(
    job_type: str,
    factory,
) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = factory()

    service.create(
        job_type=job_type,
        priority=JobPriority.NORMAL,
        requested_scope=scope,
        pinned_configuration=config,
    )

    assert chat.actor_calls == 1
    assert len(repository.create_calls) == 1
    persisted = repository.create_calls[0]
    assert json.loads(persisted["requested_scope_json"]) == scope
    assert json.loads(persisted["pinned_configuration_json"]) == config
