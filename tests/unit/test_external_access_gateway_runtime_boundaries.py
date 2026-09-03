from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import ExternalAuthorizationError, ExternalResponse


class _CountingTransport:
    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, url: str, *, max_bytes: int, timeout_seconds: float) -> ExternalResponse:
        del max_bytes, timeout_seconds
        self.calls += 1
        return ExternalResponse(
            final_url=url,
            status=200,
            headers={"content-type": "text/html; charset=utf-8"},
            body=b"<html><body>captured external evidence</body></html>",
        )


def _row_count(app: AthenaApplication, table: str) -> int:
    row = app.database.connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
    assert row is not None
    return int(row["count"])


def test_external_authorization_rejects_boolean_ttl_before_persistence(tmp_path: Path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "ttl-runtime"))
    app.start()
    before = _row_count(app, "external_access_authorizations")
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_explicit(
            purpose="invalid ttl",
            allowed_hosts=("example.com",),
            ttl_seconds=True,
        )
    assert _row_count(app, "external_access_authorizations") == before
    app.stop()


def test_direct_fallback_rejects_boolean_ttl_without_new_grant(tmp_path: Path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "fallback-ttl"))
    app.start()
    authorization = app.external_access.authorize_explicit(
        purpose="fallback ttl",
        allowed_hosts=("example.com",),
    )
    before = _row_count(app, "external_access_authorizations")
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_direct_fallback(
            authorization.authorization_id,
            host="example.com",
            ttl_seconds=True,
        )
    assert _row_count(app, "external_access_authorizations") == before
    app.stop()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_bytes": True},
        {"timeout_seconds": True},
        {"timeout_seconds": float("nan")},
        {"timeout_seconds": float("inf")},
    ],
)
def test_external_capture_rejects_invalid_resource_boundaries_before_side_effects(
    tmp_path: Path,
    kwargs: dict[str, object],
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "resource-boundary"))
    app.start()
    transport = _CountingTransport()
    app.external_access.transports["direct_explicit"] = transport
    authorization = app.external_access.authorize_explicit(
        purpose="resource boundary",
        allowed_hosts=("example.com",),
        privacy_route="direct_explicit",
    )
    audit_before = _row_count(app, "external_access_events")
    sources_before = len(app.sources.list())
    with pytest.raises(ValueError):
        app.external_access.capture_url(
            authorization.authorization_id,
            "https://example.com/report",
            **kwargs,
        )
    assert transport.calls == 0
    assert _row_count(app, "external_access_events") == audit_before
    assert len(app.sources.list()) == sources_before
    app.stop()
