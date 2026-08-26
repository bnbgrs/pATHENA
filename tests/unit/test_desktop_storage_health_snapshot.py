from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QThreadPool
from PySide6.QtTest import QSignalSpy

from athena.api import client as client_module
from athena.api.client import CoreApiClientError
from athena.api.contracts import HealthResponse, ProviderHealthResponse, StorageHealthResponse
from athena.api.storage_client import StorageAwareCoreApiClient
from athena.desktop.app import create_application
from athena.desktop.storage_api_controller import (
    StorageDesktopApiController,
    StorageDesktopApiSnapshot,
)


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
    token_path.write_text("storage-token\n", encoding="ascii")
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


def _storage() -> StorageHealthResponse:
    return StorageHealthResponse(
        api_version="v1",
        status="available",
        database_open=True,
        database_path="/local/athena.sqlite3",
        database_size_bytes=2048,
        wal_size_bytes=512,
        observed_at_us=123456,
        detail=None,
    )


def test_storage_client_reads_authenticated_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    seen: list[tuple[str, str, str | None]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        assert timeout == 2.0
        seen.append(
            (
                request.get_method(),
                request.full_url,
                request.get_header("Authorization"),
            )
        )
        return _Response(_storage().to_dict())

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)
    health = StorageAwareCoreApiClient(
        runtime_root,
        timeout_seconds=2.0,
    ).storage_health()

    assert health == _storage()
    assert seen == [
        (
            "GET",
            "http://127.0.0.1:32123/api/v1/storage/health",
            "Bearer storage-token",
        )
    ]


class _Gateway:
    def __init__(self, *, storage_fail: bool = False) -> None:
        self.storage_fail = storage_fail

    def health(self) -> HealthResponse:
        return HealthResponse(api_version="v1", core_status="ok", detail=None)

    def provider_health(self) -> ProviderHealthResponse:
        return ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        )

    def list_models(self) -> tuple[()]:
        return ()

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[()]:
        del limit, offset
        return ()

    def storage_health(self) -> StorageHealthResponse:
        if self.storage_fail:
            raise CoreApiClientError("Storage probe unavailable.")
        return _storage()


def _refresh(gateway: _Gateway) -> StorageDesktopApiSnapshot:
    app = create_application(["pathena-storage-health-test"])
    pool = QThreadPool()
    pool.setMaxThreadCount(1)
    controller = StorageDesktopApiController(gateway, thread_pool=pool)
    ready = QSignalSpy(controller.snapshot_ready)
    failed = QSignalSpy(controller.connection_failed)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert ready.count() == 1
    assert failed.count() == 0
    snapshot = ready.at(0)[0]
    assert isinstance(snapshot, StorageDesktopApiSnapshot)
    return snapshot


def test_storage_health_is_carried_in_desktop_snapshot() -> None:
    snapshot = _refresh(_Gateway())

    assert snapshot.health.core_status == "ok"
    assert snapshot.storage == _storage()
    assert snapshot.storage_error is None


def test_storage_probe_failure_does_not_break_desktop_snapshot() -> None:
    snapshot = _refresh(_Gateway(storage_fail=True))

    assert snapshot.health.core_status == "ok"
    assert snapshot.storage is None
    assert snapshot.storage_error == "Storage probe unavailable."
