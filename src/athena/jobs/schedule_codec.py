"""Canonical durable serialization for scheduled job definitions."""

from __future__ import annotations

import json
import uuid
from typing import Any

from athena.jobs.schedule_definition import ScheduleDefinition
from athena.jobs.schedule_policy import MissedRunPolicy

_SCHEMA_VERSION = 1
_FIELDS = frozenset(
    {
        "schema_version",
        "schedule_id",
        "job_type",
        "schedule_expression",
        "timezone_name",
        "created_by_actor_id",
        "created_at_us",
        "updated_at_us",
        "missed_run_policy",
        "max_backfill",
        "enabled",
    }
)


def encode_schedule_definition(schedule: ScheduleDefinition) -> str:
    """Encode one schedule using a deterministic versioned JSON representation."""
    if not isinstance(schedule, ScheduleDefinition):
        raise TypeError("schedule must be a ScheduleDefinition.")

    payload = {
        "schema_version": _SCHEMA_VERSION,
        "schedule_id": str(schedule.schedule_id),
        "job_type": schedule.job_type,
        "schedule_expression": schedule.schedule_expression,
        "timezone_name": schedule.timezone_name,
        "created_by_actor_id": str(schedule.created_by_actor_id),
        "created_at_us": schedule.created_at_us,
        "updated_at_us": schedule.updated_at_us,
        "missed_run_policy": schedule.missed_run_policy.value,
        "max_backfill": schedule.max_backfill,
        "enabled": schedule.enabled,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def decode_schedule_definition(encoded: str) -> ScheduleDefinition:
    """Decode canonical schedule JSON and reject ambiguous or unknown state."""
    if not isinstance(encoded, str):
        raise TypeError("encoded schedule must be text.")

    try:
        payload = json.loads(encoded, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise ValueError("encoded schedule is not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise ValueError("encoded schedule must be a JSON object.")
    keys = set(payload)
    if keys != _FIELDS:
        missing = sorted(_FIELDS - keys)
        unknown = sorted(keys - _FIELDS)
        raise ValueError(
            f"encoded schedule fields do not match schema; missing={missing}, unknown={unknown}."
        )

    schema_version = payload["schema_version"]
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise TypeError("schedule schema_version must be an integer.")
    if schema_version != _SCHEMA_VERSION:
        raise ValueError(f"unsupported schedule schema_version: {schema_version}.")

    schedule_id = _canonical_uuid(payload["schedule_id"], "schedule_id")
    actor_id = _canonical_uuid(payload["created_by_actor_id"], "created_by_actor_id")

    policy_value = payload["missed_run_policy"]
    if not isinstance(policy_value, str):
        raise TypeError("missed_run_policy must be text.")
    try:
        policy = MissedRunPolicy(policy_value)
    except ValueError as exc:
        raise ValueError(f"unsupported missed_run_policy: {policy_value!r}.") from exc

    return ScheduleDefinition(
        schedule_id=schedule_id,
        job_type=payload["job_type"],
        schedule_expression=payload["schedule_expression"],
        timezone_name=payload["timezone_name"],
        created_by_actor_id=actor_id,
        created_at_us=payload["created_at_us"],
        updated_at_us=payload["updated_at_us"],
        missed_run_policy=policy,
        max_backfill=payload["max_backfill"],
        enabled=payload["enabled"],
    )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"encoded schedule contains duplicate field: {key}.")
        payload[key] = value
    return payload


def _canonical_uuid(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be canonical UUID text.")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"{label} is not a valid UUID.") from exc
    if str(parsed) != value:
        raise ValueError(f"{label} must use canonical lowercase UUID text.")
    return parsed
