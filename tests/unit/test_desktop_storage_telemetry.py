from __future__ import annotations

from pathlib import Path

import pytest

from athena.api.client import CoreApiClient, CoreApiClientError
from athena.api.contracts import (
    HealthResponse,
    ProviderHealthResponse,
    StorageHealthResponse,
)
from athena.desktop.api_controller import DesktopApiSnapshot, _collect_snapshot
from athena.desktop.system_runtime_overview import project_system_runtime


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


def _payload() -> dict[str, object]:
    return {
        "api_version": "v1",
        "status": "available",
        "database_open": True,
        "database_path": "/local/athena.sqlite3",
        "database_size_bytes": 2048,
        "wal_size_bytes": 512,
        "observed_at_us": 123456,
        "detail": None,
    }


def test_core_api_client_reads_validated_storage_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = CoreApiClient(tmp_path)
    seen: list[str] = []

    def fake_get(path: str, **_kwargs: object) -> dict[str, object]:
        seen.append(path)
        return _payload()

    monkeypatch.setattr(client, "_get", fake_get)

    assert client.storage_health() == _storage()
    assert seen == ["/api/v1/storage/health"]


def test_core_api_client_rejects_contradictory_storage_health(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = CoreApiClient(tmp_path)
    payload = _payload()
    payload["database_open"] = False
    monkeypatch.setattr(client, "_get", lambda *_args, **_kwargs: payload)

    with pytest.raises(CoreApiClientError, match="open database") as exc_info:
        client.storage_health()

    assert exc_info.value.code == "invalid_response"


class _Gateway:
    def __init__(self, *, storage_error: bool = False) -> None:
        self.storage_error = storage_error

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
        if self.storage_error:
            raise CoreApiClientError("Storage probe unavailable.")
        return _storage()


def test_snapshot_collects_storage_without_coupling_other_status() -> None:
    snapshot = _collect_snapshot(_Gateway(), chat_limit=50)

    assert snapshot.health.core_status == "ok"
    assert snapshot.storage == _storage()
    assert snapshot.storage_error is None


def test_storage_probe_failure_is_isolated_from_core_snapshot() -> None:
    snapshot = _collect_snapshot(_Gateway(storage_error=True), chat_limit=50)

    assert snapshot.health.core_status == "ok"
    assert snapshot.storage is None
    assert snapshot.storage_error == "Storage probe unavailable."


def test_system_runtime_renders_live_storage_sizes() -> None:
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        ),
        models=(),
        chats=(),
        storage=_storage(),
    )

    overview = project_system_runtime(snapshot)

    assert overview.storage.value == "Available · DB 2.0 KiB · WAL 512 B"
    assert overview.storage.state == "success"
    assert overview.state == "success"
    assert "Storage: Available · DB 2.0 KiB · WAL 512 B" in overview.detail


def test_missing_optional_storage_probe_does_not_degrade_core_state() -> None:
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=ProviderHealthResponse(
            provider="lm_studio",
            status="ready",
            detail=None,
        ),
        models=(),
        chats=(),
        storage=None,
        storage_error="Storage probe unavailable.",
    )

    overview = project_system_runtime(snapshot)

    assert overview.storage.value == "Unavailable"
    assert overview.storage.state == "unavailable"
    assert overview.state == "success"
    assert "Storage telemetry: Storage probe unavailable." in overview.detail
