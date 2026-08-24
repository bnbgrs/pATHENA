from __future__ import annotations

import math

import pytest

from athena.jobs.lease_guard import blocking_operation_lease_seconds


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "30", None])
def test_lease_guard_rejects_invalid_base_extension(value: object) -> None:
    with pytest.raises(ValueError, match="base_extend_seconds must be an integer >= 1"):
        blocking_operation_lease_seconds(
            timeout_seconds=30,
            base_extend_seconds=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "timeout",
    [True, False, 0, -1, 0.0, -1.5, float("nan"), float("inf"), float("-inf"), "30", None],
)
def test_lease_guard_falls_back_for_unusable_timeout(timeout: object) -> None:
    assert (
        blocking_operation_lease_seconds(
            timeout_seconds=timeout,
            base_extend_seconds=7,
        )
        == 7
    )


def test_lease_guard_handles_huge_integer_timeout_without_float_conversion() -> None:
    huge = 10**400

    value = blocking_operation_lease_seconds(
        timeout_seconds=huge,
        base_extend_seconds=7,
    )

    assert value == huge + 7


def test_lease_guard_rounds_positive_float_timeout_up() -> None:
    value = blocking_operation_lease_seconds(
        timeout_seconds=3.25,
        base_extend_seconds=7,
    )

    assert value == 11
    assert math.isfinite(float(value))
