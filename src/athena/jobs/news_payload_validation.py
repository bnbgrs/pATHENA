"""Fail-closed payload validation for durable News jobs."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from datetime import date
from typing import Any

from athena.news.models import NEWS_JOB_TYPE, NEWS_PERIOD_JOB_TYPE, NEWS_PIPELINE_VERSION
from athena.news.schema import NEWS_SCHEMA_ID


class NewsJobPayloadValidationError(ValueError):
    """Raised when a durable News job contract is not persistence-safe."""


def validate_news_job_payload(
    job_type: str,
    *,
    requested_scope: Mapping[str, Any] | None,
    pinned_configuration: Mapping[str, Any] | None,
) -> None:
    """Validate one current News job producer/worker contract exactly."""
    if job_type == NEWS_JOB_TYPE:
        _validate_daily(requested_scope, pinned_configuration)
        return
    if job_type == NEWS_PERIOD_JOB_TYPE:
        _validate_period(requested_scope, pinned_configuration)
        return
    raise NewsJobPayloadValidationError(f"Unsupported News job type {job_type!r}.")


def _validate_daily(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = NEWS_JOB_TYPE
    _require_exact_keys(
        scope,
        {"profile_id", "target_date"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "profile_id", label=label)
    _date_text(scope, "target_date", label=label)
    _validate_config(config, label=label)


def _validate_period(
    scope: Mapping[str, Any] | None,
    config: Mapping[str, Any] | None,
) -> None:
    label = NEWS_PERIOD_JOB_TYPE
    _require_exact_keys(
        scope,
        {"profile_id", "period_kind", "period_start", "period_end"},
        label=f"{label} requested_scope",
    )
    assert scope is not None
    _uuid_text(scope, "profile_id", label=label)
    kind = _text(scope, "period_kind", label=label)
    if kind not in {"weekly", "monthly"}:
        raise NewsJobPayloadValidationError(
            "news.period period_kind must be 'weekly' or 'monthly'."
        )
    start = _date_text(scope, "period_start", label=label)
    end = _date_text(scope, "period_end", label=label)
    if end < start:
        raise NewsJobPayloadValidationError(
            "news.period period_end must be >= period_start."
        )
    _validate_config(config, label=label)


def _validate_config(
    config: Mapping[str, Any] | None,
    *,
    label: str,
) -> None:
    _require_exact_keys(
        config,
        {"pipeline_version", "news_schema"},
        label=f"{label} pinned_configuration",
    )
    assert config is not None
    if _text(config, "pipeline_version", label=label) != NEWS_PIPELINE_VERSION:
        raise NewsJobPayloadValidationError(
            f"{label} pipeline_version is unsupported."
        )
    if _text(config, "news_schema", label=label) != NEWS_SCHEMA_ID:
        raise NewsJobPayloadValidationError(f"{label} news_schema is unsupported.")


def _require_exact_keys(
    value: Mapping[str, Any] | None,
    expected: set[str],
    *,
    label: str,
) -> None:
    if value is None or set(value) != expected:
        raise NewsJobPayloadValidationError(
            f"{label} has unexpected or missing fields."
        )


def _text(value: Mapping[str, Any], field: str, *, label: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item or item != item.strip():
        raise NewsJobPayloadValidationError(
            f"{label} field {field!r} must be canonical non-empty text."
        )
    return item


def _uuid_text(value: Mapping[str, Any], field: str, *, label: str) -> uuid.UUID:
    raw = _text(value, field, label=label)
    try:
        parsed = uuid.UUID(raw)
    except ValueError as exc:
        raise NewsJobPayloadValidationError(
            f"{label} field {field!r} must be a UUID string."
        ) from exc
    if str(parsed) != raw:
        raise NewsJobPayloadValidationError(
            f"{label} field {field!r} must use canonical UUID text."
        )
    return parsed


def _date_text(value: Mapping[str, Any], field: str, *, label: str) -> date:
    raw = _text(value, field, label=label)
    try:
        parsed = date.fromisoformat(raw)
    except ValueError as exc:
        raise NewsJobPayloadValidationError(
            f"{label} field {field!r} must be an ISO calendar date."
        ) from exc
    if parsed.isoformat() != raw:
        raise NewsJobPayloadValidationError(
            f"{label} field {field!r} must use canonical ISO date text."
        )
    return parsed
