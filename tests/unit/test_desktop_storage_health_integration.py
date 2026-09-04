from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QThreadPool
from PySide6.QtTest import QSignalSpy

from athena.api import client as client_module
from athena.api.client import CoreApiClientError
from athena.api.contracts import (
    HealthResponse,
    ProviderHealthResponse,
    StorageHealthResponse,
)
from athena.api.storage_client import StorageAwareCoreApiClient
from athena.desktop.api_controller import DesktopApiSnapshot
from athena.desktop.app import create_application
from athena.desktop.storage_api_controller import (
    StorageDesktopApiController,
    StorageDesktopApiSnapshot,
)
from athena.desktop.system_runtime_overview import project_system_runtime


class _Response:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.status = 200
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> _Response:
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


def _available_storage() -> StorageHealthResponse:
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


def test_storage_client_reads_authenticated_storage_health(
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
        return _Response(
            {
                "api_version": "v1",
                "status": "available",
                "database_open": True,
                "database_path": "/local/athena.sqlite3",
                "database_size_bytes": 2048,
                "wal_size_bytes": 512,
                "observed_at_us": 123456,
                "detail": None,
            }
        )

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    health = StorageAwareCoreApiClient(
        runtime_root,
        timeout_seconds=2.0,
    ).storage_health()

    assert health == _available_storage()
    assert seen == [
        (
            "GET",
            "http://127.0.0.1:32123/api/v1/storage/health",
            "Bearer storage-token",
        )
    ]


def test_storage_client_rejects_contradictory_available_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    monkeypatch.setattr(
        client_module,
        "urlopen",
        lambda request, timeout: _Response(
            {
                "api_version": "v1",
                "status": "available",
                "database_open": False,
                "database_path": "/local/athena.sqlite3",
                "database_size_bytes": 2048,
                "wal_size_bytes": 512,
                "observed_at_us": 123456,
                "detail": None,
            }
        ),
    )

    with pytest.raises(CoreApiClientError, match="open database") as exc_info:
        StorageAwareCoreApiClient(runtime_root).storage_health()

    assert exc_info.value.code == "invalid_response"


def test_storage_client_from_environment_preserves_concrete_type(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    local_root = (tmp_path / "athena-local").resolve()
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(local_root))
    monkeypatch.delenv("ATHENA_ARCHIVE_ROOT", raising=False)
    monkeypatch.delenv("ATHENA_BACKUP_ROOT", raising=False)
    monkeypatch.delenv("ATHENA_PROJECTION_ROOT", raising=False)

    client = StorageAwareCoreApiClient.from_environment(timeout_seconds=1.25)

    assert isinstance(client, StorageAwareCoreApiClient)
    assert client.runtime_root == local_root / "tmp" / "core-api"
    assert client.timeout_seconds == 1.25


class _StorageGateway:
    def __init__(self, *, storage_fail: bool = False) -> None:
        self.storage_fail = storage_fail
        self.thread_ids: list[int] = []

    def _record(self) -> None:
        self.thread_ids.append(threading.get_ident())

    def health(self) -> HealthResponse:
        self._record()
        return HealthResponse(api_version="v1", core_status="ok", detail=None)

    def provider_health(self) -> ProviderHealthResponse:
        self._record()
        return ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        )

    def list_models(self) -> tuple[()]:
        self._record()
        return ()

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[()]:
        self._record()
        del limit, offset
        return ()

    def storage_health(self) -> StorageHealthResponse:
        self._record()
        if self.storage_fail:
            raise CoreApiClientError("Storage probe unavailable.")
        return _available_storage()


def _pool() -> QThreadPool:
    pool = QThreadPool()
    pool.setMaxThreadCount(1)
    return pool


def test_storage_controller_collects_probe_off_ui_thread() -> None:
    app = create_application(["pathena-storage-controller-test"])
    gateway = _StorageGateway()
    pool = _pool()
    controller = StorageDesktopApiController(gateway, thread_pool=pool)
    spy = QSignalSpy(controller.snapshot_ready)
    main_thread = threading.get_ident()

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    snapshot = spy.at(0)[0]
    assert isinstance(snapshot, StorageDesktopApiSnapshot)
    assert snapshot.storage == _available_storage()
    assert snapshot.storage_error is None
    assert gateway.thread_ids
    assert all(thread_id != main_thread for thread_id in gateway.thread_ids)


def test_storage_probe_failure_does_not_break_core_snapshot() -> None:
    app = create_application(["pathena-storage-controller-failure-test"])
    gateway = _StorageGateway(storage_fail=True)
    pool = _pool()
    controller = StorageDesktopApiController(gateway, thread_pool=pool)
    ready_spy = QSignalSpy(controller.snapshot_ready)
    failed_spy = QSignalSpy(controller.connection_failed)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert ready_spy.count() == 1
    assert failed_spy.count() == 0
    snapshot = ready_spy.at(0)[0]
    assert isinstance(snapshot, StorageDesktopApiSnapshot)
    assert snapshot.health.core_status == "ok"
    assert snapshot.storage is None
    assert snapshot.storage_error == "Storage probe unavailable."


def test_system_runtime_renders_live_storage_sizes() -> None:
    snapshot = StorageDesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        ),
        models=(),
        chats=(),
        storage=_available_storage(),
    )

    overview = project_system_runtime(snapshot)

    assert overview.storage.value == "Available · DB 2.0 KiB · WAL 512 B"
    assert overview.storage.state == "success"
    assert overview.state == "success"
    assert "Storage: Available · DB 2.0 KiB · WAL 512 B" in overview.detail


def test_system_runtime_keeps_missing_optional_probe_nonfatal() -> None:
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        ),
        models=(),
        chats=(),
    )

    overview = project_system_runtime(snapshot)

    assert overview.storage.value == "Unavailable"
    assert overview.state == "success"
    assert "exposes no storage probe" in overview.detail
