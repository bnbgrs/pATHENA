from __future__ import annotations

import io

import pytest

from athena.model.adapters.local_http import (
    LocalResponseTooLargeError,
    _BoundedLocalResponse,
)


class _RecordingBytesIO(io.BytesIO):
    def __init__(self, initial_bytes: bytes) -> None:
        super().__init__(initial_bytes)
        self.read_sizes: list[int] = []
        self.readline_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return super().read(size)

    def readline(self, size: int = -1) -> bytes:
        self.readline_sizes.append(size)
        return super().readline(size)


def test_chunked_reads_cannot_bypass_cumulative_response_limit() -> None:
    response = _BoundedLocalResponse(io.BytesIO(b"abcdef"), max_bytes=5)

    assert response.read(3) == b"abc"
    with pytest.raises(LocalResponseTooLargeError, match="configured byte limit"):
        response.read(3)


def test_exact_cumulative_limit_still_allows_eof() -> None:
    response = _BoundedLocalResponse(io.BytesIO(b"abcde"), max_bytes=5)

    assert response.read(2) == b"ab"
    assert response.read(3) == b"cde"
    assert response.read(1) == b""


def test_read_after_readline_shares_the_same_response_budget() -> None:
    response = _BoundedLocalResponse(io.BytesIO(b"ab\ncdef"), max_bytes=5)

    assert response.readline() == b"ab\n"
    with pytest.raises(LocalResponseTooLargeError, match="configured byte limit"):
        response.read(3)


def test_readline_only_requests_remaining_budget_plus_detection_byte() -> None:
    raw = _RecordingBytesIO(b"abcdef\n")
    response = _BoundedLocalResponse(raw, max_bytes=5)

    assert response.read(3) == b"abc"
    with pytest.raises(LocalResponseTooLargeError, match="configured byte limit"):
        response.readline()

    assert raw.readline_sizes == [3]


def test_readline_after_exact_limit_reads_only_one_detection_byte() -> None:
    raw = _RecordingBytesIO(b"abcdef")
    response = _BoundedLocalResponse(raw, max_bytes=5)

    assert response.read(5) == b"abcde"
    with pytest.raises(LocalResponseTooLargeError, match="configured byte limit"):
        response.readline()

    assert raw.readline_sizes == [1]


def test_negative_read_is_bounded_like_read_all() -> None:
    response = _BoundedLocalResponse(io.BytesIO(b"abcdef"), max_bytes=5)

    with pytest.raises(LocalResponseTooLargeError, match="configured byte limit"):
        response.read(-1)


def test_direct_read_rejects_expired_total_deadline_before_underlying_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter([10.0, 11.0])
    monkeypatch.setattr(
        "athena.model.adapters.local_http.monotonic",
        lambda: next(times),
    )
    raw = _RecordingBytesIO(b"abc")
    response = _BoundedLocalResponse(
        raw,
        max_bytes=5,
        total_timeout_seconds=0.5,
    )

    with pytest.raises(TimeoutError, match="total timeout"):
        response.read(1)

    assert raw.read_sizes == []


def test_direct_readline_rejects_expired_total_deadline_before_underlying_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter([20.0, 21.0])
    monkeypatch.setattr(
        "athena.model.adapters.local_http.monotonic",
        lambda: next(times),
    )
    raw = _RecordingBytesIO(b"abc\n")
    response = _BoundedLocalResponse(
        raw,
        max_bytes=5,
        total_timeout_seconds=0.5,
    )

    with pytest.raises(TimeoutError, match="total timeout"):
        response.readline()

    assert raw.readline_sizes == []


def test_direct_read_fails_closed_when_deadline_expires_during_underlying_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    times = iter([30.0, 30.2, 31.0])
    monkeypatch.setattr(
        "athena.model.adapters.local_http.monotonic",
        lambda: next(times),
    )
    raw = _RecordingBytesIO(b"abc")
    response = _BoundedLocalResponse(
        raw,
        max_bytes=5,
        total_timeout_seconds=0.5,
    )

    with pytest.raises(TimeoutError, match="total timeout"):
        response.read(1)

    assert raw.read_sizes == [1]
