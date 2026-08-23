"""Fail-closed payload validation for durable News jobs."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from datetime import date, timedelta
from typing import Any

from athena.news.common import _default_profile_id
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
    _default_profile(scope, label=label)
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
    _default_profile(scope, label=label)
    kind = _text(scope, "period_kind", label=label)
    if kind not in {"weekly", "monthly"}:
        raise NewsJobPayloadValidationError(
            "news.period period_kind must be 'weekly' or 'monthly'."
        )
    start = _date_text(scope, "period_start", label=label)
    end = _date_text(scope, "period_end", label=label)
    if kind == "weekly":
        if start.weekday() != 0 or end != start + timedelta(days=6):
            raise NewsJobPayloadValidationError(
                "news.period weekly windows must be a closed Monday-Sunday week."
            )
    else:
        if start.day != 1 or end != _month_end(start):
            raise NewsJobPayloadValidationError(
                "news.period monthly windows must cover one closed calendar month."
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
    if not isinstance(value, Mapping):
        raise NewsJobPayloadValidationError(f"{label} must be an object.")
    if set(value) != expected or not all(isinstance(key, str) for key in value):
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


def _default_profile(value: Mapping[str, Any], *, label: str) -> uuid.UUID:
    parsed = _uuid_text(value, "profile_id", label=label)
    if parsed != _default_profile_id():
        raise NewsJobPayloadValidationError(
            f"{label} profile_id must reference the default durable News profile."
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


def _month_end(start: date) -> date:
    if start.month == 12:
        return date(start.year, 12, 31)
    next_month = date(start.year, start.month + 1, 1)
    return next_month - timedelta(days=1)
