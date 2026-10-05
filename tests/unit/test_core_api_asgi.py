from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from athena.api.asgi import CoreApiAsgiApp
from athena.api.runtime import LocalApiRuntime
from athena.api.service import CoreApiFacade
from athena.chat.models import ChatMessage, ChatSummary, ChatThread, MessageType
from athena.model.domain import ModelInfo, ProviderHealth, ProviderHealthStatus
from athena.observability.health import HealthService
from athena.retrieval.universal import (
    UniversalSearchEntityType,
    UniversalSearchResult,
)


class _Chat:
    def __init__(self) -> None:
        self.chat_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        self.message_id = uuid.UUID("22222222-2222-2222-2222-222222222222")
        self.revision_id = uuid.UUID("33333333-3333-3333-3333-333333333333")
        self.actor_id = uuid.UUID("44444444-4444-4444-4444-444444444444")
        self.edited_revision_id = uuid.UUID("55555555-5555-5555-5555-555555555555")
        self.fork_chat_id = uuid.UUID("66666666-6666-6666-6666-666666666666")
        self.fork_message_id = uuid.UUID("77777777-7777-7777-7777-777777777777")
        self.fork_revision_id = uuid.UUID("88888888-8888-8888-8888-888888888888")
        self.content = "hello"

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummary, ...]:
        assert limit > 0
        assert offset >= 0
        return (
            ChatSummary(
                chat_id=self.chat_id,
                started_at_us=10,
                ended_at_us=None,
                archive_mode="standard",
                lifecycle_state="active",
                message_count=1,
            ),
        )

    def create_chat(self) -> uuid.UUID:
        return self.chat_id

    def load_chat(self, chat_id: uuid.UUID) -> ChatThread:
        if chat_id == self.chat_id:
            message_id = self.message_id
            revision_id = self.revision_id
            content = self.content
        else:
            assert chat_id == self.fork_chat_id
            message_id = self.fork_message_id
            revision_id = self.fork_revision_id
            content = self.content
        return ChatThread(
            chat_id=chat_id,
            started_at_us=10,
            ended_at_us=None,
            archive_mode="standard",
            lifecycle_state="active",
            messages=(
                ChatMessage(
                    message_id=message_id,
                    chat_id=chat_id,
                    sequence_no=1,
                    message_type=MessageType.USER,
                    actor_id=self.actor_id,
                    created_at_us=11,
                    revision_id=revision_id,
                    content=content,
                    content_format="text/plain",
                ),
            ),
        )

    def edit_user_message(
        self,
        *,
        chat_id: uuid.UUID,
        message_id: uuid.UUID,
        expected_revision_id: uuid.UUID,
        content: str,
    ) -> ChatMessage:
        assert chat_id == self.chat_id
        assert message_id == self.message_id
        assert expected_revision_id == self.revision_id
        self.content = content
        self.revision_id = self.edited_revision_id
        return self.load_chat(self.chat_id).messages[0]

    def fork_chat_from_message(
        self,
        *,
        chat_id: uuid.UUID,
        source_message_id: uuid.UUID,
        source_revision_id: uuid.UUID,
    ) -> uuid.UUID:
        assert chat_id == self.chat_id
        assert source_message_id == self.message_id
        assert source_revision_id == self.revision_id
        return self.fork_chat_id


class _News:
    def __init__(self) -> None:
        self.value = {
            "enabled": 1,
            "timezone_name": "Europe/Berlin",
            "local_hour": 7,
            "local_minute": 0,
        }

    def profile(self) -> dict[str, object]:
        return dict(self.value)

    def configure_profile(
        self,
        *,
        timezone_name: str | None = None,
        local_hour: int | None = None,
        local_minute: int | None = None,
    ) -> dict[str, object]:
        if timezone_name is not None:
            self.value["timezone_name"] = timezone_name
        if local_hour is not None:
            self.value["local_hour"] = local_hour
        if local_minute is not None:
            self.value["local_minute"] = local_minute
        return dict(self.value)


class _UniversalSearch:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                str,
                int,
                tuple[UniversalSearchEntityType, ...] | None,
            ]
        ] = []

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[UniversalSearchResult, ...]:
        self.calls.append((query, limit, entity_types))
        return (
            UniversalSearchResult(
                result_ref="source:55555555-5555-5555-5555-555555555555",
                entity_id=uuid.UUID("55555555-5555-5555-5555-555555555555"),
                revision_id=None,
                entity_type=UniversalSearchEntityType.SOURCE,
                title="Alpha.pdf",
                preview="application/pdf",
                rank=1,
            ),
        )


class _Provider:
    @property
    def provider_id(self) -> str:
        return "lm_studio"

    def health(self) -> ProviderHealth:
        return ProviderHealth(status=ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (
            ModelInfo(
                provider="lm_studio",
                backend_model_id="example/model",
                display_name="Example Model",
                model_type="llm",
                context_capacity=262144,
                quantization="Q4_K_S",
                loaded=True,
                vision=True,
                trained_for_tool_use=True,
                loaded_context_length=8192,
            ),
        )


def _facade() -> CoreApiFacade:
    health = HealthService()
    health.mark_ok()
    return CoreApiFacade(
        health=health,
        chat=_Chat(),  # type: ignore[arg-type]
        model_provider=_Provider(),
    )


async def _request(
    app: CoreApiAsgiApp,
    runtime: LocalApiRuntime,
    *,
    method: str,
    path: str,
    query: bytes = b"",
    token: str | None = None,
    origin: str | None = None,
    body: bytes = b"",
) -> tuple[int, dict[str, str], dict[str, Any]]:
    headers: list[tuple[bytes, bytes]] = []
    if token is not None:
        headers.append((b"authorization", f"Bearer {token}".encode("ascii")))
    if origin is not None:
        headers.append((b"origin", origin.encode("ascii")))

    scope: dict[str, Any] = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query,
        "headers": headers,
    }
    receive_calls = 0

    async def receive() -> dict[str, Any]:
        nonlocal receive_calls
        receive_calls += 1
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
    start, response = sent
    assert start["type"] == "http.response.start"
    assert response["type"] == "http.response.body"
    response_headers = {
        key.decode("ascii"): value.decode("ascii") for key, value in start["headers"]
    }
    payload = json.loads(response["body"].decode("utf-8"))
    return int(start["status"]), response_headers, payload


def _app(tmp_path) -> tuple[CoreApiAsgiApp, LocalApiRuntime, str]:
    runtime = LocalApiRuntime(tmp_path / "api")
    runtime.publish(port=32123)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    return CoreApiAsgiApp(facade=_facade(), runtime=runtime), runtime, token


def _news_app(tmp_path) -> tuple[CoreApiAsgiApp, LocalApiRuntime, str]:
    runtime = LocalApiRuntime(tmp_path / "news-api")
    runtime.publish(port=32124)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    facade = _facade()
    facade.attach_news(_News())
    return CoreApiAsgiApp(facade=facade, runtime=runtime), runtime, token


def test_asgi_chat_cancel_reports_known_and_unknown_operation_truthfully(
    tmp_path,
) -> None:
    runtime = LocalApiRuntime(tmp_path / "cancel-api")
    runtime.publish(port=32125)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    facade = _facade()
    operation_id = "55555555-5555-4555-8555-555555555555"
    reservation = facade.reserve_chat_operation(operation_id)
    assert reservation is not None
    app = CoreApiAsgiApp(facade=facade, runtime=runtime)

    known_status, _, known = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path=f"/api/v1/chat-operations/{operation_id}/cancel",
            token=token,
        )
    )
    assert known_status == 202
    assert known == {
        "accepted": True,
        "operation_id": operation_id,
    }
    assert reservation.cancel_requested() is True

    facade.release_chat_operation(reservation)

    late_status, _, late = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path=f"/api/v1/chat-operations/{operation_id}/cancel",
            token=token,
        )
    )
    assert late_status == 202
    assert late == {
        "accepted": False,
        "operation_id": operation_id,
    }


def test_asgi_chat_edit_and_fork_use_durable_core_contracts(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"
    revision_id = "33333333-3333-3333-3333-333333333333"

    edit_status, _, edited = asyncio.run(
        _request(
            app,
            runtime,
            method="PATCH",
            path=f"/api/v1/chats/{chat_id}/messages/{message_id}/edit",
            token=token,
            body=json.dumps(
                {
                    "expected_revision_id": revision_id,
                    "content": "revised",
                }
            ).encode("utf-8"),
        )
    )
    assert edit_status == 200
    assert edited["chat_id"] == chat_id
    assert edited["messages"][0]["content"] == "revised"
    assert edited["messages"][0]["revision_id"] == (
        "55555555-5555-5555-5555-555555555555"
    )

    fork_app, fork_runtime, fork_token = _app(tmp_path / "fork")
    fork_status, _, forked = asyncio.run(
        _request(
            fork_app,
            fork_runtime,
            method="POST",
            path=f"/api/v1/chats/{chat_id}/messages/{message_id}/fork",
            token=fork_token,
            body=json.dumps({"revision_id": revision_id}).encode("utf-8"),
        )
    )
    assert fork_status == 201
    assert forked["chat_id"] == "66666666-6666-6666-6666-666666666666"
    assert forked["chat_id"] != chat_id
    assert forked["messages"][0]["content"] == "hello"


def test_asgi_chat_edit_and_fork_validate_revision_payloads(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"

    edit_status, _, edit_problem = asyncio.run(
        _request(
            app,
            runtime,
            method="PATCH",
            path=f"/api/v1/chats/{chat_id}/messages/{message_id}/edit",
            token=token,
            body=json.dumps(
                {
                    "expected_revision_id": "not-a-uuid",
                    "content": "revised",
                }
            ).encode("utf-8"),
        )
    )
    assert edit_status == 400
    assert edit_problem["code"] == "invalid_request"

    fork_status, _, fork_problem = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path=f"/api/v1/chats/{chat_id}/messages/{message_id}/fork",
            token=token,
            body=json.dumps({"revision_id": ""}).encode("utf-8"),
        )
    )
    assert fork_status == 400
    assert fork_problem["code"] == "invalid_request"


def test_asgi_universal_search_parses_filters_and_returns_core_results(
    tmp_path,
) -> None:
    runtime = LocalApiRuntime(tmp_path / "search-api")
    runtime.publish(port=32126)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    facade = _facade()
    search = _UniversalSearch()
    facade.attach_universal_search(search)
    app = CoreApiAsgiApp(facade=facade, runtime=runtime)

    status, _, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/search",
            query=b"q=alpha&limit=7&types=source%2Cjob",
            token=token,
        )
    )

    assert status == 200
    assert search.calls == [
        (
            "alpha",
            7,
            (
                UniversalSearchEntityType.SOURCE,
                UniversalSearchEntityType.JOB,
            ),
        )
    ]
    assert payload["items"][0]["result_ref"] == (
        "source:55555555-5555-5555-5555-555555555555"
    )
    assert payload["items"][0]["revision_id"] is None

    invalid_status, _, invalid = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/search",
            query=b"q=alpha&types=not-real",
            token=token,
        )
    )
    assert invalid_status == 400
    assert invalid["code"] == "invalid_request"


def test_asgi_requires_session_token(tmp_path) -> None:
    app, runtime, _token = _app(tmp_path)

    status, headers, payload = asyncio.run(
        _request(app, runtime, method="GET", path="/api/v1/health")
    )

    assert status == 401
    assert headers["www-authenticate"] == "Bearer"
    assert payload["code"] == "unauthorized"
    assert "request_id" in payload


def test_asgi_rejects_browser_origin_even_with_token(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    status, _headers, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/health",
            token=token,
            origin="http://example.test",
        )
    )

    assert status == 403
    assert payload["code"] == "browser_origin_rejected"


def test_asgi_health_and_capabilities(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    health_status, health_headers, health = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/health",
            token=token,
        )
    )
    capabilities_status, _, capabilities = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/capabilities",
            token=token,
        )
    )

    assert health_status == 200
    assert health["core_status"] == "ok"
    assert health_headers["content-type"] == "application/json; charset=utf-8"
    assert health_headers["x-request-id"]
    assert capabilities_status == 200
    assert "chat.read" in capabilities["features"]


def test_asgi_news_schedule_read_and_update(tmp_path) -> None:
    app, runtime, token = _news_app(tmp_path)

    read_status, _, initial = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/news/profile",
            token=token,
        )
    )
    save_status, _, saved = asyncio.run(
        _request(
            app,
            runtime,
            method="PUT",
            path="/api/v1/news/profile",
            token=token,
            body=json.dumps(
                {
                    "timezone_name": "Europe/Berlin",
                    "local_hour": 6,
                    "local_minute": 30,
                }
            ).encode("utf-8"),
        )
    )

    assert read_status == 200
    assert initial["enabled"] is True
    assert (initial["local_hour"], initial["local_minute"]) == (7, 0)
    assert save_status == 200
    assert (saved["local_hour"], saved["local_minute"]) == (6, 30)


def test_asgi_chat_routes_and_limit_validation(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    list_status, _, listed = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/chats",
            query=b"limit=20&offset=1",
            token=token,
        )
    )
    create_status, _, created = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path="/api/v1/chats",
            token=token,
        )
    )
    load_status, _, loaded = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/chats/11111111-1111-1111-1111-111111111111",
            token=token,
        )
    )
    invalid_status, _, invalid = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/chats",
            query=b"limit=0",
            token=token,
        )
    )
    invalid_offset_status, _, invalid_offset = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/chats",
            query=b"limit=20&offset=-1",
            token=token,
        )
    )

    assert list_status == 200
    assert listed["items"][0]["message_count"] == 1
    assert create_status == 201
    assert created["chat_id"] == "11111111-1111-1111-1111-111111111111"
    assert load_status == 200
    assert loaded["messages"][0]["content"] == "hello"
    assert invalid_status == 400
    assert invalid["code"] == "invalid_request"
    assert invalid_offset_status == 400
    assert invalid_offset["code"] == "invalid_request"
    assert "offset" in invalid_offset["message"]


def test_asgi_model_routes(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    health_status, _, health = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/models/health",
            token=token,
        )
    )
    list_status, _, models = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/models",
            token=token,
        )
    )

    assert health_status == 200
    assert health["status"] == "ready"
    assert list_status == 200
    assert models["items"][0]["backend_model_id"] == "example/model"


def test_asgi_invalid_chat_id_is_safe_400(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    status, _, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/chats/not-a-uuid",
            token=token,
        )
    )

    assert status == 400
    assert payload["code"] == "invalid_request"
    assert "badly formed" in payload["message"]


def test_asgi_unknown_route_is_safe_404(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    status, _, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/does-not-exist",
            token=token,
        )
    )

    assert status == 404
    assert payload["code"] == "not_found"


def test_asgi_known_route_with_wrong_method_is_405(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    status, _, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path="/api/v1/health",
            token=token,
        )
    )

    assert status == 405
    assert payload["code"] == "method_not_allowed"


def test_asgi_shutdown_requires_dedicated_process_opt_in(tmp_path) -> None:
    app, runtime, token = _app(tmp_path)

    unavailable_status, _, unavailable = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path="/api/v1/system/shutdown",
            token=token,
        )
    )

    enabled = CoreApiAsgiApp(
        facade=_facade(),
        runtime=runtime,
        allow_shutdown=True,
    )
    accepted_status, _, accepted = asyncio.run(
        _request(
            enabled,
            runtime,
            method="POST",
            path="/api/v1/system/shutdown",
            token=token,
        )
    )

    assert unavailable_status == 409
    assert unavailable["code"] == "shutdown_unavailable"
    assert accepted_status == 202
    assert accepted == {"accepted": True}
