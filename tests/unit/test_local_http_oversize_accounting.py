from __future__ import annotations

import pytest

from athena.model.adapters.local_http import (
    LocalResponseTooLargeError,
    _BoundedLocalResponse,
)


class _OversizedReadResponse:
    def __init__(self) -> None:
        self.calls = 0

    def read(self, size: int) -> bytes:
        self.calls += 1
        return b"x" * (size + 1)


class _OversizedLineResponse:
    def __init__(self) -> None:
        self.calls = 0

    def readline(self, size: int) -> bytes:
        self.calls += 1
        return b"x" * (size + 1)


def test_oversized_read_rejects_without_counting_and_poisons_followup_io() -> None:
    response = _OversizedReadResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    with pytest.raises(LocalResponseTooLargeError):
        bounded.read()

    assert bounded._bytes_read == 0
    assert response.calls == 1

    with pytest.raises(LocalResponseTooLargeError):
        bounded.read(1)

    assert bounded._bytes_read == 0
    assert response.calls == 1


def test_oversized_readline_rejects_without_counting_and_poisons_followup_io() -> None:
    response = _OversizedLineResponse()
    bounded = _BoundedLocalResponse(response, max_bytes=4)

    with pytest.raises(LocalResponseTooLargeError):
        bounded.readline()

    assert bounded._bytes_read == 0
    assert response.calls == 1

    with pytest.raises(LocalResponseTooLargeError):
        bounded.readline()

    assert bounded._bytes_read == 0
    assert response.calls == 1
