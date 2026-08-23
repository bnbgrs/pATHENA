from __future__ import annotations

import math

import pytest

from athena.jobs.lease_guard import blocking_operation_lease_seconds


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1.0, id="float"),
        pytest.param("1", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_blocking_operation_rejects_invalid_base_extension(value: object) -> None:
    with pytest.raises(ValueError, match="integer >= 1"):
        blocking_operation_lease_seconds(
            timeout_seconds=10,
            base_extend_seconds=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "timeout",
    [
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param("10", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_invalid_or_unbounded_provider_timeout_keeps_base_lease(timeout: object) -> None:
    assert blocking_operation_lease_seconds(
        timeout_seconds=timeout,
        base_extend_seconds=7,
    ) == 7


def test_blocking_operation_rounds_timeout_up_and_preserves_integer_result() -> None:
    result = blocking_operation_lease_seconds(
        timeout_seconds=2.01,
        base_extend_seconds=7,
    )

    assert result == 10
    assert isinstance(result, int)
    assert not isinstance(result, bool)


def test_finite_integer_timeout_extends_lease() -> None:
    assert blocking_operation_lease_seconds(
        timeout_seconds=12,
        base_extend_seconds=5,
    ) == 17


def test_timeout_exactly_base_still_adds_blocking_window() -> None:
    assert blocking_operation_lease_seconds(
        timeout_seconds=5.0,
        base_extend_seconds=5,
    ) == 10


def test_math_module_remains_finite_for_reference_case() -> None:
    result = blocking_operation_lease_seconds(
        timeout_seconds=math.nextafter(1.0, 2.0),
        base_extend_seconds=1,
    )
    assert result == 3
