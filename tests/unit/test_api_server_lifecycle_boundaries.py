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



def test_server_stop_retains_runtime_discovery_until_clear_succeeds() -> None:
    events: list[str] = []

    class _RetryRuntime:
        def __init__(self) -> None:
            self.attempts = 0

        def clear(self) -> None:
            self.attempts += 1
            events.append(f"runtime-{self.attempts}")
            if self.attempts == 1:
                raise RuntimeError("clear failed")

    server = CoreApiServer.__new__(CoreApiServer)
    runtime = _RetryRuntime()
    discovery = object()
    server.runtime = runtime  # type: ignore[assignment]
    server._server = None
    server._thread = None
    server._discovery = discovery  # type: ignore[assignment]

    with pytest.raises(CoreApiServerError, match="did not stop cleanly"):
        server.stop()

    assert server._discovery is discovery

    server.stop()

    assert events == ["runtime-1", "runtime-2"]
    assert server._discovery is None


def test_server_stop_retains_live_server_and_thread_for_retry() -> None:
    events: list[str] = []
    state = {"alive": True, "shutdown_attempts": 0}

    class _RetryServer:
        def shutdown(self) -> None:
            state["shutdown_attempts"] += 1
            events.append(f"shutdown-{state['shutdown_attempts']}")
            if state["shutdown_attempts"] == 1:
                raise RuntimeError("shutdown failed")
            state["alive"] = False

        def server_close(self) -> None:
            events.append("close")

    class _RetryThread:
        def join(self, *, timeout: float) -> None:
            assert timeout > 0
            events.append("join")

        def is_alive(self) -> bool:
            return state["alive"]

    server = CoreApiServer.__new__(CoreApiServer)
    owned_server = _RetryServer()
    owned_thread = _RetryThread()
    server.runtime = _Runtime(events)  # type: ignore[assignment]
    server._server = owned_server  # type: ignore[assignment]
    server._thread = owned_thread  # type: ignore[assignment]
    server._discovery = None

    with pytest.raises(CoreApiServerError, match="did not stop cleanly"):
        server.stop()

    assert server._server is owned_server
    assert server._thread is owned_thread

    server.stop()

    assert events == [
        "runtime",
        "shutdown-1",
        "close",
        "join",
        "runtime",
        "shutdown-2",
        "close",
        "join",
    ]
    assert server._server is None
    assert server._thread is None



def test_server_start_retains_live_resources_when_rollback_is_incomplete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    state = {"alive": True, "shutdown_attempts": 0}

    class _PublishingRuntime:
        def publish(self, *, port: int) -> None:
            assert port == 43123
            events.append("publish")
            raise RuntimeError("publish failed")

        def clear(self) -> None:
            events.append("runtime-clear")

    class _StartupServer:
        server_address = ("127.0.0.1", 43123)

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            events.append("server-create")

        def serve_forever(self, *, poll_interval: float) -> None:
            assert poll_interval > 0

        def shutdown(self) -> None:
            state["shutdown_attempts"] += 1
            events.append(f"shutdown-{state['shutdown_attempts']}")
            if state["shutdown_attempts"] == 1:
                raise RuntimeError("rollback shutdown failed")
            state["alive"] = False

        def server_close(self) -> None:
            events.append("close")

    class _StartupThread:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            events.append("thread-create")

        def start(self) -> None:
            events.append("thread-start")

        def join(self, *, timeout: float) -> None:
            assert timeout > 0
            events.append("join")

        def is_alive(self) -> bool:
            return state["alive"]

    monkeypatch.setattr(server_module, "_AthenaHttpServer", _StartupServer)
    monkeypatch.setattr(server_module.threading, "Thread", _StartupThread)

    server = CoreApiServer.__new__(CoreApiServer)
    runtime = _PublishingRuntime()
    server._host = "127.0.0.1"
    server._configured_port = 0
    server.runtime = runtime  # type: ignore[assignment]
    server._shutdown_callback = None
    server.app = object()  # type: ignore[assignment]
    server._server = None
    server._thread = None
    server._discovery = None

    with pytest.raises(RuntimeError, match="publish failed"):
        server.start()

    assert server._server is not None
    assert server._thread is not None
    assert state["alive"] is True

    server.stop()

    assert server._server is None
    assert server._thread is None
    assert state["alive"] is False
    assert events == [
        "server-create",
        "thread-create",
        "thread-start",
        "publish",
        "runtime-clear",
        "shutdown-1",
        "close",
        "join",
        "runtime-clear",
        "shutdown-2",
        "close",
        "join",
    ]



def test_server_start_rejects_incomplete_previous_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    constructed = False

    class _ForbiddenServer:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal constructed
            constructed = True
            raise AssertionError("server construction must not occur")

    monkeypatch.setattr(server_module, "_AthenaHttpServer", _ForbiddenServer)

    server = CoreApiServer.__new__(CoreApiServer)
    server._host = "127.0.0.1"
    server._configured_port = 0
    server._shutdown_callback = None
    server.app = object()  # type: ignore[assignment]
    server._server = None
    server._thread = None
    server._discovery = object()  # type: ignore[assignment]

    with pytest.raises(CoreApiServerError, match="stale lifecycle state"):
        server.start()

    assert constructed is False


def test_server_start_rejects_incomplete_failed_start_rollback() -> None:
    class _LiveThread:
        def is_alive(self) -> bool:
            return True

    server = CoreApiServer.__new__(CoreApiServer)
    server._server = object()  # type: ignore[assignment]
    server._thread = _LiveThread()  # type: ignore[assignment]
    server._discovery = None

    with pytest.raises(CoreApiServerError, match="cleanup completes"):
        server.start()
