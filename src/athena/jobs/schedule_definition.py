"""Durable schedule-definition and occurrence identity primitives."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.jobs.schedule_policy import MissedRunPolicy

_OCCURRENCE_ID_PREFIX = "athena-schedule-occurrence-v1:"


def _require_uuid(value: object, label: str) -> None:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")


def _require_text(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value:
        raise ValueError(f"{label} must not be empty.")
    if value != value.strip():
        raise ValueError(f"{label} must use canonical trimmed text.")


def _require_timestamp_us(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer microsecond timestamp.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")


@dataclass(frozen=True, slots=True)
class ScheduleDefinition:
    """Canonical durable metadata for a recurring job schedule."""

    schedule_id: uuid.UUID
    job_type: str
    schedule_expression: str
    timezone_name: str
    created_by_actor_id: uuid.UUID
    created_at_us: int
    updated_at_us: int
    missed_run_policy: MissedRunPolicy
    max_backfill: int | None
    enabled: bool = True

    def __post_init__(self) -> None:
        _require_uuid(self.schedule_id, "ScheduleDefinition schedule_id")
        _require_uuid(
            self.created_by_actor_id,
            "ScheduleDefinition created_by_actor_id",
        )
        _require_text(self.job_type, "ScheduleDefinition job_type")
        _require_text(
            self.schedule_expression,
            "ScheduleDefinition schedule_expression",
        )
        _require_text(self.timezone_name, "ScheduleDefinition timezone_name")
        _require_timestamp_us(
            self.created_at_us,
            "ScheduleDefinition created_at_us",
        )
        _require_timestamp_us(
            self.updated_at_us,
            "ScheduleDefinition updated_at_us",
        )
        if self.updated_at_us < self.created_at_us:
            raise ValueError("ScheduleDefinition updated_at_us precedes created_at_us.")
        if not isinstance(self.missed_run_policy, MissedRunPolicy):
            raise TypeError(
                "ScheduleDefinition missed_run_policy must be a MissedRunPolicy."
            )
        if not isinstance(self.enabled, bool):
            raise TypeError("ScheduleDefinition enabled must be bool.")

        if self.missed_run_policy is MissedRunPolicy.BACKFILL_BOUNDED:
            if isinstance(self.max_backfill, bool) or not isinstance(
                self.max_backfill,
                int,
            ):
                raise TypeError(
                    "ScheduleDefinition backfill_bounded requires integer max_backfill."
                )
            if self.max_backfill < 1:
                raise ValueError("ScheduleDefinition max_backfill must be >= 1.")
        elif self.max_backfill is not None:
            raise ValueError(
                "ScheduleDefinition max_backfill is only valid for backfill_bounded."
            )

    @property
    def uri(self) -> str:
        return f"operational://schedule/{self.schedule_id}"


def occurrence_id(schedule_id: uuid.UUID, scheduled_at_us: int) -> uuid.UUID:
    """Return the stable identity for one logical schedule occurrence.

    Re-evaluating or recovering the same occurrence returns exactly the same UUID,
    giving persistence layers a deterministic uniqueness key without conflating
    distinct scheduled instants.
    """

    _require_uuid(schedule_id, "schedule_id")
    _require_timestamp_us(scheduled_at_us, "scheduled_at_us")
    return uuid.uuid5(
        schedule_id,
        f"{_OCCURRENCE_ID_PREFIX}{scheduled_at_us}",
    )
