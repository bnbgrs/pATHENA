"""Proxy-free HTTP transport for loopback-only local model adapters."""

from __future__ import annotations

import ipaddress
import math
from numbers import Real
from typing import Any, cast
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_LOCAL_RESPONSE_BYTES = 32 * 1024 * 1024


class LocalResponseTooLargeError(OSError):
    """Raised when a non-streaming local provider response exceeds its byte cap."""


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


class _BoundedLocalResponse:
    """Delegate one local HTTP response while bounding whole-body reads."""

    def __init__(self, response: Any, *, max_bytes: int) -> None:
        self._response = response
        self._max_bytes = max_bytes

    def __enter__(self) -> _BoundedLocalResponse:
        enter = getattr(self._response, "__enter__", None)
        if enter is not None:
            enter()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> Any:
        exit_method = getattr(self._response, "__exit__", None)
        if exit_method is not None:
            return exit_method(exc_type, exc, traceback)
        close = getattr(self._response, "close", None)
        if close is not None:
            close()
        return None

    def __iter__(self) -> Any:
        return iter(self._response)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    def read(self, amt: int | None = None) -> bytes:
        if amt is not None and amt >= 0:
            return cast(bytes, self._response.read(amt))
        raw = cast(bytes, self._response.read(self._max_bytes + 1))
        if len(raw) > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model response exceeded the configured byte limit."
            )
        return raw


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


def _bound_http_error_body(exc: HTTPError) -> None:
    if exc.fp is not None:
        bounded_fp: Any = _BoundedLocalResponse(
            exc.fp,
            max_bytes=MAX_LOCAL_RESPONSE_BYTES,
        )
        error: Any = exc
        error.fp = bounded_fp
        error.file = bounded_fp


def open_local_request(request: Request, *, timeout: float) -> Any:
    """Open a loopback provider request without proxies or redirect traversal.

    Explicitly installing an empty ``ProxyHandler`` keeps local model traffic
    local even when HTTP_PROXY, HTTPS_PROXY, ALL_PROXY or platform proxy settings
    are present. Redirects are rejected so a loopback service cannot move a
    request onto an external URL. The URL itself is revalidated here so future
    adapters cannot accidentally use this transport for a non-loopback target.

    Whole-body ``read()`` calls are capped independently of Content-Length so a
    faulty or compromised loopback service cannot make callers buffer an
    arbitrarily large non-streaming response. Iteration remains unchanged for
    explicitly streaming protocols such as SSE.
    """
    if not isinstance(request, Request):
        raise TypeError("Local model transport requires urllib.request.Request.")
    _assert_loopback_http_request(request)
    validated_timeout = _validated_timeout(timeout)
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    try:
        response = opener.open(request, timeout=validated_timeout)
    except HTTPError as exc:
        _bound_http_error_body(exc)
        raise
    return _BoundedLocalResponse(
        response,
        max_bytes=MAX_LOCAL_RESPONSE_BYTES,
    )
