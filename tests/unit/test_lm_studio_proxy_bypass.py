from __future__ import annotations

import json
from unittest.mock import patch
from urllib.request import HTTPRedirectHandler, ProxyHandler

from athena.model.adapters.lm_studio import LMStudioProvider
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider


class _Response:
    def __init__(self, payload: object) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


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
