from __future__ import annotations

import uuid

import pytest

from athena.common.time import utc_now_us
from athena.external.gateway import (
    ExternalAccessAuthorizationRecord,
    ExternalAccessGateway,
    ExternalDestinationError,
)


class _LocalChat:
    def __init__(self, actor_id: uuid.UUID) -> None:
        self.actor_id = actor_id

    def ensure_local_user(self) -> uuid.UUID:
        return self.actor_id


class _PolicyGateway(ExternalAccessGateway):
    def __init__(self, authorization: ExternalAccessAuthorizationRecord) -> None:
        self._authorization = authorization
        self.chat = _LocalChat(authorization.actor_id)  # type: ignore[assignment]

    def get_authorization(
        self,
        authorization_id: uuid.UUID,
    ) -> ExternalAccessAuthorizationRecord:
        assert authorization_id == self._authorization.authorization_id
        return self._authorization


def _authorization(*, host: str = "example.com") -> ExternalAccessAuthorizationRecord:
    now_us = utc_now_us()
    return ExternalAccessAuthorizationRecord(
        authorization_id=uuid.uuid4(),
        actor_id=uuid.uuid4(),
        purpose="test external policy",
        allowed_hosts_json=f'["{host}"]',
        privacy_route="direct_explicit",
        origin="explicit_user",
        expires_at_us=now_us + 60_000_000,
        revoked_at_us=None,
        created_at_us=now_us,
    )


def test_require_authorized_rejects_plaintext_http() -> None:
    authorization = _authorization()
    gateway = _PolicyGateway(authorization)

    with pytest.raises(ExternalDestinationError, match="Only HTTPS external URLs"):
        gateway._require_authorized(
            authorization.authorization_id,
            url="http://example.com/source?q=secret",
        )


def test_require_authorized_accepts_https_default_port() -> None:
    authorization = _authorization()
    gateway = _PolicyGateway(authorization)

    assert (
        gateway._require_authorized(
            authorization.authorization_id,
            url="https://example.com/source",
        )
        == authorization
    )


def test_require_authorized_rejects_https_to_http_redirect_target() -> None:
    authorization = _authorization()
    gateway = _PolicyGateway(authorization)

    # capture_url re-runs _require_authorized for every redirect target before fetch.
    with pytest.raises(ExternalDestinationError, match="Only HTTPS external URLs"):
        gateway._require_authorized(
            authorization.authorization_id,
            url="http://example.com/redirected",
        )
