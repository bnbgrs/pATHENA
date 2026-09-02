from __future__ import annotations

import json

import pytest

from athena.security.models import Argon2idParameters


@pytest.mark.parametrize(
    "field,value",
    [
        ("format_version", True),
        ("format_version", 1.0),
        ("iterations", True),
        ("iterations", 3.0),
        ("lanes", False),
        ("lanes", 4.0),
        ("memory_cost_kib", True),
        ("memory_cost_kib", 65536.0),
        ("length", True),
        ("length", 32.0),
    ],
)
def test_direct_argon2_parameters_reject_non_exact_integers(
    field: str,
    value: object,
) -> None:
    kwargs: dict[str, object] = {field: value}

    with pytest.raises(ValueError):
        Argon2idParameters(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "payload",
    [
        {"format_version": 1, "iterations": 3, "lanes": 4, "length": 32},
        {
            "format_version": 1,
            "iterations": 3,
            "lanes": 4,
            "length": 32,
            "memory_cost_kib": 65536,
            "extra": 1,
        },
    ],
)
def test_argon2_json_requires_exact_field_set(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Argon2idParameters.from_json(json.dumps(payload))


@pytest.mark.parametrize("value", [None, 1, True, b"{}"])
def test_argon2_json_requires_text(value: object) -> None:
    with pytest.raises(ValueError):
        Argon2idParameters.from_json(value)  # type: ignore[arg-type]


def test_argon2_json_roundtrip_preserves_current_profile() -> None:
    current = Argon2idParameters()

    restored = Argon2idParameters.from_json(current.to_json())

    assert restored == current


def test_argon2_v1_accepts_resource_ceiling_without_running_kdf() -> None:
    parameters = Argon2idParameters(
        iterations=10,
        lanes=16,
        memory_cost_kib=256 * 1024,
    )

    assert parameters.iterations == 10
    assert parameters.lanes == 16
    assert parameters.memory_cost_kib == 256 * 1024


@pytest.mark.parametrize(
    "field,value",
    [
        ("iterations", 11),
        ("lanes", 17),
        ("memory_cost_kib", 256 * 1024 + 1),
    ],
)
def test_argon2_v1_rejects_work_factors_above_resource_ceiling(
    field: str,
    value: int,
) -> None:
    kwargs: dict[str, object] = {field: value}

    with pytest.raises(ValueError, match="resource ceiling"):
        Argon2idParameters(**kwargs)  # type: ignore[arg-type]


def test_argon2_json_rejects_pathological_work_factors_before_kdf() -> None:
    payload = {
        "format_version": 1,
        "iterations": 1_000_000,
        "lanes": 4,
        "length": 32,
        "memory_cost_kib": 64 * 1024,
    }

    with pytest.raises(ValueError, match="resource ceiling"):
        Argon2idParameters.from_json(json.dumps(payload))
