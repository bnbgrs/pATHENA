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
        self._stream_bytes_read = 0
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
        if self._is_event_stream():
            yield from self._iter_sse_events()
            return

        while True:
            self._assert_before_deadline()
            raw_line = self.readline()
            self._assert_before_deadline()
            if not raw_line:
                return
            yield raw_line

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    def _assert_before_deadline(self) -> None:
        if self._deadline is not None and monotonic() >= self._deadline:
            raise TimeoutError(
                "Local model streaming response exceeded the configured total timeout."
            )

    def _is_event_stream(self) -> bool:
        try:
            headers = self._response.headers
        except AttributeError:
            return False

        try:
            content_type = headers.get_content_type()
        except (AttributeError, TypeError, ValueError):
            try:
                raw_content_type = headers.get("Content-Type", "")
            except (AttributeError, TypeError, ValueError):
                return False
            if not isinstance(raw_content_type, str):
                return False
            content_type = raw_content_type.partition(";")[0].strip()

        return str(content_type).casefold() == "text/event-stream"

    def _iter_sse_events(self) -> Any:
        """Yield one normalized ``data:`` line per complete SSE event.

        SSE events are framed by blank lines, not by TCP/HTTP line boundaries.
        Multiple data fields therefore form one event and are joined with a
        newline as required by the event-stream format. Comments and unrelated
        fields are ignored. A final buffered event is flushed at EOF because
        local model servers commonly terminate immediately after ``[DONE]``.
        """
        data_fields: list[bytes] = []
        first_line = True

        while True:
            self._assert_before_deadline()
            raw_line = self.readline()
            self._assert_before_deadline()
            if not raw_line:
                if data_fields:
                    yield b"data:" + b"\n".join(data_fields) + b"\n"
                return

            line = raw_line.rstrip(b"\r\n")
            if first_line:
                first_line = False
                if line.startswith(b"\xef\xbb\xbf"):
                    line = line[3:]

            if not line:
                if data_fields:
                    yield b"data:" + b"\n".join(data_fields) + b"\n"
                    data_fields.clear()
                continue

            if line.startswith(b":"):
                continue

            if b":" in line:
                field, value = line.split(b":", 1)
                if value.startswith(b" "):
                    value = value[1:]
            else:
                field, value = line, b""

            if field == b"data":
                data_fields.append(value)

    def readline(self) -> bytes:
        readline = getattr(self._response, "readline", None)
        if readline is None:
            raise OSError("Local model streaming response does not support bounded lines.")
        raw = cast(bytes, readline(self._max_bytes + 1))
        if len(raw) > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model streaming response line exceeded the configured byte limit."
            )
        if self._stream_bytes_read + len(raw) > self._max_bytes:
            raise LocalResponseTooLargeError(
                "Local model streaming response exceeded the configured byte limit."
            )
        self._stream_bytes_read += len(raw)
        return raw

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
    arbitrarily large non-streaming response. Streaming iteration uses bounded
    ``readline()`` calls, a cumulative byte cap, and a monotonic total deadline
    in addition to the socket inactivity timeout, preventing giant SSE lines,
    many-small-event floods, and indefinitely active local streams from bypassing
    the configured transport and generation bounds. Event-stream responses are
    normalized to complete SSE data events before adapters consume them.
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
        total_timeout_seconds=validated_timeout,
    )
