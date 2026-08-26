from __future__ import annotations

from athena.api.contracts import HealthResponse, ProviderHealthResponse
from athena.desktop.api_controller import DesktopApiSnapshot
from athena.desktop.system_runtime_overview import (
    disconnected_system_runtime,
    project_system_runtime,
)


def _snapshot(
    *,
    provider: ProviderHealthResponse | None = None,
    model_freshness: str | None = None,
) -> DesktopApiSnapshot:
    return DesktopApiSnapshot(
        health=HealthResponse(api_version="v1", core_status="ok", detail=None),
        provider=provider,
        models=(),
        chats=(),
        model_freshness=model_freshness,
    )


def test_system_runtime_projects_only_snapshot_backed_security_facts() -> None:
    overview = project_system_runtime(
        _snapshot(
            provider=ProviderHealthResponse(
                provider="lm_studio",
                status="ready",
                detail=None,
            )
        )
    )

    assert overview.core.value == "Ok"
    assert overview.network.value == "Provider reachable"
    assert overview.local_processing.value == "Lm studio"
    assert overview.local_processing.state == "success"
    assert overview.storage.value == "Unavailable"
    assert overview.background.value == "Unavailable"
    assert overview.loopback.value == "Unavailable"
    assert overview.encrypted_at_rest.value == "Unavailable"
    assert overview.tor.value == "Unavailable"


def test_system_runtime_preserves_stale_provider_semantics() -> None:
    overview = project_system_runtime(
        _snapshot(
            provider=ProviderHealthResponse(
                provider="lm_studio",
                status="ready",
                detail=None,
            ),
            model_freshness="stale",
        )
    )

    assert overview.provider.state == "stale"
    assert overview.network.state == "stale"
    assert overview.local_processing.state == "stale"


def test_disconnected_system_runtime_does_not_retain_unprobed_facts() -> None:
    overview = disconnected_system_runtime("Core offline")

    assert overview.core.value == "Disconnected"
    assert overview.core.state == "error"
    assert overview.network.value == "Core unreachable"
    assert overview.storage.state == "unavailable"
    assert overview.background.state == "unavailable"
    assert overview.loopback.state == "unavailable"
    assert overview.local_processing.state == "unavailable"
    assert overview.encrypted_at_rest.state == "unavailable"
    assert overview.tor.state == "unavailable"
