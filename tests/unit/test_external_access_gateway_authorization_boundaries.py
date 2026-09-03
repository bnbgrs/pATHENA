from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.external.gateway import ExternalAuthorizationError


def _authorization_count(app: AthenaApplication) -> int:
    row = app.database.connection.execute(
        "SELECT COUNT(*) AS count FROM external_access_authorizations"
    ).fetchone()
    assert row is not None
    return int(row["count"])


def _fail_actor_resolution() -> None:
    pytest.fail("invalid authorization input reached actor resolution")


@pytest.mark.parametrize("purpose", [None, 7, True, b"research"])
def test_authorize_explicit_rejects_non_text_purpose_before_actor_or_persistence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    purpose: object,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "purpose-boundary"))
    app.start()
    monkeypatch.setattr(app.external_access.chat, "ensure_local_user", _fail_actor_resolution)
    before = _authorization_count(app)
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_explicit(
            purpose=purpose,  # type: ignore[arg-type]
            allowed_hosts=("example.com",),
        )
    assert _authorization_count(app) == before
    app.stop()


@pytest.mark.parametrize(
    "allowed_hosts",
    [
        "example.com",
        b"example.com",
        123,
        ("example.com", 7),
        [None],
    ],
)
def test_authorize_explicit_rejects_invalid_host_container_before_actor_or_persistence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    allowed_hosts: object,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "hosts-boundary"))
    app.start()
    monkeypatch.setattr(app.external_access.chat, "ensure_local_user", _fail_actor_resolution)
    before = _authorization_count(app)
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_explicit(
            purpose="bounded authorization",
            allowed_hosts=allowed_hosts,  # type: ignore[arg-type]
        )
    assert _authorization_count(app) == before
    app.stop()


def test_authorize_explicit_preserves_valid_host_normalization(tmp_path: Path) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "valid-hosts"))
    app.start()
    authorization = app.external_access.authorize_explicit(
        purpose=" normalized purpose ",
        allowed_hosts=["EXAMPLE.com.", "example.com", "openai.com"],
    )
    assert authorization.purpose == "normalized purpose"
    assert authorization.allowed_hosts_json == '["example.com","openai.com"]'
    app.stop()

@pytest.mark.parametrize("privacy_route", [None, 7, True, b"tor", [], {}])
def test_authorize_explicit_rejects_non_text_privacy_route_before_actor_or_persistence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    privacy_route: object,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "route-boundary"))
    app.start()
    monkeypatch.setattr(app.external_access.chat, "ensure_local_user", _fail_actor_resolution)
    before = _authorization_count(app)
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_explicit(
            purpose="bounded authorization",
            allowed_hosts=("example.com",),
            privacy_route=privacy_route,  # type: ignore[arg-type]
        )
    assert _authorization_count(app) == before
    app.stop()


def _fail_authorization_lookup(*_args: object, **_kwargs: object) -> None:
    pytest.fail("invalid direct fallback host reached authorization lookup")


@pytest.mark.parametrize("host", [None, 7, True, b"example.com", []])
def test_authorize_direct_fallback_rejects_non_text_host_before_authorization_lookup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    host: object,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "fallback-host-boundary"))
    app.start()
    source = app.external_access.authorize_explicit(
        purpose="fallback source",
        allowed_hosts=("example.com",),
    )
    monkeypatch.setattr(app.external_access, "get_authorization", _fail_authorization_lookup)
    with pytest.raises(ExternalAuthorizationError):
        app.external_access.authorize_direct_fallback(
            source.authorization_id,
            host=host,  # type: ignore[arg-type]
        )
    app.stop()
