from __future__ import annotations

import uuid
from urllib.parse import parse_qsl, urlsplit

import pytest

from athena.common.time import utc_now_us
from athena.external.gateway import (
    ExternalAccessAuthorizationRecord,
    ExternalAccessGateway,
    ExternalDestinationError,
    ExternalDirectApprovalRequired,
    _provenance_url,
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


def _query(url: str) -> dict[str, str]:
    return dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))


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


def test_provenance_url_redacts_aws_signed_url_credentials_case_insensitively() -> None:
    source = (
        "https://example.com/object?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Credential=AKIA_TEST%2F20260825%2Feu-central-1%2Fs3%2Faws4_request"
        "&x-AmZ-SeCuRiTy-ToKeN=session-secret"
        "&X-AMZ-SIGNATURE=deadbeef"
        "&partNumber=1#local-fragment"
    )

    provenance = _provenance_url(source)
    query = _query(provenance)

    assert query["X-Amz-Credential"] == "[REDACTED]"
    assert query["x-AmZ-SeCuRiTy-ToKeN"] == "[REDACTED]"
    assert query["X-AMZ-SIGNATURE"] == "[REDACTED]"
    assert query["X-Amz-Algorithm"] == "AWS4-HMAC-SHA256"
    assert query["partNumber"] == "1"
    assert urlsplit(provenance).fragment == ""
    assert "AKIA_TEST" not in provenance
    assert "session-secret" not in provenance
    assert "deadbeef" not in provenance


def test_provenance_url_redacts_google_signed_url_credentials_case_insensitively() -> None:
    source = (
        "https://example.com/object?X-Goog-Algorithm=GOOG4-RSA-SHA256"
        "&x-GoOg-CrEdEnTiAl=user%40example.com%2F20260825%2Fauto%2Fstorage%2Fgoog4_request"
        "&X-GOOG-SIGNATURE=cafebabe"
        "&response-content-type=text%2Fplain"
    )

    provenance = _provenance_url(source)
    query = _query(provenance)

    assert query["x-GoOg-CrEdEnTiAl"] == "[REDACTED]"
    assert query["X-GOOG-SIGNATURE"] == "[REDACTED]"
    assert query["X-Goog-Algorithm"] == "GOOG4-RSA-SHA256"
    assert query["response-content-type"] == "text/plain"
    assert "user%40example.com" not in provenance
    assert "cafebabe" not in provenance


def test_direct_approval_error_uses_redacted_signed_url() -> None:
    error = ExternalDirectApprovalRequired(
        url=(
            "https://example.com/object?X-Goog-Credential=private-credential"
            "&X-Goog-Signature=private-signature&generation=7"
        ),
        reason_code="tor_transport_failed_direct_approval_required",
    )

    message = str(error)
    assert "private-credential" not in message
    assert "private-signature" not in message
    assert "generation=7" in message
    assert message.count("%5BREDACTED%5D") == 2
