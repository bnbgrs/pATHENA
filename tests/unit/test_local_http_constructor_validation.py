from __future__ import annotations

from typing import Any

import pytest

from athena.model.adapters.local_http import _BoundedLocalResponse


class _UnusedResponse:
    def read(self, size: int) -> bytes:
        raise AssertionError("delegate read must not be reached")


@pytest.mark.parametrize("invalid_max_bytes", [True, False, 0, -1, 1.5, "32"])
def test_bounded_local_response_rejects_invalid_byte_limit(
    invalid_max_bytes: Any,
) -> None:
    with pytest.raises(
        ValueError,
        match="byte limit must be a positive integer",
    ):
        _BoundedLocalResponse(_UnusedResponse(), max_bytes=invalid_max_bytes)


@pytest.mark.parametrize(
    "invalid_timeout",
    [True, False, 0.0, -1.0, float("nan"), float("inf"), float("-inf")],
)
def test_bounded_local_response_rejects_invalid_total_timeout(
    invalid_timeout: Any,
) -> None:
    with pytest.raises(
        ValueError,
        match="timeout must be a finite number > 0",
    ):
        _BoundedLocalResponse(
            _UnusedResponse(),
            max_bytes=32,
            total_timeout_seconds=invalid_timeout,
        )


def test_bounded_local_response_accepts_valid_limits() -> None:
    bounded = _BoundedLocalResponse(
        _UnusedResponse(),
        max_bytes=32,
        total_timeout_seconds=1,
    )

    assert bounded._max_bytes == 32
    assert bounded._deadline is not None
