from __future__ import annotations

from io import BytesIO
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from athena.model.adapters import local_http
from athena.model.adapters.lm_studio import (
    LMStudioProvider,
    ProviderUnavailableError,
)
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.model.domain import ModelChatMessage


class _FakeResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        lines: tuple[bytes, ...] = (),
        content_length: str | None = None,
    ) -> None:
        self._stream = BytesIO(payload)
        self._lines = lines
        self.read_sizes: list[int] = []
        self.closed = False
        self.headers = (
            {} if content_length is None else {"Content-Length": content_length}
        )

    def read(self, amount: int = -1) -> bytes:
        self.read_sizes.append(amount)
        return self._stream.read(amount)

    def __iter__(self) -> Any:
        return iter(self._lines)

    def close(self) -> None:
        self.closed = True


class _FakeOpener:
    def __init__(self, result: Any) -> None:
        self._result = result

    def open(self, request: Request, *, timeout: float) -> Any:
        del request, timeout
        if isinstance(self._result, BaseException):
            raise self._result
        return self._result


def _install_response(
    monkeypatch: pytest.MonkeyPatch,
    response: Any,
    *,
    max_bytes: int = 8,
) -> None:
    monkeypatch.setattr(local_http, "MAX_LOCAL_RESPONSE_BYTES", max_bytes)
    monkeypatch.setattr(
        local_http,
        "build_opener",
        lambda *handlers: _FakeOpener(response),
    )


def test_whole_body_read_accepts_exact_limit_and_reads_only_max_plus_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _FakeResponse(b"12345678")
    _install_response(monkeypatch, raw)

    with local_http.open_local_request(
        Request("http://127.0.0.1:1234/api/v1/models"),
        timeout=1.0,
    ) as response:
        assert response.read() == b"12345678"

    assert raw.read_sizes == [9]
    assert raw.closed is True


def test_whole_body_read_rejects_max_plus_one_without_leaking_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _FakeResponse(b"SECRET123")
    _install_response(monkeypatch, raw)

    with local_http.open_local_request(
        Request("http://localhost:1234/api/v1/models"),
        timeout=1.0,
    ) as response:
        with pytest.raises(local_http.LocalResponseTooLargeError) as raised:
            response.read()

    assert "SECRET" not in str(raised.value)
    assert raw.read_sizes == [9]


def test_misleading_small_content_length_cannot_bypass_real_byte_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _FakeResponse(b"123456789", content_length="1")
    _install_response(monkeypatch, raw)

    with local_http.open_local_request(
        Request("http://127.0.0.1:1234/api/v1/models"),
        timeout=1.0,
    ) as response:
        with pytest.raises(local_http.LocalResponseTooLargeError):
            response.read()

    assert raw.read_sizes == [9]


def test_stream_iteration_is_not_converted_into_a_whole_body_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _FakeResponse(b"", lines=(b"data: one\n", b"data: [DONE]\n"))
    _install_response(monkeypatch, raw)

    with local_http.open_local_request(
        Request("http://127.0.0.1:1234/v1/chat/completions"),
        timeout=1.0,
    ) as response:
        assert list(response) == [b"data: one\n", b"data: [DONE]\n"]

    assert raw.read_sizes == []


def test_http_error_body_is_bounded_before_provider_error_parsing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    error = HTTPError(
        "http://127.0.0.1:1234/v1/chat/completions",
        400,
        "bad request",
        {},
        BytesIO(b"SECRET123"),
    )
    _install_response(monkeypatch, error)

    with pytest.raises(HTTPError) as raised:
        local_http.open_local_request(
            Request("http://127.0.0.1:1234/v1/chat/completions"),
            timeout=1.0,
        )

    with pytest.raises(local_http.LocalResponseTooLargeError) as limit_error:
        raised.value.read()
    assert "SECRET" not in str(limit_error.value)


def test_model_discovery_fails_closed_on_oversize_local_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(monkeypatch, _FakeResponse(b"123456789"))
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")

    with pytest.raises(ProviderUnavailableError):
        provider.discover_models()


def test_structured_generation_fails_closed_on_oversize_local_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(monkeypatch, _FakeResponse(b"123456789"))
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")

    with pytest.raises(ProviderUnavailableError):
        provider.generate_structured(
            model_id="local-model",
            messages=(ModelChatMessage(role="user", content="return json"),),
            schema_id="example",
            json_schema={"type": "object"},
        )


def test_controlled_structured_generation_fails_closed_on_oversize_local_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(monkeypatch, _FakeResponse(b"123456789"))
    provider = LMStudioProvider(base_url="http://127.0.0.1:1234")

    with pytest.raises(ProviderUnavailableError):
        provider.generate_controlled_structured(
            model_id="local-model",
            messages=(
                ModelChatMessage(role="system", content="return valid json"),
                ModelChatMessage(role="user", content="do it"),
            ),
            schema_id="example",
            json_schema={"type": "object"},
            reasoning_mode="off",
            context_length=4096,
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=40,
            min_p=0.0,
            repeat_penalty=1.0,
        )


def test_embedding_generation_fails_closed_on_oversize_local_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_response(monkeypatch, _FakeResponse(b"123456789"))
    model_provider = LMStudioProvider(base_url="http://127.0.0.1:1234")
    embedding_provider = LMStudioEmbeddingProvider(model_provider=model_provider)

    with pytest.raises(ProviderUnavailableError):
        embedding_provider.embed(model_id="embedding-model", texts=("hello",))
