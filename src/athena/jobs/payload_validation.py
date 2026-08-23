"""Fail-closed validation for durable built-in job payloads.

This module is deliberately dependency-light so the application-facing job service can
reject malformed persistent work before actor creation or repository writes. Workers
still re-validate their own runtime contracts; this boundary prevents invalid new jobs
from entering durable state in the first place.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from typing import Any


class BuiltinJobPayloadValidationError(ValueError):
    """Raised when a built-in durable job payload is not persistence-safe."""


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
    elif job_type == "backup.create":
        _validate_backup_create(requested_scope, pinned_configuration)
    elif job_type == "archive.replicate":
        _validate_archive_replicate(requested_scope, pinned_configuration)


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
