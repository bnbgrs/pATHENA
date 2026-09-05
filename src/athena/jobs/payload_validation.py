"""Fail-closed validation for durable built-in job payloads.

This module is deliberately dependency-light so the application-facing job service can
reject malformed persistent work before actor creation or repository writes. Workers
still re-validate their own runtime contracts; this boundary prevents invalid new jobs
from entering durable state in the first place.
"""

from __future__ import annotations

import math
import uuid
from collections.abc import Mapping
from typing import Any


class BuiltinJobPayloadValidationError(ValueError):
    """Raised when a built-in durable job payload is not persistence-safe."""


_NON_EXECUTABLE_BUILTIN_JOB_TYPES = frozenset(
    {
        "source.represent",
        "source.chunk",
        "search.rebuild",
        "integrity.sweep",
    }
)

_RESEARCH_SOURCE_TYPES = frozenset(
    {
        "file",
        "web_snapshot",
        "email",
        "text",
        "image",
        "audio",
        "video",
        "document",
        "api_capture",
        "chat_export",
        "other",
    }
)


def validate_builtin_job_payload(
    job_type: str,
    *,
    requested_scope: Mapping[str, Any] | None,
    pinned_configuration: Mapping[str, Any] | None,
) -> None:
    if job_type == "source.process":
        _validate_source_process(requested_scope, pinned_configuration)
    elif job_type == "source.analyze":
        _validate_source_analyze(requested_scope, pinned_configuration)
    elif job_type == "source.extract":
        _validate_source_extract(requested_scope, pinned_configuration)
    elif job_type == "embedding.rebuild":
        _validate_embedding_rebuild(requested_scope, pinned_configuration)
    elif job_type == "research.exhaustive":
        _validate_research_exhaustive(requested_scope, pinned_configuration)
    elif job_type == "backup.create":
        _validate_backup_create(requested_scope, pinned_configuration)
    elif job_type == "archive.replicate":
        _validate_archive_replicate(requested_scope, pinned_configuration)
    elif job_type in _NON_EXECUTABLE_BUILTIN_JOB_TYPES:
        raise BuiltinJobPayloadValidationError(
            f"{job_type} has no executable durable worker and cannot be persisted."
        )


def _validate_source_process(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "source.process"
    _require_exact_or_optional_keys(
        scope,
        required={"source_id"},
        optional={"research_work_item_id"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "source_id", label=label)
    if "research_work_item_id" in scope:
        _uuid_text(scope, "research_work_item_id", label=label)

    expected = {
        "pipeline_version",
        "text_parser",
        "pdf_parser",
        "docx_parser",
        "html_parser",
        "chunking_profile",
        "chunk_batch_size",
        "embedding_policy",
    }
    _require_exact_keys(config, expected, label=f"{label} pinned_configuration")
    assert config is not None
    _equal_text(config, "pipeline_version", "source-process-v2", label=label)
    _equal_text(config, "text_parser", "athena.native_text@1", label=label)
    _text(config, "pdf_parser", label=label)
    _text(config, "docx_parser", label=label)
    _text(config, "html_parser", label=label)
    _equal_text(config, "chunking_profile", "default", label=label)
    batch = _integer(config, "chunk_batch_size", minimum=1, label=label)
    if batch != 32:
        raise BuiltinJobPayloadValidationError(
            "source.process chunk_batch_size must match durable pipeline value 32."
        )
    _equal_text(config, "embedding_policy", "deferred", label=label)


def _validate_source_analyze(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "source.analyze"
    _require_exact_or_optional_keys(
        scope,
        required={"source_id", "representation_id", "question"},
        optional={"research_work_item_id"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "source_id", label=label)
    _uuid_text(scope, "representation_id", label=label)
    if "research_work_item_id" in scope:
        _uuid_text(scope, "research_work_item_id", label=label)
    _text(scope, "question", label=label)

    expected = {
        "pipeline_version",
        "model_id",
        "model_signature_id",
        "model_signature_sha256",
        "effective_context_limit",
        "output_reserve",
        "safety_margin",
        "token_estimator",
        "max_hierarchy_depth",
        "prompt_template_id",
        "prompt_template_version",
    }
    _require_exact_keys(config, expected, label=f"{label} pinned_configuration")
    assert config is not None
    _equal_text(config, "pipeline_version", "source-analysis-v1", label=label)
    _text(config, "model_id", label=label)
    _uuid_text(config, "model_signature_id", label=label)
    _sha256_text(config, "model_signature_sha256", label=label)
    effective = _integer(config, "effective_context_limit", minimum=64, label=label)
    reserve = _integer(config, "output_reserve", minimum=1, label=label)
    margin = _integer(config, "safety_margin", minimum=0, label=label)
    _integer(config, "max_hierarchy_depth", minimum=1, label=label)
    if reserve + margin >= effective:
        raise BuiltinJobPayloadValidationError(
            "source.analyze context budget leaves no positive input budget."
        )
    _equal_text(config, "token_estimator", "utf8-bytes-div3-v1", label=label)
    _equal_text(config, "prompt_template_id", "athena.source_analysis", label=label)
    _equal_text(config, "prompt_template_version", "1", label=label)


def _validate_source_extract(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "source.extract"
    _require_exact_keys(
        scope,
        {"analysis_id", "final_artifact_id"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "analysis_id", label=label)
    _uuid_text(scope, "final_artifact_id", label=label)

    expected = {
        "pipeline_version",
        "model_id",
        "model_signature_id",
        "model_signature_sha256",
        "model",
        "effective_context_limit",
        "provider_context_length",
        "output_reserve",
        "safety_margin",
        "token_estimator",
        "max_hierarchy_depth",
        "prompt_template_id",
        "prompt_template_version",
        "source_extraction_schema_id",
        "merge_schema_id",
        "pair_audit_schema_id",
        "provider_transport",
        "reasoning_mode",
        "temperature",
        "top_p",
        "top_k",
        "min_p",
        "repeat_penalty",
        "store",
        "structured_contract_version",
        "structured_validation",
        "provider_instance_policy",
    }
    _require_exact_keys(config, expected, label=f"{label} pinned_configuration")
    assert config is not None
    _equal_text(
        config,
        "pipeline_version",
        "source-analysis-knowledge-extraction/3",
        label=label,
    )
    _text(config, "model_id", label=label)
    _uuid_text(config, "model_signature_id", label=label)
    _sha256_text(config, "model_signature_sha256", label=label)
    model = config.get("model")
    if not isinstance(model, Mapping) or not model:
        raise BuiltinJobPayloadValidationError(
            "source.extract field 'model' must be a non-empty object snapshot."
        )

    effective = _integer(config, "effective_context_limit", minimum=64, label=label)
    provider_context = _integer(config, "provider_context_length", minimum=64, label=label)
    if provider_context != effective:
        raise BuiltinJobPayloadValidationError(
            "source.extract provider context must equal the pinned effective context."
        )
    reserve = _integer(config, "output_reserve", minimum=1, label=label)
    margin = _integer(config, "safety_margin", minimum=0, label=label)
    _integer(config, "max_hierarchy_depth", minimum=1, label=label)
    if reserve + margin >= effective:
        raise BuiltinJobPayloadValidationError(
            "source.extract context budget leaves no positive input budget."
        )
    _equal_text(config, "token_estimator", "utf8-bytes-div3-v1", label=label)
    _equal_text(
        config,
        "prompt_template_id",
        "athena.source_analysis_knowledge_extraction_hierarchical",
        label=label,
    )
    _equal_text(config, "prompt_template_version", "6", label=label)
    _equal_text(
        config,
        "source_extraction_schema_id",
        "athena_source_analysis_knowledge_extraction_v1",
        label=label,
    )
    _equal_text(
        config,
        "merge_schema_id",
        "athena_source_extraction_semantic_dedup_v3",
        label=label,
    )
    _equal_text(
        config,
        "pair_audit_schema_id",
        "athena_source_extraction_pair_batch_audit_v1",
        label=label,
    )
    _text(config, "provider_transport", label=label)
    _equal_text(config, "reasoning_mode", "off", label=label)
    if _number(config, "temperature", label=label) != 0.0:
        raise BuiltinJobPayloadValidationError("source.extract temperature must be 0.0.")
    if _number(config, "top_p", label=label) != 0.95:
        raise BuiltinJobPayloadValidationError("source.extract top_p must be 0.95.")
    if _integer(config, "top_k", minimum=0, label=label) != 40:
        raise BuiltinJobPayloadValidationError("source.extract top_k must be 40.")
    if _number(config, "min_p", label=label) != 0.05:
        raise BuiltinJobPayloadValidationError("source.extract min_p must be 0.05.")
    if _number(config, "repeat_penalty", label=label) != 1.1:
        raise BuiltinJobPayloadValidationError("source.extract repeat_penalty must be 1.1.")
    _exact_bool(config, "store", False, label=label)
    _equal_text(
        config,
        "structured_contract_version",
        "athena.controlled_structured_json/1",
        label=label,
    )
    _equal_text(
        config,
        "structured_validation",
        "athena_stage_parser_v1",
        label=label,
    )
    _equal_text(
        config,
        "provider_instance_policy",
        "initial_context_then_runtime_instance_reuse_v1",
        label=label,
    )


def _validate_embedding_rebuild(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "embedding.rebuild"
    _require_exact_keys(scope, {"index_kind"}, label=f"{label} requested_scope")
    assert scope is not None
    _equal_text(scope, "index_kind", "archive_source_chunks", label=label)

    _require_exact_keys(
        config,
        {
            "batch_size",
            "index_kind",
            "model_id",
            "pipeline_version",
            "target_chunk_generation",
        },
        label=f"{label} pinned_configuration",
    )
    assert config is not None
    batch_size = _integer(config, "batch_size", minimum=1, label=label)
    if batch_size > 256:
        raise BuiltinJobPayloadValidationError(
            "embedding.rebuild batch_size must be between 1 and 256."
        )
    _equal_text(config, "index_kind", "archive_source_chunks", label=label)
    _text(config, "model_id", label=label)
    _equal_text(
        config,
        "pipeline_version",
        "archive-embedding-rebuild-v1",
        label=label,
    )
    _integer(config, "target_chunk_generation", minimum=0, label=label)


def _validate_research_exhaustive(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "research.exhaustive"
    _require_exact_keys(
        scope,
        {
            "mode",
            "query",
            "domains",
            "project_ids",
            "source_types",
            "explicit_source_ids",
            "time_start_us",
            "time_end_us",
            "internet_scope",
            "coverage_target",
        },
        label=f"{label} requested_scope",
    )
    assert scope is not None
    mode = _text(scope, "mode", label=label)
    if mode not in {"local_exhaustive", "scoped_project"}:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive field 'mode' has an unsupported value."
        )
    _text(scope, "query", label=label)
    _canonical_sorted_text_list(scope, "domains", label=label)
    _canonical_uuid_list(scope, "project_ids", label=label)
    if mode == "scoped_project" and not scope.get("project_ids"):
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive scoped_project mode requires project_ids."
        )
    source_types = _canonical_sorted_text_list(scope, "source_types", label=label)
    if any(item not in _RESEARCH_SOURCE_TYPES for item in source_types):
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive source_types contains an unsupported source type."
        )
    _canonical_uuid_list(scope, "explicit_source_ids", label=label)
    start = _optional_integer(scope, "time_start_us", minimum=0, label=label)
    end = _optional_integer(scope, "time_end_us", minimum=0, label=label)
    if start is not None and end is not None and end < start:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive time_end_us must be >= time_start_us."
        )
    if scope.get("internet_scope") is not None:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive local mode requires internet_scope to be null."
        )
    coverage = scope.get("coverage_target")
    if isinstance(coverage, bool) or not isinstance(coverage, float):
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive field 'coverage_target' must be a canonical float."
        )
    if not math.isfinite(coverage) or not 0.0 < coverage <= 1.0:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive coverage_target must be finite and in (0, 1]."
        )

    _require_exact_keys(
        config,
        {
            "pipeline_version",
            "snapshot_commit_seq",
            "coverage_formula_id",
            "candidate_dedup_id",
            "requested_model_id",
            "context_limit",
            "output_reserve",
            "safety_margin",
            "max_hierarchy_depth",
        },
        label=f"{label} pinned_configuration",
    )
    assert config is not None
    _equal_text(
        config,
        "pipeline_version",
        "exhaustive-research-orchestration-v2",
        label=label,
    )
    _integer(config, "snapshot_commit_seq", minimum=0, label=label)
    _equal_text(
        config,
        "coverage_formula_id",
        "eligible-success-or-irrelevant-v1",
        label=label,
    )
    _equal_text(
        config,
        "candidate_dedup_id",
        "source-content-sha256-v1",
        label=label,
    )
    _optional_text(config, "requested_model_id", label=label)
    _optional_integer(config, "context_limit", minimum=1, label=label)
    _optional_integer(config, "output_reserve", minimum=1, label=label)
    _optional_integer(config, "safety_margin", minimum=0, label=label)
    _integer(config, "max_hierarchy_depth", minimum=1, label=label)


def _validate_backup_create(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "backup.create"
    _require_exact_keys(
        scope,
        {"schedule_slot_us", "target_id"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "target_id", label=label)
    _integer(scope, "schedule_slot_us", minimum=0, label=label)

    _require_exact_keys(
        config,
        {"pipeline_version", "quiet_hour_utc"},
        label=f"{label} pinned_configuration",
    )
    assert config is not None
    _equal_text(config, "pipeline_version", "backup-scheduler-v1", label=label)
    quiet_hour = _integer(config, "quiet_hour_utc", minimum=0, label=label)
    if quiet_hour > 23:
        raise BuiltinJobPayloadValidationError(
            "backup.create quiet_hour_utc must be between 0 and 23."
        )


def _validate_archive_replicate(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = "archive.replicate"
    _require_exact_keys(scope, {"target_role"}, label=f"{label} requested_scope")
    assert scope is not None
    _equal_text(scope, "target_role", "archive_root", label=label)

    _require_exact_keys(
        config,
        {"pipeline_version", "storage_retry_seconds"},
        label=f"{label} pinned_configuration",
    )
    assert config is not None
    _equal_text(config, "pipeline_version", "archive-replication-v1", label=label)
    _integer(config, "storage_retry_seconds", minimum=1, label=label)


def _require_exact_keys(
    value: Mapping[str, Any] | None,
    expected: set[str],
    *,
    label: str,
) -> None:
    if value is None or set(value) != expected:
        raise BuiltinJobPayloadValidationError(
            f"{label} has unexpected or missing fields."
        )


def _require_exact_or_optional_keys(
    value: Mapping[str, Any] | None,
    *,
    required: set[str],
    optional: set[str],
    label: str,
) -> None:
    if value is None:
        raise BuiltinJobPayloadValidationError(f"{label} is required.")
    keys = set(value)
    if not required <= keys or keys - required - optional:
        raise BuiltinJobPayloadValidationError(
            f"{label} has unexpected or missing fields."
        )


def _text(value: Mapping[str, Any], field: str, *, label: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be non-empty text."
        )
    if item != item.strip():
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must already be canonical text."
        )
    return item


def _optional_text(
    value: Mapping[str, Any],
    field: str,
    *,
    label: str,
) -> str | None:
    item = value.get(field)
    if item is None:
        return None
    return _text(value, field, label=label)


def _canonical_sorted_text_list(
    value: Mapping[str, Any],
    field: str,
    *,
    label: str,
) -> list[str]:
    raw = value.get(field)
    if not isinstance(raw, list):
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be a list."
        )
    result: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item or item != item.strip():
            raise BuiltinJobPayloadValidationError(
                f"{label} field {field!r} must contain canonical non-empty text."
            )
        result.append(item)
    if result != sorted(set(result)):
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be sorted and unique."
        )
    return result


def _canonical_uuid_list(
    value: Mapping[str, Any],
    field: str,
    *,
    label: str,
) -> None:
    raw = value.get(field)
    if not isinstance(raw, list):
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be a list."
        )
    parsed: list[uuid.UUID] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            raise BuiltinJobPayloadValidationError(
                f"{label} field {field!r} must contain UUID strings."
            )
        try:
            parsed_item = uuid.UUID(item)
        except ValueError as exc:
            raise BuiltinJobPayloadValidationError(
                f"{label} field {field!r} must contain UUID strings."
            ) from exc
        if str(parsed_item) != item:
            raise BuiltinJobPayloadValidationError(
                f"{label} field {field!r} must contain canonical UUID text."
            )
        parsed.append(parsed_item)
    canonical = [str(item) for item in sorted(set(parsed), key=lambda item: item.bytes)]
    if raw != canonical:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be sorted and unique."
        )


def _equal_text(
    value: Mapping[str, Any],
    field: str,
    expected: str,
    *,
    label: str,
) -> None:
    if _text(value, field, label=label) != expected:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} has an unsupported value."
        )


def _uuid_text(value: Mapping[str, Any], field: str, *, label: str) -> uuid.UUID:
    raw = _text(value, field, label=label)
    try:
        parsed = uuid.UUID(raw)
    except ValueError as exc:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be a UUID string."
        ) from exc
    if str(parsed) != raw.lower():
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must use canonical UUID text."
        )
    return parsed


def _sha256_text(value: Mapping[str, Any], field: str, *, label: str) -> bytes:
    raw = _text(value, field, label=label)
    if raw.lower() != raw:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must use lowercase hexadecimal."
        )
    try:
        digest = bytes.fromhex(raw)
    except ValueError as exc:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be hexadecimal."
        ) from exc
    if len(digest) != 32:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must encode SHA-256."
        )
    return digest


def _integer(
    value: Mapping[str, Any],
    field: str,
    *,
    minimum: int,
    label: str,
) -> int:
    item = value.get(field)
    if isinstance(item, bool) or not isinstance(item, int) or item < minimum:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be an integer >= {minimum}."
        )
    return item


def _optional_integer(
    value: Mapping[str, Any],
    field: str,
    *,
    minimum: int,
    label: str,
) -> int | None:
    item = value.get(field)
    if item is None:
        return None
    return _integer(value, field, minimum=minimum, label=label)


def _number(value: Mapping[str, Any], field: str, *, label: str) -> float:
    item = value.get(field)
    if isinstance(item, bool) or not isinstance(item, (int, float)):
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be a finite number."
        )
    result = float(item)
    if not math.isfinite(result):
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be a finite number."
        )
    return result


def _exact_bool(
    value: Mapping[str, Any],
    field: str,
    expected: bool,
    *,
    label: str,
) -> None:
    item = value.get(field)
    if not isinstance(item, bool) or item is not expected:
        raise BuiltinJobPayloadValidationError(
            f"{label} field {field!r} must be {expected!r}."
        )
