from __future__ import annotations

import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar
from urllib.request import Request

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.adapters.local_http import (
    LocalRequestCancelledError,
    open_cancellable_local_request,
)
from athena.model.domain import ModelChatMessage


class _BlockingHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    request_seen: ClassVar[threading.Event] = threading.Event()
    headers_sent: ClassVar[threading.Event] = threading.Event()
    release_server: ClassVar[threading.Event] = threading.Event()
    request_count: ClassVar[int] = 0
    mode: ClassVar[str] = "headers"

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_POST(self) -> None:  # noqa: N802
        type(self).request_count += 1
        type(self).request_seen.set()

        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)

        if type(self).mode == "headers":
            type(self).release_server.wait(5.0)
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", "0")
                self.end_headers()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.flush()
        type(self).headers_sent.set()
        type(self).release_server.wait(5.0)
        try:
            self.wfile.write(
                b'data: {"choices":[{"delta":{"content":"late"},'
                b'"finish_reason":null}]}\n\n'
            )
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass


def _server(mode: str) -> tuple[ThreadingHTTPServer, threading.Thread]:
    _BlockingHandler.request_seen = threading.Event()
    _BlockingHandler.headers_sent = threading.Event()
    _BlockingHandler.release_server = threading.Event()
    _BlockingHandler.request_count = 0
    _BlockingHandler.mode = mode

    server = ThreadingHTTPServer(("127.0.0.1", 0), _BlockingHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _shutdown(
    server: ThreadingHTTPServer,
    thread: threading.Thread,
) -> None:
    _BlockingHandler.release_server.set()
    server.shutdown()
    server.server_close()
    thread.join(2.0)


def test_cancellable_local_request_interrupts_blocked_response_headers() -> None:
    server, server_thread = _server("headers")
    cancelled = threading.Event()
    observed: list[BaseException] = []
    request = Request(
        f"http://127.0.0.1:{server.server_port}/blocked",
        data=b"{}",
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    def run() -> None:
        try:
            with open_cancellable_local_request(
                request,
                timeout=30.0,
                cancel_requested=cancelled.is_set,
                poll_seconds=0.01,
            ) as response:
                response.read()
        except BaseException as exc:
            observed.append(exc)

    client = threading.Thread(target=run)
    client.start()
    try:
        assert _BlockingHandler.request_seen.wait(2.0)
        started = time.monotonic()
        cancelled.set()
        client.join(2.0)
        elapsed = time.monotonic() - started

        assert client.is_alive() is False
        assert elapsed < 2.0
        assert len(observed) == 1
        assert isinstance(observed[0], LocalRequestCancelledError)
        assert _BlockingHandler.request_count == 1
    finally:
        _shutdown(server, server_thread)


def test_lmstudio_cancellable_stream_interrupts_blocked_first_token() -> None:
    server, server_thread = _server("stream")
    cancelled = threading.Event()
    chunks: list[str] = []
    failures: list[BaseException] = []
    provider = LMStudioProvider(
        base_url=f"http://127.0.0.1:{server.server_port}",
        generation_timeout_seconds=30.0,
    )

    def run() -> None:
        try:
            chunks.extend(
                provider.stream_chat_cancellable(
                    model_id="local/test-model",
                    messages=(ModelChatMessage(role="user", content="hello"),),
                    cancel_requested=cancelled.is_set,
                )
            )
        except BaseException as exc:
            failures.append(exc)

    client = threading.Thread(target=run)
    client.start()
    try:
        assert _BlockingHandler.headers_sent.wait(2.0)
        started = time.monotonic()
        cancelled.set()
        client.join(2.0)
        elapsed = time.monotonic() - started

        assert client.is_alive() is False
        assert elapsed < 2.0
        assert failures == []
        assert chunks == []
        assert _BlockingHandler.request_count == 1
    finally:
        _shutdown(server, server_thread)
