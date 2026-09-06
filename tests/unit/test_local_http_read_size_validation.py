from __future__ import annotations

from typing import Any

import pytest

from athena.model.adapters.local_http import _BoundedLocalResponse


class _TrackingResponse:
    def __init__(self) -> None:
        self.read_calls = 0

    def read(self, size: int) -> bytes:
        self.read_calls += 1
        return b"x" * max(0, size)


@pytest.mark.parametrize("invalid_size", [True, 1.5, "1"])
def test_bounded_local_response_rejects_invalid_read_size_before_delegate(
    invalid_size: Any,
) -> None:
    response = _TrackingResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=16)

    with pytest.raises(
        TypeError,
        match="read size must be an integer or None",
    ):
        bounded.read(invalid_size)

    assert response.read_calls == 0


def test_bounded_local_response_still_accepts_negative_integer_read_size() -> None:
    response = _TrackingResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    assert bounded.read(-1) == b"xxxx"
    assert response.read_calls == 1
