from __future__ import annotations

import pytest

from athena.observability.health import HealthService, HealthSnapshot, HealthStatus


@pytest.mark.parametrize("detail", ["", "   ", None, 123, True])
def test_health_failure_detail_must_be_nonempty_text(detail: object) -> None:
    service = HealthService()

    with pytest.raises(ValueError):
        service.mark_failed(detail)  # type: ignore[arg-type]


@pytest.mark.parametrize("detail", ["", "   ", None, 123, True])
def test_health_recovery_detail_must_be_nonempty_text(detail: object) -> None:
    service = HealthService()

    with pytest.raises(ValueError):
        service.mark_recovery_required(detail)  # type: ignore[arg-type]


def test_health_snapshot_rejects_untyped_status() -> None:
    with pytest.raises(ValueError):
        HealthSnapshot(status="ok")  # type: ignore[arg-type]


def test_health_service_preserves_valid_failure_detail() -> None:
    service = HealthService()
    service.mark_failed("database unavailable")

    assert service.snapshot() == HealthSnapshot(
        status=HealthStatus.FAILED,
        detail="database unavailable",
    )
