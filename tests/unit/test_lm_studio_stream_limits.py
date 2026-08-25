from __future__ import annotations

from collections.abc import Iterator

import pytest

import athena.model.adapters.local_http as local_http
from athena.model.adapters.local_http import (
    LocalResponseTooLargeError,
    _BoundedLocalResponse,
)


class _LineResponse:
    def __init__(self, lines: list[bytes]) -> None:
        self._lines = iter(lines)
        self.readline_limits: list[int] = []

    def readline(self, limit: int) -> bytes:
        self.readline_limits.append(limit)
        try:
            return next(self._lines)
        except StopIteration:
            return b""


class _OversizeLineResponse:
    def __init__(self, *, sentinel: bytes) -> None:
        self.sentinel = sentinel
        self.readline_limits: list[int] = []

    def readline(self, limit: int) -> bytes:
        self.readline_limits.append(limit)
        return self.sentinel + (b"x" * max(0, limit - len(self.sentinel)))


def test_streaming_lines_are_read_with_max_plus_one_boundary() -> None:
    backend = _LineResponse([b"12345678"])
    response = _BoundedLocalResponse(backend, max_bytes=8)

    assert response.readline() == b"12345678"
    assert backend.readline_limits == [9]


def test_oversize_streaming_line_fails_closed_without_content_leak() -> None:
    sentinel = b"SECRET"
    backend = _OversizeLineResponse(sentinel=sentinel)
    response = _BoundedLocalResponse(backend, max_bytes=8)

    with pytest.raises(LocalResponseTooLargeError) as raised:
        response.readline()

    assert backend.readline_limits == [9]
    assert sentinel.decode() not in str(raised.value)


def test_streaming_total_deadline_stops_continuously_active_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times: Iterator[float] = iter([10.0, 10.2, 10.6, 11.0])
    monkeypatch.setattr(local_http, "monotonic", lambda: next(times))
    backend = _LineResponse([b": heartbeat\n", b": heartbeat\n"])
    response = _BoundedLocalResponse(
        backend,
        max_bytes=64,
        total_timeout_seconds=1.0,
    )

    iterator = iter(response)
    assert next(iterator) == b": heartbeat\n"
    with pytest.raises(TimeoutError, match="total timeout"):
        next(iterator)


def test_normal_stream_iteration_preserves_sse_framing_lines() -> None:
    lines = [
        b"\n",
        b": keepalive\n",
        b'data: {"choices": []}\n',
        b"data: [DONE]\n",
    ]
    backend = _LineResponse([*lines, b""])
    response = _BoundedLocalResponse(backend, max_bytes=128)

    assert list(response) == lines
    assert all(limit == 129 for limit in backend.readline_limits)
