from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from athena.api.asgi import CoreApiAsgiApp
from athena.api.client import CoreApiClient
from athena.api.contracts import HealthResponse, JsonValue
from athena.api.runtime import LocalApiRuntime


@dataclass
class _UnifiedSurface:
    operation_id: str | None = None

    def send_unified_local_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        requested_embedding_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> HealthResponse:
        del (
            requested_model_id,
            requested_embedding_model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert chat_id == "11111111-1111-1111-1111-111111111111"
        assert content == "hello"
        self.operation_id = operation_id
        return HealthResponse(api_version="v1", core_status="ok", detail=None)


class _CaptureClient(CoreApiClient):
    def __init__(self, runtime_root: Path) -> None:
        super().__init__(runtime_root)
        self.body: dict[str, JsonValue] | None = None

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str] | None = None,
        expected_status: int,
        json_body: dict[str, JsonValue] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, JsonValue]:
        del query, timeout_seconds
        assert method == "POST"
        assert path.endswith("/messages/unified-local")
        assert expected_status == 200
        assert json_body is not None
        self.body = dict(json_body)
        return {
            "thread": {
                "chat_id": "11111111-1111-1111-1111-111111111111",
                "started_at_us": 1,
                "ended_at_us": None,
                "archive_mode": "archive",
                "lifecycle_state": "active",
                "messages": [],
            },
            "assistant_text": "answer",
            "evidence": [],
            "personal_memory": [],
            "grounding": {
                "cited_context_ids": [],
                "canonical_context_ids": [],
                "user_statement_context_ids": [],
                "conversation_context_ids": [],
                "source_context_ids": [],
                "research_context_ids": [],
                "news_context_ids": [],
                "invalid_context_ids": [],
                "uses_inference": False,
                "uses_model_prior": True,
                "uses_unknown": False,
                "has_provenance_marker": True,
            },
            "processing_run_id": "22222222-2222-4222-8222-222222222222",
            "model_id": "primary",
            "embedding_model_id": None,
        }


async def _post(
    app: CoreApiAsgiApp,
    *,
    token: str,
    operation_id: object,
) -> tuple[int, dict[str, Any]]:
    body = json.dumps(
        {
            "content": "hello",
            "operation_id": operation_id,
        }
    ).encode("utf-8")
    scope: dict[str, Any] = {
        "type": "http",
        "method": "POST",
        "path": (
            "/api/v1/chats/11111111-1111-1111-1111-111111111111/"
            "messages/unified-local"
        ),
        "query_string": b"",
        "headers": [
            (b"authorization", f"Bearer {token}".encode("ascii")),
        ],
    }
    received = False

    async def receive() -> dict[str, Any]:
        nonlocal received
        assert not received
        received = True
        return {
            "type": "http.request",
            "body": body,
            "more_body": False,
        }

    sent: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    assert len(sent) == 2
    status = int(sent[0]["status"])
    payload = json.loads(sent[1]["body"].decode("utf-8"))
    assert isinstance(payload, dict)
    return status, payload


def _app(tmp_path: Path) -> tuple[CoreApiAsgiApp, LocalApiRuntime, str, _UnifiedSurface]:
    runtime = LocalApiRuntime(tmp_path / "api")
    runtime.publish(port=32124)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    surface = _UnifiedSurface()
    app = CoreApiAsgiApp(
        facade=surface,  # type: ignore[arg-type]
        runtime=runtime,
    )
    return app, runtime, token, surface


def test_asgi_canonicalizes_and_forwards_unified_operation_id(tmp_path: Path) -> None:
    app, _runtime, token, surface = _app(tmp_path)
    operation_id = uuid.UUID("AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA")

    status, payload = asyncio.run(
        _post(
            app,
            token=token,
            operation_id=str(operation_id).upper(),
        )
    )

    assert status == 200
    assert payload["core_status"] == "ok"
    assert surface.operation_id == str(operation_id)


def test_asgi_rejects_invalid_unified_operation_id_before_facade(tmp_path: Path) -> None:
    app, _runtime, token, surface = _app(tmp_path)

    status, payload = asyncio.run(
        _post(
            app,
            token=token,
            operation_id="not-a-uuid",
        )
    )

    assert status == 400
    assert payload["code"] == "invalid_request"
    assert surface.operation_id is None


def test_client_canonicalizes_unified_operation_id_in_json(tmp_path: Path) -> None:
    client = _CaptureClient(tmp_path)
    operation_id = uuid.UUID("AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA")

    response = client.send_unified_local_chat_message(
        "11111111-1111-1111-1111-111111111111",
        content="hello",
        operation_id=str(operation_id).upper(),
    )

    assert response.assistant_text == "answer"
    assert client.body is not None
    assert client.body["operation_id"] == str(operation_id)


def test_client_rejects_invalid_unified_operation_id_before_request(tmp_path: Path) -> None:
    client = _CaptureClient(tmp_path)

    with pytest.raises(ValueError, match="operation_id"):
        client.send_unified_local_chat_message(
            "11111111-1111-1111-1111-111111111111",
            content="hello",
            operation_id="not-a-uuid",
        )

    assert client.body is None
