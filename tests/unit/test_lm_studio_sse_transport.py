from __future__ import annotations

from unittest.mock import patch

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.adapters.local_http import _BoundedLocalResponse
from athena.model.domain import ModelChatMessage


class _Headers:
    def get_content_type(self) -> str:
        return "text/event-stream"


class _WireResponse:
    headers = _Headers()

    def __init__(self, lines: list[bytes]) -> None:
        self._lines = iter(lines)

    def __enter__(self) -> "_WireResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def readline(self, size: int = -1) -> bytes:
        del size
        return next(self._lines, b"")


def _bounded(lines: list[bytes]) -> _BoundedLocalResponse:
    return _BoundedLocalResponse(
        _WireResponse(lines),
        max_bytes=1024 * 1024,
        total_timeout_seconds=5.0,
    )


def test_lm_studio_stream_consumes_complete_multiline_sse_events() -> None:
    response = _bounded(
        [
            b"\xef\xbb\xbf: keepalive\r\n",
            b"event: message\r\n",
            b'data: {"choices": [\r\n',
            b'data: {"delta": {"content": "Hello"}}]}\r\n',
            b"\r\n",
            b"id: 2\n",
            b'data: {"choices": [{"delta": {"content": " world"}}]}\n',
            b"\n",
            b"data: [DONE]\n",
        ]
    )
    provider = LMStudioProvider("http://127.0.0.1:1234")

    with patch(
        "athena.model.adapters.lm_studio.open_local_request",
        return_value=response,
    ):
        chunks = tuple(
            provider.stream_chat(
                model_id="example/model",
                messages=(ModelChatMessage(role="user", content="Hi"),),
            )
        )

    assert chunks == ("Hello", " world")


def test_sse_transport_preserves_non_data_fields_as_non_payload() -> None:
    response = _bounded(
        [
            b": comment\n",
            b"retry: 1000\n",
            b"event: ping\n",
            b"\n",
            b"data: [DONE]\n",
        ]
    )

    assert tuple(response) == (b"data:[DONE]\n",)
