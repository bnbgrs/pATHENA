from __future__ import annotations

import json
from unittest.mock import patch
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request

import pytest

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.model.adapters.local_http import open_local_request


class _Response:
    def __init__(self, payload: object) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self, amount: int = -1) -> bytes:
        if amount < 0:
            return self._payload
        return self._payload[:amount]


class _Opener:
    def __init__(self, response: _Response) -> None:
        self.response = response
        self.requests: list[object] = []
        self.timeouts: list[float] = []

    def open(self, request: object, *, timeout: float) -> _Response:
        self.requests.append(request)
        self.timeouts.append(timeout)
        return self.response


def test_embedding_transport_ignores_ambient_proxy_settings_and_redirects(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("ALL_PROXY", "socks5://127.0.0.1:9")

    opener = _Opener(
        _Response(
            {
                "data": [
                    {
                        "index": 0,
                        "embedding": [1.0, 0.0],
                    }
                ]
            }
        )
    )
    captured_handlers: list[object] = []

    def fake_build_opener(*handlers: object) -> _Opener:
        captured_handlers.extend(handlers)
        return opener

    provider = LMStudioEmbeddingProvider(
        LMStudioProvider("http://127.0.0.1:1234")
    )

    with patch(
        "athena.model.adapters.local_http.build_opener",
        side_effect=fake_build_opener,
    ):
        vectors = provider.embed(model_id="embedding-model", texts=("hello",))

    assert vectors == ((1.0, 0.0),)
    assert len(opener.requests) == 1
    assert opener.timeouts == [300.0]

    proxy_handlers = [
        handler
        for handler in captured_handlers
        if isinstance(handler, ProxyHandler)
    ]
    assert len(proxy_handlers) == 1
    assert proxy_handlers[0].proxies == {}

    redirect_handlers = [
        handler
        for handler in captured_handlers
        if isinstance(handler, HTTPRedirectHandler)
    ]
    assert len(redirect_handlers) == 1
    assert type(redirect_handlers[0]).__name__ == "_RejectRedirects"


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/v1/models",
        "https://192.0.2.10/v1/models",
        "file:///tmp/models",
    ],
)
def test_local_transport_rejects_non_loopback_targets_before_open(url: str) -> None:
    with patch("athena.model.adapters.local_http.build_opener") as build_opener:
        with pytest.raises(ValueError, match="Local model transport"):
            open_local_request(Request(url), timeout=1.0)

    build_opener.assert_not_called()


@pytest.mark.parametrize("url", ["http://localhost:1234/", "http://127.0.0.1:1234/", "http://[::1]:1234/"])
def test_local_transport_accepts_loopback_hosts(url: str) -> None:
    opener = _Opener(_Response({"ok": True}))
    with patch(
        "athena.model.adapters.local_http.build_opener",
        return_value=opener,
    ):
        with open_local_request(Request(url), timeout=1.25) as response:
            assert response.read()

    assert opener.timeouts == [1.25]
