from __future__ import annotations

import pytest

from athena.model.domain import ProviderHealth, ProviderHealthStatus


def test_provider_health_status_exposes_complete_normative_state_set() -> None:
    assert {status.value for status in ProviderHealthStatus} == {
        "unavailable",
        "starting",
        "ready",
        "busy",
        "degraded",
        "error",
    }


@pytest.mark.parametrize(
    "status",
    [
        ProviderHealthStatus.UNAVAILABLE,
        ProviderHealthStatus.STARTING,
        ProviderHealthStatus.READY,
        ProviderHealthStatus.BUSY,
        ProviderHealthStatus.DEGRADED,
        ProviderHealthStatus.ERROR,
    ],
)
def test_provider_health_accepts_every_normative_state(
    status: ProviderHealthStatus,
) -> None:
    health = ProviderHealth(status=status, detail="observable state")

    assert health.status is status
    assert health.detail == "observable state"
