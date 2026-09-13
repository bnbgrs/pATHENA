from __future__ import annotations

import uuid

import pytest

from athena.jobs.schedule_definition import ScheduleDefinition
from athena.jobs.schedule_policy import MissedRunPolicy


def _definition(*, timezone_name: str) -> ScheduleDefinition:
    return ScheduleDefinition(
        schedule_id=uuid.UUID("11111111-1111-4111-8111-111111111111"),
        job_type="research.refresh",
        schedule_expression="0 * * * *",
        timezone_name=timezone_name,
        created_by_actor_id=uuid.UUID("22222222-2222-4222-8222-222222222222"),
        created_at_us=100,
        updated_at_us=100,
        missed_run_policy=MissedRunPolicy.RUN_ONCE,
        max_backfill=None,
    )


def test_schedule_definition_accepts_available_iana_timezone() -> None:
    definition = _definition(timezone_name="Europe/Berlin")
    assert definition.timezone_name == "Europe/Berlin"


def test_schedule_definition_rejects_unknown_iana_timezone() -> None:
    with pytest.raises(ValueError, match="available IANA timezone"):
        _definition(timezone_name="Mars/Olympus_Mons")
