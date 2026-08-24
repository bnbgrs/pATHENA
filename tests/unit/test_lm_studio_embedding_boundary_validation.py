from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pytest

from athena.model.adapters.lm_studio import ModelProviderError, ProviderProtocolError
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider
from athena.model.domain import ModelInfo


@dataclass
class _ModelProvider:
    base_url: str = "http://127.0.0.1:1234"
    models: tuple[ModelInfo, ...] = ()

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return self.models


def _provider(
    *,
    timeout: Any = 300.0,
    models: tuple[ModelInfo, ...] = (),
) -> LMStudioEmbeddingProvider:
    return LMStudioEmbeddingProvider(
        model_provider=_ModelProvider(models=models),  # type: ignore[arg-type]
        generation_timeout_seconds=timeout,
    )


@pytest.mark.parametrize(
    "timeout",
    [True, False, 0, -1, math.nan, math.inf, -math.inf, "30", None],
)
def test_embedding_provider_rejects_invalid_timeout(timeout: Any) -> None:
    with pytest.raises(ValueError):
        _provider(timeout=timeout)


@pytest.mark.parametrize("model_id", [None, 1, True, "", "   "])
def test_embed_rejects_invalid_model_id_before_transport(model_id: Any) -> None:
    provider = _provider()

    with pytest.raises(ValueError):
        provider.embed(model_id=model_id, texts=("text",))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "texts",
    [
        "abc",
        b"abc",
        bytearray(b"abc"),
        ["ok", 1],
        ["ok", None],
        ["ok", "   "],
    ],
)
def test_embed_rejects_non_text_sequences_before_transport(texts: Any) -> None:
    provider = _provider()

    with pytest.raises(ValueError):
        provider.embed(model_id="embedding-model", texts=texts)


def test_embed_empty_sequence_remains_noop() -> None:
    provider = _provider()

    assert provider.embed(model_id="embedding-model", texts=()) == ()


def test_resolve_model_rejects_non_text_explicit_id() -> None:
    provider = _provider()

    with pytest.raises(ModelProviderError):
        provider.resolve_model(1)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "vector",
    [
        [],
        [True],
        ["1.0"],
        [math.nan],
        [math.inf],
        [-math.inf],
    ],
)
def test_embedding_vector_parser_rejects_invalid_components(vector: object) -> None:
    with pytest.raises(ProviderProtocolError):
        LMStudioEmbeddingProvider._parse_vector(vector)


def test_embedding_vector_parser_accepts_finite_numeric_vector() -> None:
    assert LMStudioEmbeddingProvider._parse_vector([1, 2.5, -3]) == (
        1.0,
        2.5,
        -3.0,
    )
