"""Focused transport regressions for the local Core API ASGI surface."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import Mock

from athena.api.asgi import CoreApiAsgiApp
from athena.api.contracts import API_VERSION, StorageHealthResponse


def test_storage_health_route_returns_current_read_only_contract() -> None:
    facade = Mock()
    facade.storage_health.return_value = StorageHealthResponse(
        api_version=API_VERSION,
        status="available",
        database_open=True,
        database_path="C:/pATHENA/athena.db",
        database_size_bytes=4096,
        wal_size_bytes=512,
        observed_at_us=123456,
        detail=None,
    )
    runtime = Mock()
    runtime.authenticate.return_value = True
    app = CoreApiAsgiApp(facade=facade, runtime=runtime)
    sent: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    asyncio.run(
        app(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/storage/health",
                "headers": [(b"authorization", b"Bearer test-token")],
            },
            receive,
            send,
        )
    )

    facade.storage_health.assert_called_once_with()
    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 200
    body = json.loads(sent[1]["body"])
    assert body == {
        "api_version": API_VERSION,
        "status": "available",
        "database_open": True,
        "database_path": "C:/pATHENA/athena.db",
        "database_size_bytes": 4096,
        "wal_size_bytes": 512,
        "observed_at_us": 123456,
        "detail": None,
    }


def test_storage_health_route_requires_authentication() -> None:
    facade = Mock()
    runtime = Mock()
    runtime.authenticate.return_value = False
    app = CoreApiAsgiApp(facade=facade, runtime=runtime)
    sent: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    asyncio.run(
        app(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/v1/storage/health",
                "headers": [],
            },
            receive,
            send,
        )
    )

    facade.storage_health.assert_not_called()
    assert sent[0]["status"] == 401
