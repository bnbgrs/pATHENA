"""Proxy-free HTTP transport for loopback-only local model adapters."""

from __future__ import annotations

import ipaddress
import math
from numbers import Real
from typing import Any
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class _RejectRedirects(HTTPRedirectHandler):
    """Prevent a local-only provider request from escaping through a redirect."""

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        del req, fp, code, msg, headers, newurl
        return None


def _assert_loopback_http_request(request: Request) -> None:
    parsed = urlsplit(request.full_url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Local model transport requires an HTTP(S) request.")
    host = parsed.hostname
    if host is None:
        raise ValueError("Local model transport request is missing a host.")
    if host.casefold() == "localhost":
        return
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError(
            "Local model transport requires an explicit loopback host."
        ) from exc
    if not address.is_loopback:
        raise ValueError("Local model transport requires a loopback host.")


def _validated_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("Local model transport timeout must be a finite number > 0.")
    try:
        timeout = float(value)
    except OverflowError as exc:
        raise ValueError(
            "Local model transport timeout must be a finite number > 0."
        ) from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Local model transport timeout must be a finite number > 0.")
    return timeout


def open_local_request(request: Request, *, timeout: float) -> Any:
    """Open a loopback provider request without proxies or redirect traversal.

    Explicitly installing an empty ``ProxyHandler`` keeps local model traffic
    local even when HTTP_PROXY, HTTPS_PROXY, ALL_PROXY or platform proxy settings
    are present. Redirects are rejected so a loopback service cannot move a
    request onto an external URL. The URL itself is revalidated here so future
    adapters cannot accidentally use this transport for a non-loopback target.
    """
    if not isinstance(request, Request):
        raise TypeError("Local model transport requires urllib.request.Request.")
    _assert_loopback_http_request(request)
    validated_timeout = _validated_timeout(timeout)
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    return opener.open(request, timeout=validated_timeout)
