"""Proxy-free HTTP transport for loopback-only local model adapters."""

from __future__ import annotations

import ipaddress
import math
from numbers import Real
from time import monotonic
from typing import Any, cast
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_LOCAL_RESPONSE_BYTES = 32 * 1024 * 1024
_BLOCKED_RESPONSE_READ_APIS = frozenset(
    {"peek", "read1", "readall", "readinto", "readinto1", "readlines"}
)
_BLOCKED_RESPONSE_BODY_ESCAPE_ATTRS = frozenset({"file", "fp", "raw"})


class LocalResponseTooLargeError(OSError):
    """Raised when a local provider response unit exceeds its byte cap."""


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
    """Delegate one local HTTP response with bounded buffering and streaming lifetime."""

    def __init__(
        self,
        response: Any,
        *,
        max_bytes: int,
        total_timeout_seconds: float | None = None,
    ) -> None:
        self._response = response
        self._max_bytes = max_bytes
        self._bytes_read = 0
        self._deadline = (
            monotonic() + total_timeout_seconds
            if total_timeout_seconds is not None
            else None
        )

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
        while True:
            self._assert_before_deadline()
            raw_line = self.readline()
            self._assert_before_deadline()
            if not raw_line:
                return
            yield raw_line

    def __getattr__(self, name: str) -> Any:
        if name in _BLOCKED_RESPONSE_READ_APIS:
            raise OSError(
                "Local model response only supports bounded read/readline access."
            )
        if name in _BLOCKED_RESPONSE_BODY_ESCAPE_ATTRS:
            raise OSError(
                "Local model response does not expose raw body handles outside bounded access."
            )
        return getattr(self._response, name)

    def _assert_before_deadline(self) -> None:
        if self._deadline is not None and monotonic() >= self._deadline:
            raise TimeoutError(
                "Local model streaming response exceeded the configured total timeout."
            )

    def _assert_within_byte_budget(self) -> None:
        if self._bytes_read > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model response exceeded the configured byte limit."
            )

    def readline(self) -> bytes:
        self._assert_before_deadline()
        self._assert_within_byte_budget()
        readline = getattr(self._response, "readline", None)
        if readline is None:
            raise OSError("Local model streaming response does not support bounded lines.")
        remaining = self._max_bytes - self._bytes_read
        raw = cast(bytes, readline(remaining + 1))
        self._bytes_read += len(raw)
        if self._bytes_read > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model streaming response exceeded the configured byte limit."
            )
        self._assert_before_deadline()
        return raw

    def read(self, amt: int | None = None) -> bytes:
        self._assert_before_deadline()
        self._assert_within_byte_budget()
        remaining = self._max_bytes - self._bytes_read
        request_size = (
            remaining + 1
            if amt is None or amt < 0
            else min(amt, remaining + 1)
        )
        raw = cast(bytes, self._response.read(request_size))
        self._bytes_read += len(raw)
        if self._bytes_read > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model response exceeded the configured byte limit."
            )
        self._assert_before_deadline()
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


def _bound_http_error_body(
    exc: HTTPError,
    *,
    total_timeout_seconds: float,
) -> None:
    if exc.fp is not None:
        bounded_fp: Any = _BoundedLocalResponse(
            exc.fp,
            max_bytes=MAX_LOCAL_RESPONSE_BYTES,
            total_timeout_seconds=total_timeout_seconds,
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
    arbitrarily large non-streaming response. Streaming iteration uses bounded
    ``readline()`` calls, a cumulative byte cap, and a monotonic total deadline
    in addition to the socket inactivity timeout, preventing giant SSE lines,
    many-small-event floods, and indefinitely active local streams from bypassing
    the configured transport and generation bounds. HTTP error bodies use the
    same byte and total-time bounds before provider-specific error parsing.
    Alternative raw response read APIs and body-handle escape attributes are
    rejected so callers cannot bypass the bounded read/readline paths accidentally.
    """
    if not isinstance(request, Request):
        raise TypeError("Local model transport requires urllib.request.Request.")
    _assert_loopback_http_request(request)
    validated_timeout = _validated_timeout(timeout)
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    try:
        response = opener.open(request, timeout=validated_timeout)
    except HTTPError as exc:
        _bound_http_error_body(
            exc,
            total_timeout_seconds=validated_timeout,
        )
        raise
    return _BoundedLocalResponse(
        response,
        max_bytes=MAX_LOCAL_RESPONSE_BYTES,
        total_timeout_seconds=validated_timeout,
    )
