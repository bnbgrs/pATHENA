from __future__ import annotations

from typing import Any

import pytest

from athena.model.adapters.local_http import _BoundedLocalResponse


class _MalformedBodyResponse:
    def __init__(self, value: Any) -> None:
        self.value = value
        self.read_calls = 0
        self.readline_calls = 0

    def read(self, size: int) -> Any:
        self.read_calls += 1
        return self.value

    def readline(self, size: int) -> Any:
        self.readline_calls += 1
        return self.value


@pytest.mark.parametrize("invalid_body", ["text", bytearray(b"bytes"), memoryview(b"bytes")])
def test_bounded_local_response_rejects_non_bytes_read_body(invalid_body: Any) -> None:
    response = _MalformedBodyResponse(invalid_body)
    bounded = _BoundedLocalResponse(response, max_bytes=32)

    with pytest.raises(OSError, match="response body must be bytes"):
        bounded.read()

    assert response.read_calls == 1
    assert bounded._bytes_read == 0


@pytest.mark.parametrize("invalid_body", ["line", bytearray(b"line"), memoryview(b"line")])
def test_bounded_local_response_rejects_non_bytes_stream_line(invalid_body: Any) -> None:
    response = _MalformedBodyResponse(invalid_body)
    bounded = _BoundedLocalResponse(response, max_bytes=32)

    with pytest.raises(OSError, match="response body must be bytes"):
        bounded.readline()

    assert response.readline_calls == 1
    assert bounded._bytes_read == 0
