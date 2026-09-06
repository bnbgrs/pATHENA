from __future__ import annotations

import pytest

from athena.model.adapters.local_http import (
    LocalResponseTooLargeError,
    _BoundedLocalResponse,
)


class _TrackingReadResponse:
    def __init__(self) -> None:
        self.calls = 0

    def read(self, size: int) -> bytes:
        self.calls += 1
        return b"unexpected"


def test_zero_byte_read_does_not_touch_delegate_or_accounting() -> None:
    response = _TrackingReadResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    assert bounded.read(0) == b""
    assert response.calls == 0
    assert bounded._bytes_read == 0


def test_zero_byte_read_still_honors_poisoned_budget_before_delegate() -> None:
    response = _TrackingReadResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)
    bounded._byte_budget_poisoned = True

    with pytest.raises(LocalResponseTooLargeError):
        bounded.read(0)

    assert response.calls == 0
    assert bounded._bytes_read == 0


def test_zero_byte_read_still_requires_callable_read_delegate() -> None:
    bounded = _BoundedLocalResponse(object(), max_bytes=4)

    with pytest.raises(OSError, match="bounded read access"):
        bounded.read(0)
