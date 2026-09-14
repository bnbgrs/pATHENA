from __future__ import annotations

from email.message import Message
from io import BytesIO

import pytest

import athena.model.adapters.local_http as local_http
from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import ModelChatMessage


class _FakeResponse(BytesIO):
    def __init__(self, body: bytes, *, content_type: str) -> None:
        super().__init__(body)
        self.headers = Message()
        self.headers["Content-Type"] = content_type


class _FakeOpener:
    def __init__(self, body: bytes, *, content_type: str) -> None:
        self._body = body
        self._content_type = content_type

    def open(self, request, *, timeout: float) -> _FakeResponse:
        del request, timeout
        return _FakeResponse(self._body, content_type=self._content_type)


def _install_body(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
    *,
    content_type: str = "text/event-stream; charset=utf-8",
) -> None:
    monkeypatch.setattr(
        local_http,
        "build_opener",
        lambda *handlers: _FakeOpener(body, content_type=content_type),
    )


def _request() -> local_http.Request:
    return local_http.Request(
        "http://127.0.0.1:1234/v1/chat/completions",
        headers={"Accept": "text/event-stream"},
    )


def test_sse_frames_multiline_data_and_ignores_non_data_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = (
        b"\xef\xbb\xbf: initial comment\r\n"
        b"event: message\r\n"
        b"id: 7\r\n"
        b"retry: 1000\r\n"
        b"unknown: ignored\r\n"
        b'data: {"choices": [\r\n'
        b'data: {"delta": {"content": "Hello"}}]}\r\n'
        b"\r\n"
        b": keepalive\n"
        b"event: done\n"
        b"\n"
        b"data: [DONE]"
    )
    _install_body(monkeypatch, body)

    response = local_http.open_local_request(_request(), timeout=2.0)

    assert tuple(response) == (
        b'data:{"choices": [\n{"delta": {"content": "Hello"}}]}\n',
        b"data:[DONE]\n",
    )


def test_sse_event_without_data_yields_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_body(
        monkeypatch,
        b"event: ping\nid: 3\nretry: 50\nunknown: ignored\n\n: comment\n\n",
    )

    response = local_http.open_local_request(_request(), timeout=2.0)

    assert tuple(response) == ()


def test_non_sse_iteration_remains_physical_lines_even_when_requested_as_sse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = b"data: one\ndata: two\n\n"
    _install_body(monkeypatch, body, content_type="application/json")

    response = local_http.open_local_request(_request(), timeout=2.0)

    assert tuple(response) == (b"data: one\n", b"data: two\n", b"\n")


def test_sse_framing_cannot_bypass_raw_byte_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_body(monkeypatch, b"data: 1234567890\n\n")
    monkeypatch.setattr(local_http, "MAX_LOCAL_RESPONSE_BYTES", 8)
    response = local_http.open_local_request(_request(), timeout=2.0)

    with pytest.raises(local_http.LocalResponseTooLargeError, match="byte limit"):
        tuple(response)


def test_sse_framing_preserves_total_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_body(monkeypatch, b"data: one\n\n")
    clock = iter((0.0, 0.1, 0.2, 1.0))
    monkeypatch.setattr(local_http, "monotonic", lambda: next(clock))
    response = local_http.open_local_request(_request(), timeout=1.0)

    with pytest.raises(TimeoutError, match="total timeout"):
        tuple(response)


def test_lm_studio_accepts_one_json_event_split_across_data_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    body = (
        b'data: {"choices": [\n'
        b'data: {"delta": {"content": "Hello"}}]}\n'
        b"\n"
        b"data: [DONE]"
    )
    _install_body(monkeypatch, body)
    provider = LMStudioProvider("http://127.0.0.1:1234")

    chunks = tuple(
        provider.stream_chat(
            model_id="example/model",
            messages=(ModelChatMessage(role="user", content="Hi"),),
        )
    )

    assert chunks == ("Hello",)
