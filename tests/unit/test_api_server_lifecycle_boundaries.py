from __future__ import annotations

from email.message import Message
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

import athena.api.server as server_module
from athena.api.server import CoreApiServer, CoreApiServerError


@pytest.mark.parametrize("port", [True, False, 1234.5, "1234", -1, 65536])
def test_server_rejects_invalid_port_before_runtime_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    port: Any,
) -> None:
    def forbidden_runtime(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("runtime construction must not occur")

    monkeypatch.setattr(server_module, "LocalApiRuntime", forbidden_runtime)

    with pytest.raises(ValueError, match="integer between 0 and 65535"):
        CoreApiServer(
            facade=object(),  # type: ignore[arg-type]
            runtime_root=tmp_path,
            port=port,  # type: ignore[arg-type]
        )


class _Runtime:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def clear(self) -> None:
        self.events.append("runtime")


class _InterruptingServer:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def shutdown(self) -> None:
        self.events.append("shutdown")
        raise KeyboardInterrupt()

    def server_close(self) -> None:
        self.events.append("close")


class _Thread:
    def __init__(self, events: list[str]) -> None:
        self.events = events

    def join(self, *, timeout: float) -> None:
        assert timeout > 0
        self.events.append("join")

    def is_alive(self) -> bool:
        return False


def test_server_stop_attempts_all_cleanup_before_reraising_interrupt() -> None:
    events: list[str] = []
    server = CoreApiServer.__new__(CoreApiServer)
    server.runtime = _Runtime(events)  # type: ignore[assignment]
    server._server = _InterruptingServer(events)  # type: ignore[assignment]
    server._thread = _Thread(events)  # type: ignore[assignment]
    server._discovery = None

    with pytest.raises(KeyboardInterrupt):
        server.stop()

    assert events == ["runtime", "shutdown", "close", "join"]
    assert server._server is None
    assert server._thread is None


def _request_handler(headers: Message, body: bytes = b"") -> server_module._AthenaRequestHandler:
    handler = object.__new__(server_module._AthenaRequestHandler)
    handler.headers = headers
    handler.rfile = BytesIO(body)
    return handler


def test_request_body_rejects_duplicate_content_length() -> None:
    headers = Message()
    headers["Content-Length"] = "1"
    headers["Content-Length"] = "1"
    handler = _request_handler(headers, b"x")

    with pytest.raises(ValueError, match="Multiple Content-Length"):
        handler._read_request_body()


def test_request_body_rejects_noncanonical_content_length() -> None:
    headers = Message()
    headers["Content-Length"] = "+1"
    handler = _request_handler(headers, b"x")

    with pytest.raises(ValueError, match="canonical non-negative integer"):
        handler._read_request_body()


def test_request_body_reads_exact_canonical_length() -> None:
    headers = Message()
    headers["Content-Length"] = "3"
    handler = _request_handler(headers, b"abc")

    assert handler._read_request_body() == b"abc"


def test_server_stop_wraps_normal_cleanup_failure() -> None:
    events: list[str] = []

    class _FailingRuntime:
        def clear(self) -> None:
            events.append("runtime")
            raise RuntimeError("clear failed")

    server = CoreApiServer.__new__(CoreApiServer)
    server.runtime = _FailingRuntime()  # type: ignore[assignment]
    server._server = None
    server._thread = None
    server._discovery = None

    with pytest.raises(CoreApiServerError, match="did not stop cleanly"):
        server.stop()

    assert events == ["runtime"]
