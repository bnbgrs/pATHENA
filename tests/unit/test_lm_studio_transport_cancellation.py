from __future__ import annotations

import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import ClassVar

import pytest

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.domain import ModelChatMessage
from athena.model.ports import ProviderGenerationCancelledError

_REQUEST_ID = "11111111-2222-4333-8444-555555555555"


class _BlockingSseHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    headers_sent: ClassVar[threading.Event] = threading.Event()
    release: ClassVar[threading.Event] = threading.Event()

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.flush()
        type(self).headers_sent.set()
        type(self).release.wait(3.0)
        try:
            self.wfile.write(
                b'data: {"choices":[{"delta":{"content":"late"},'
                b'"finish_reason":null}]}\n\n'
                b"data: [DONE]\n\n"
            )
            self.wfile.flush()
        except OSError:
            pass


class _BlockingHeadersHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    request_received: ClassVar[threading.Event] = threading.Event()
    release: ClassVar[threading.Event] = threading.Event()

    def log_message(self, format: str, *args: object) -> None:
        del format, args

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        type(self).request_received.set()
        type(self).release.wait(3.0)
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
        except OSError:
            pass


def _serve(
    handler: type[BaseHTTPRequestHandler],
) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.daemon_threads = True
    thread = threading.Thread(
        target=server.serve_forever,
        name="lmstudio-cancel-test-server",
        daemon=True,
    )
    thread.start()
    return server, thread


def _provider(server: ThreadingHTTPServer) -> LMStudioProvider:
    host, port = server.server_address[:2]
    return LMStudioProvider(
        f"http://{host}:{port}",
        timeout_seconds=1.0,
        generation_timeout_seconds=5.0,
    )


def _consume(
    provider: LMStudioProvider,
    *,
    errors: list[BaseException],
) -> threading.Thread:
    def run() -> None:
        try:
            list(
                provider.stream_chat_cancellable(
                    request_id=_REQUEST_ID,
                    model_id="primary",
                    messages=(
                        ModelChatMessage(
                            role="user",
                            content="cancel the blocked transport",
                        ),
                    ),
                )
            )
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(
        target=run,
        name="lmstudio-cancel-test-client",
    )
    thread.start()
    return thread


def test_cancel_generation_interrupts_blocked_first_sse_read() -> None:
    _BlockingSseHandler.headers_sent.clear()
    _BlockingSseHandler.release.clear()
    server, server_thread = _serve(_BlockingSseHandler)
    provider = _provider(server)
    errors: list[BaseException] = []

    try:
        client_thread = _consume(provider, errors=errors)
        assert _BlockingSseHandler.headers_sent.wait(2.0)

        provider.cancel_generation(_REQUEST_ID)

        client_thread.join(2.0)
        assert client_thread.is_alive() is False
        assert len(errors) == 1
        assert isinstance(errors[0], ProviderGenerationCancelledError)
        assert provider._active_generation_transports == {}
    finally:
        _BlockingSseHandler.release.set()
        server.shutdown()
        server.server_close()
        server_thread.join(2.0)


def test_cancel_generation_interrupts_wait_for_response_headers() -> None:
    _BlockingHeadersHandler.request_received.clear()
    _BlockingHeadersHandler.release.clear()
    server, server_thread = _serve(_BlockingHeadersHandler)
    provider = _provider(server)
    errors: list[BaseException] = []

    try:
        client_thread = _consume(provider, errors=errors)
        assert _BlockingHeadersHandler.request_received.wait(2.0)

        provider.cancel_generation(_REQUEST_ID)

        client_thread.join(2.0)
        assert client_thread.is_alive() is False
        assert len(errors) == 1
        assert isinstance(errors[0], ProviderGenerationCancelledError)
        assert provider._active_generation_transports == {}
    finally:
        _BlockingHeadersHandler.release.set()
        server.shutdown()
        server.server_close()
        server_thread.join(2.0)


def test_cancel_generation_rejects_noncanonical_request_identity() -> None:
    provider = LMStudioProvider("http://127.0.0.1:1234")

    with pytest.raises(ValueError, match="canonical UUID"):
        provider.cancel_generation("not-a-uuid")

    with pytest.raises(ValueError, match="canonical UUID text"):
        provider.cancel_generation(str(uuid.UUID(_REQUEST_ID)).upper())
