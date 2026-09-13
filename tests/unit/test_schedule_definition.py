from __future__ import annotations

import uuid
from typing import Any

import pytest

from athena.jobs.schedule_definition import ScheduleDefinition, occurrence_id
from athena.jobs.schedule_policy import MissedRunPolicy


def _definition(**overrides: Any) -> ScheduleDefinition:
    values: dict[str, Any] = {
        "schedule_id": uuid.UUID("11111111-1111-4111-8111-111111111111"),
        "job_type": "research.refresh",
        "schedule_expression": "0 * * * *",
        "timezone_name": "Europe/Berlin",
        "created_by_actor_id": uuid.UUID("22222222-2222-4222-8222-222222222222"),
        "created_at_us": 100,
        "updated_at_us": 100,
        "missed_run_policy": MissedRunPolicy.RUN_ONCE,
        "max_backfill": None,
        "enabled": True,
    }
    values.update(overrides)
    return ScheduleDefinition(**values)


def test_definition_preserves_canonical_durable_fields() -> None:
    definition = _definition()
    assert definition.uri == (
        "operational://schedule/11111111-1111-4111-8111-111111111111"
    )
    assert definition.enabled is True


def test_bounded_policy_requires_positive_integer_limit() -> None:
    bounded = _definition(
        missed_run_policy=MissedRunPolicy.BACKFILL_BOUNDED,
        max_backfill=3,
    )
    assert bounded.max_backfill == 3

    with pytest.raises(TypeError, match="integer max_backfill"):
        _definition(
            missed_run_policy=MissedRunPolicy.BACKFILL_BOUNDED,
            max_backfill=True,
        )
    with pytest.raises(ValueError, match=">= 1"):
        _definition(
            missed_run_policy=MissedRunPolicy.BACKFILL_BOUNDED,
            max_backfill=0,
        )


def test_nonbounded_policy_rejects_backfill_limit() -> None:
    with pytest.raises(ValueError, match="only valid"):
        _definition(max_backfill=1)


def test_definition_rejects_noncanonical_text_and_time_regression() -> None:
    with pytest.raises(ValueError, match="canonical trimmed text"):
        _definition(job_type=" research.refresh")
    with pytest.raises(ValueError, match="precedes"):
        _definition(updated_at_us=99)


def test_definition_requires_real_policy_and_boolean_enabled_flag() -> None:
    with pytest.raises(TypeError, match="MissedRunPolicy"):
        _definition(missed_run_policy="run_once")
    with pytest.raises(TypeError, match="enabled must be bool"):
        _definition(enabled=1)


def test_occurrence_id_is_stable_for_recovery_and_retry() -> None:
    schedule_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
    first = occurrence_id(schedule_id, 1_700_000_000_000_000)
    recovered = occurrence_id(schedule_id, 1_700_000_000_000_000)
    assert first == recovered


def test_occurrence_id_distinguishes_schedule_and_scheduled_instant() -> None:
    schedule_a = uuid.UUID("11111111-1111-4111-8111-111111111111")
    schedule_b = uuid.UUID("33333333-3333-4333-8333-333333333333")
    at_us = 1_700_000_000_000_000

    assert occurrence_id(schedule_a, at_us) != occurrence_id(schedule_a, at_us + 1)
    assert occurrence_id(schedule_a, at_us) != occurrence_id(schedule_b, at_us)


@pytest.mark.parametrize("bad_time", [True, -1])
def test_occurrence_id_rejects_invalid_timestamp(bad_time: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        occurrence_id(
            uuid.UUID("11111111-1111-4111-8111-111111111111"),
            bad_time,
        )
