from __future__ import annotations

import pytest

from athena.jobs.models import _require_optional_json


@pytest.mark.parametrize(
    "value",
    [
        "NaN",
        "Infinity",
        "-Infinity",
        '{"value":NaN}',
        '{"value":Infinity}',
        '{"value":-Infinity}',
    ],
)
def test_durable_job_json_rejects_non_standard_constants(value: str) -> None:
    with pytest.raises(ValueError, match="strict JSON"):
        _require_optional_json(value, "payload")


def test_durable_job_json_rejects_duplicate_object_keys() -> None:
    with pytest.raises(ValueError, match="strict JSON"):
        _require_optional_json('{"a":1,"a":2}', "payload")


@pytest.mark.parametrize(
    "value",
    [
        None,
        "null",
        "true",
        "false",
        "0",
        '"text"',
        "[]",
        "{}",
        '{"nested":[1,2,3]}',
    ],
)
def test_durable_job_json_accepts_standard_json(value: str | None) -> None:
    _require_optional_json(value, "payload")
