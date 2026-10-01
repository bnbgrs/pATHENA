from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from athena.api import client as client_module
from athena.api.asgi import CoreApiAsgiApp
from athena.api.client import CoreApiClient, CoreApiClientError
from athena.api.runtime import LocalApiRuntime
from athena.api.search_contracts import (
    SearchProtectionResponse,
    SearchResultResponse,
)
from athena.retrieval.universal import UniversalSearchEntityType


class _SearchFacade:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                str,
                int,
                tuple[UniversalSearchEntityType, ...] | None,
            ]
        ] = []

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]:
        self.calls.append((query, limit, entity_types))
        return (
            SearchResultResponse(
                result_ref="knowledge:11111111-1111-1111-1111-111111111111",
                title="Alpha project",
                preview="Alpha search preview",
                entity_type="knowledge",
                revision_id="22222222-2222-2222-2222-222222222222",
                rank=1,
                retrieval_methods=("lexical",),
                source_anchor=None,
                protection=SearchProtectionResponse(
                    state="unprotected",
                    protection_scope_id=None,
                ),
            ),
        )


async def _request(
    app: CoreApiAsgiApp,
    runtime: LocalApiRuntime,
    *,
    method: str,
    path: str,
    query: bytes = b"",
    token: str,
) -> tuple[int, dict[str, Any]]:
    scope: dict[str, Any] = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query,
        "headers": [
            (
                b"authorization",
                f"Bearer {token}".encode("ascii"),
            ),
        ],
    }

    async def receive() -> dict[str, Any]:
        return {
            "type": "http.request",
            "body": b"",
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
    return (
        int(start["status"]),
        json.loads(response["body"].decode("utf-8")),
    )


def _search_app(
    tmp_path: Path,
) -> tuple[CoreApiAsgiApp, LocalApiRuntime, str, _SearchFacade]:
    runtime = LocalApiRuntime(tmp_path / "api")
    runtime.publish(port=32123)
    token = runtime.token_path.read_text(encoding="utf-8").strip()
    facade = _SearchFacade()
    app = CoreApiAsgiApp(
        facade=facade,  # type: ignore[arg-type]
        runtime=runtime,
    )
    return app, runtime, token, facade


def test_asgi_universal_search_projects_query_limit_and_filters(
    tmp_path: Path,
) -> None:
    app, runtime, token, facade = _search_app(tmp_path)

    status, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/search",
            query=(
                b"q=alpha+project&limit=7"
                b"&entity_type=knowledge%2Csource"
            ),
            token=token,
        )
    )

    assert status == 200
    assert facade.calls == [
        (
            "alpha project",
            7,
            (
                UniversalSearchEntityType.KNOWLEDGE,
                UniversalSearchEntityType.SOURCE,
            ),
        )
    ]
    assert payload["items"] == [
        {
            "result_ref": (
                "knowledge:"
                "11111111-1111-1111-1111-111111111111"
            ),
            "title": "Alpha project",
            "preview": "Alpha search preview",
            "entity_type": "knowledge",
            "revision_id": "22222222-2222-2222-2222-222222222222",
            "rank": 1,
            "retrieval_methods": ["lexical"],
            "source_anchor": None,
            "protection": {
                "state": "unprotected",
                "protection_scope_id": None,
            },
        }
    ]


@pytest.mark.parametrize(
    ("query", "message"),
    [
        (b"", "must occur exactly once"),
        (b"q=alpha&q=beta", "must occur exactly once"),
        (b"q=alpha&unknown=value", "unsupported query parameters"),
        (b"q=alpha&limit=0", "between 1 and 100"),
        (b"q=alpha&entity_type=source%2Csource", "must not contain duplicates"),
        (b"q=alpha&entity_type=not-a-type", "unknown type"),
    ],
)
def test_asgi_universal_search_rejects_invalid_query_contract(
    tmp_path: Path,
    query: bytes,
    message: str,
) -> None:
    app, runtime, token, facade = _search_app(tmp_path)

    status, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="GET",
            path="/api/v1/search",
            query=query,
            token=token,
        )
    )

    assert status == 400
    assert payload["code"] == "invalid_request"
    assert message in payload["message"]
    assert facade.calls == []


def test_asgi_universal_search_known_route_rejects_wrong_method(
    tmp_path: Path,
) -> None:
    app, runtime, token, facade = _search_app(tmp_path)

    status, payload = asyncio.run(
        _request(
            app,
            runtime,
            method="POST",
            path="/api/v1/search",
            token=token,
        )
    )

    assert status == 405
    assert payload["code"] == "method_not_allowed"
    assert facade.calls == []


class _Response:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.status = 200
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> bool:
        del args
        return False

    def read(self) -> bytes:
        return self._raw


def _bootstrap(runtime_root: Path) -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    token_path = runtime_root / "core-api.token"
    token_path.write_text("search-token\n", encoding="ascii")
    (runtime_root / "core-api.json").write_text(
        json.dumps(
            {
                "api_version": "v1",
                "host": "127.0.0.1",
                "port": 32123,
                "token_path": str(token_path),
                "process_id": 1234,
            }
        ),
        encoding="utf-8",
    )


def _search_payload(
    *,
    source_anchor: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "items": [
            {
                "result_ref": (
                    "source:"
                    "11111111-1111-1111-1111-111111111111"
                ),
                "title": "Alpha source",
                "preview": "Alpha project notes",
                "entity_type": "source",
                "revision_id": None,
                "rank": 1,
                "retrieval_methods": ["lexical"],
                "source_anchor": source_anchor,
                "protection": {
                    "state": "unprotected",
                    "protection_scope_id": None,
                },
            }
        ]
    }


def test_client_universal_search_encodes_filters_and_decodes_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    seen: list[tuple[str, str]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        seen.append((request.get_method(), request.full_url))
        return _Response(_search_payload())

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    result = CoreApiClient(runtime_root).universal_search(
        "alpha project",
        limit=7,
        entity_types=(
            UniversalSearchEntityType.SOURCE,
            UniversalSearchEntityType.JOB,
        ),
    )

    assert seen == [
        (
            "GET",
            (
                "http://127.0.0.1:32123/api/v1/search"
                "?q=alpha+project&limit=7"
                "&entity_type=source%2Cjob"
            ),
        )
    ]
    assert len(result) == 1
    assert result[0].entity_type == "source"
    assert result[0].revision_id is None
    assert result[0].retrieval_methods == ("lexical",)
    assert result[0].protection.state == "unprotected"


def test_client_universal_search_normalizes_invalid_anchor_response(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    monkeypatch.setattr(
        client_module,
        "urlopen",
        lambda request, timeout: _Response(
            _search_payload(
                source_anchor={
                    "representation_id": (
                        "33333333-3333-3333-3333-333333333333"
                    ),
                    "start_offset": 8,
                    "end_offset": 8,
                    "quoted_sha256": "0" * 64,
                }
            )
        ),
    )

    with pytest.raises(
        CoreApiClientError,
        match="invalid Search source anchor",
    ) as exc_info:
        CoreApiClient(runtime_root).universal_search("alpha")

    assert exc_info.value.code == "invalid_response"


@pytest.mark.parametrize(
    ("query", "limit", "entity_types", "message"),
    [
        ("", 20, None, "must not be empty"),
        ("alpha", 0, None, "between 1 and 100"),
        (
            "alpha",
            20,
            (),
            "must not be empty",
        ),
        (
            "alpha",
            20,
            (
                UniversalSearchEntityType.SOURCE,
                UniversalSearchEntityType.SOURCE,
            ),
            "must not contain duplicates",
        ),
    ],
)
def test_client_universal_search_rejects_invalid_request_before_transport(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    query: str,
    limit: int,
    entity_types: tuple[UniversalSearchEntityType, ...] | None,
    message: str,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    calls = 0

    def reject_urlopen(request: Any, timeout: float) -> _Response:
        nonlocal calls
        del request, timeout
        calls += 1
        raise AssertionError("invalid request reached transport")

    monkeypatch.setattr(client_module, "urlopen", reject_urlopen)

    with pytest.raises((TypeError, ValueError), match=message):
        CoreApiClient(runtime_root).universal_search(
            query,
            limit=limit,
            entity_types=entity_types,
        )

    assert calls == 0
