from __future__ import annotations

import json
import uuid

import pytest

from athena.jobs.schedule_codec import (
    decode_schedule_definition,
    encode_schedule_definition,
)
from athena.jobs.schedule_definition import ScheduleDefinition
from athena.jobs.schedule_policy import MissedRunPolicy


def _schedule() -> ScheduleDefinition:
    return ScheduleDefinition(
        schedule_id=uuid.UUID("00000000-0000-7000-8000-000000000001"),
        job_type="research",
        schedule_expression="0 * * * *",
        timezone_name="Europe/Berlin",
        created_by_actor_id=uuid.UUID("00000000-0000-7000-8000-000000000002"),
        created_at_us=10,
        updated_at_us=20,
        missed_run_policy=MissedRunPolicy.BACKFILL_BOUNDED,
        max_backfill=3,
        enabled=True,
    )


def test_schedule_codec_round_trips_all_durable_fields() -> None:
    schedule = _schedule()

    encoded = encode_schedule_definition(schedule)

    assert decode_schedule_definition(encoded) == schedule


def test_schedule_encoding_is_deterministic_and_versioned() -> None:
    encoded = encode_schedule_definition(_schedule())

    assert encoded == encode_schedule_definition(_schedule())
    payload = json.loads(encoded)
    assert payload["schema_version"] == 1
    assert encoded.startswith('{"created_at_us":10,')


@pytest.mark.parametrize("field", ["job_type", "enabled", "schedule_id"])
def test_decoder_rejects_missing_fields(field: str) -> None:
    payload = json.loads(encode_schedule_definition(_schedule()))
    del payload[field]

    with pytest.raises(ValueError, match="fields do not match schema"):
        decode_schedule_definition(json.dumps(payload))


def test_decoder_rejects_unknown_fields() -> None:
    payload = json.loads(encode_schedule_definition(_schedule()))
    payload["unexpected"] = True

    with pytest.raises(ValueError, match="unknown=.*unexpected"):
        decode_schedule_definition(json.dumps(payload))


def test_decoder_rejects_duplicate_json_fields() -> None:
    encoded = encode_schedule_definition(_schedule())
    duplicate = encoded[:-1] + ',"enabled":false}'

    with pytest.raises(ValueError, match="duplicate field: enabled"):
        decode_schedule_definition(duplicate)


def test_decoder_rejects_noncanonical_uuid_text() -> None:
    payload = json.loads(encode_schedule_definition(_schedule()))
    canonical = "abcdefab-cdef-7abc-8def-abcdefabcdef"
    payload["schedule_id"] = canonical.upper()

    with pytest.raises(ValueError, match="canonical lowercase UUID"):
        decode_schedule_definition(json.dumps(payload))


@pytest.mark.parametrize("version", [True, 0, 2, "1"])
def test_decoder_rejects_invalid_schema_versions(version: object) -> None:
    payload = json.loads(encode_schedule_definition(_schedule()))
    payload["schema_version"] = version

    with pytest.raises((TypeError, ValueError)):
        decode_schedule_definition(json.dumps(payload))


def test_decoder_reuses_schedule_definition_invariants() -> None:
    payload = json.loads(encode_schedule_definition(_schedule()))
    payload["max_backfill"] = 0

    with pytest.raises(ValueError, match="max_backfill must be >= 1"):
        decode_schedule_definition(json.dumps(payload))


def test_encoder_rejects_wrong_runtime_type() -> None:
    with pytest.raises(TypeError, match="ScheduleDefinition"):
        encode_schedule_definition(object())  # type: ignore[arg-type]
