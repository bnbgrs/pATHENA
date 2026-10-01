from __future__ import annotations

from pathlib import Path

import pytest

from athena.common.ids import uuid_to_blob
from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import (
    ExternalAccessError,
    ExternalAuthorizationError,
    ExternalResearchService,
    ExternalResponse,
    ExternalTransportError,
)


def _started_app(tmp_path: Path, name: str) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / name))
    app.start(run_startup_maintenance=False)
    return app


def test_external_research_preflights_all_urls_before_first_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _started_app(tmp_path, "research-preflight")
    try:
        authorization = app.external_access.authorize_explicit(
            purpose="external research",
            allowed_hosts=("example.com",),
        )
        service = ExternalResearchService(
            gateway=app.external_access,
            research=app.research,
        )
        capture_calls: list[str] = []

        def fail_capture(*_args: object, **_kwargs: object) -> object:
            capture_calls.append("called")
            pytest.fail("capture started before the complete URL set passed preflight")

        monkeypatch.setattr(app.external_access, "capture_url", fail_capture)

        with pytest.raises(ExternalAuthorizationError, match="outside authorization scope"):
            service.enqueue(
                query="compare sources",
                authorization_id=authorization.authorization_id,
                urls=(
                    "https://example.com/first",
                    "https://not-authorized.example/second",
                ),
            )
        assert capture_calls == []
    finally:
        app.stop()


@pytest.mark.parametrize(
    "urls",
    [
        "https://example.com/report",
        b"https://example.com/report",
        ("https://example.com/report", 7),
        (None,),
    ],
)
def test_external_research_rejects_invalid_url_containers_before_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    urls: object,
) -> None:
    app = _started_app(tmp_path, "research-url-boundary")
    try:
        authorization = app.external_access.authorize_explicit(
            purpose="external research",
            allowed_hosts=("example.com",),
        )
        service = ExternalResearchService(
            gateway=app.external_access,
            research=app.research,
        )

        def fail_capture(*_args: object, **_kwargs: object) -> object:
            pytest.fail("invalid External Research URL input reached capture")

        monkeypatch.setattr(app.external_access, "capture_url", fail_capture)

        with pytest.raises(ExternalAccessError, match="URL"):
            service.enqueue(
                query="compare sources",
                authorization_id=authorization.authorization_id,
                urls=urls,  # type: ignore[arg-type]
            )
    finally:
        app.stop()


class _RedirectLoopTransport:
    def __init__(self) -> None:
        self.calls = 0

    def fetch(
        self,
        url: str,
        *,
        max_bytes: int,
        timeout_seconds: float,
    ) -> ExternalResponse:
        del max_bytes, timeout_seconds
        self.calls += 1
        return ExternalResponse(
            final_url=url,
            status=302,
            headers={"location": "https://example.com/loop"},
            body=b"",
        )


class _HiddenFinalUrlTransport:
    def fetch(
        self,
        url: str,
        *,
        max_bytes: int,
        timeout_seconds: float,
    ) -> ExternalResponse:
        del url, max_bytes, timeout_seconds
        return ExternalResponse(
            final_url="https://outside.example/final",
            status=200,
            headers={"content-type": "text/plain"},
            body=b"should never be captured",
        )


def test_redirect_limit_failure_is_audited(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path, "redirect-limit")
    try:
        transport = _RedirectLoopTransport()
        app.external_access.transports["direct_explicit"] = transport
        authorization = app.external_access.authorize_explicit(
            purpose="redirect audit",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )

        with pytest.raises(ExternalTransportError, match="redirect limit"):
            app.external_access.capture_url(
                authorization.authorization_id,
                "https://example.com/start",
            )

        row = app.database.connection.execute(
            """
            SELECT outcome, reason_code
            FROM external_access_events
            WHERE authorization_id = ?
            ORDER BY created_at_us DESC
            LIMIT 1
            """,
            (uuid_to_blob(authorization.authorization_id),),
        ).fetchone()
        assert row is not None
        assert row["outcome"] == "failed"
        assert row["reason_code"] == "redirect_limit_exceeded"
        assert transport.calls == 6
    finally:
        app.stop()


def test_transport_final_url_scope_violation_is_denied_and_audited(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path, "hidden-final-url")
    try:
        app.external_access.transports["direct_explicit"] = _HiddenFinalUrlTransport()
        authorization = app.external_access.authorize_explicit(
            purpose="redirect audit",
            allowed_hosts=("example.com",),
            privacy_route="direct_explicit",
        )

        with pytest.raises(ExternalAuthorizationError, match="outside authorization scope"):
            app.external_access.capture_url(
                authorization.authorization_id,
                "https://example.com/start",
            )

        row = app.database.connection.execute(
            """
            SELECT destination_host, outcome, reason_code
            FROM external_access_events
            WHERE authorization_id = ?
            ORDER BY created_at_us DESC
            LIMIT 1
            """,
            (uuid_to_blob(authorization.authorization_id),),
        ).fetchone()
        assert row is not None
        assert row["destination_host"] == "outside.example"
        assert row["outcome"] == "denied"
        assert row["reason_code"] == "ExternalAuthorizationError"
    finally:
        app.stop()
