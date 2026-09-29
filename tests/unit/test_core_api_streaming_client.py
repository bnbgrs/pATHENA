from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

from athena.api import client as client_module
from athena.api.client import CoreApiClient, CoreApiClientError
from athena.api.contracts import (
    ChatMessageResponse,
    ChatThreadResponse,
)


CHAT_ID = "11111111-1111-1111-1111-111111111111"
OPERATION_ID = "22222222-2222-4222-8222-222222222222"


class _StreamResponse:
    status = 200

    def __init__(self, events: list[dict[str, Any]]) -> None:
        self._lines = [
            (json.dumps(event) + "\n").encode("utf-8")
            for event in events
        ]

    def __enter__(self) -> "_StreamResponse":
        return self

    def __exit__(self, *args: object) -> bool:
        del args
        return False

    def __iter__(self):
        return iter(self._lines)


def _thread() -> ChatThreadResponse:
    return ChatThreadResponse(
        chat_id=CHAT_ID,
        started_at_us=1,
        ended_at_us=None,
        archive_mode="standard",
        lifecycle_state="active",
        messages=(
            ChatMessageResponse(
                message_id=OPERATION_ID,
                chat_id=CHAT_ID,
                sequence_no=1,
                message_type="user",
                actor_id="33333333-3333-4333-8333-333333333333",
                created_at_us=1,
                revision_id="44444444-4444-4444-8444-444444444444",
                content="hello",
                content_format="text/plain",
            ),
            ChatMessageResponse(
                message_id="55555555-5555-4555-8555-555555555555",
                chat_id=CHAT_ID,
                sequence_no=2,
                message_type="assistant",
                actor_id="66666666-6666-4666-8666-666666666666",
                created_at_us=2,
                revision_id="77777777-7777-4777-8777-777777777777",
                content="Hello world",
                content_format="text/plain",
            ),
        ),
    )


def _client(tmp_path, monkeypatch: pytest.MonkeyPatch) -> CoreApiClient:
    client = CoreApiClient(
        tmp_path,
        timeout_seconds=1.0,
        generation_timeout_seconds=2.0,
    )
    monkeypatch.setattr(
        client,
        "_load_bootstrap",
        lambda: SimpleNamespace(
            base_url="http://127.0.0.1:1234",
            token="test-token",
        ),
    )
    return client


def test_stream_chat_message_delivers_real_deltas_then_completed_thread(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(tmp_path, monkeypatch)
    thread = _thread()
    events = [
        {"type": "delta", "text": "Hello "},
        {"type": "delta", "text": "world"},
        {"type": "complete", "thread": thread.to_dict()},
    ]
    captured_request = None

    def fake_urlopen(request, timeout: float):
        nonlocal captured_request
        captured_request = request
        assert timeout == 2.0
        return _StreamResponse(events)

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    deltas: list[str] = []
    result = client.stream_chat_message(
        CHAT_ID,
        content="hello",
        model_id="publisher/model",
        operation_id=OPERATION_ID,
        effective_context_limit=8192,
        max_output_tokens=1024,
        temperature=0.5,
        thinking_enabled=False,
        on_delta=deltas.append,
    )

    assert deltas == ["Hello ", "world"]
    assert result == thread
    assert captured_request is not None
    assert captured_request.full_url.endswith(
        f"/api/v1/chats/{CHAT_ID}/messages/stream"
    )
    assert (
        captured_request.headers["Accept"]
        == "application/x-ndjson"
    )


def test_stream_chat_message_surfaces_cancellation_without_fake_completion(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(tmp_path, monkeypatch)
    monkeypatch.setattr(
        client_module,
        "urlopen",
        lambda request, timeout: _StreamResponse(
            [
                {"type": "delta", "text": "partial"},
                {
                    "type": "cancelled",
                    "message": "Generation stopped.",
                },
            ]
        ),
    )

    deltas: list[str] = []
    with pytest.raises(CoreApiClientError) as exc_info:
        client.stream_chat_message(
            CHAT_ID,
            content="hello",
            operation_id=OPERATION_ID,
            on_delta=deltas.append,
        )

    assert deltas == ["partial"]
    assert exc_info.value.code == "generation_cancelled"


def test_cancel_chat_operation_uses_stable_operation_identity(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = CoreApiClient(tmp_path)
    captured: dict[str, Any] = {}

    def fake_request(
        method: str,
        path: str,
        *,
        expected_status: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        captured.update(
            method=method,
            path=path,
            expected_status=expected_status,
            kwargs=kwargs,
        )
        return {
            "accepted": True,
            "operation_id": OPERATION_ID,
        }

    monkeypatch.setattr(client, "_request", fake_request)

    assert client.cancel_chat_operation(OPERATION_ID) is True
    assert captured["method"] == "POST"
    assert captured["expected_status"] == 202
    assert captured["path"] == (
        f"/api/v1/chat-operations/{OPERATION_ID}/cancel"
    )
