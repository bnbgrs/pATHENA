from __future__ import annotations

import math

import pytest

from athena.model.adapters.lm_studio import LMStudioProvider, ProviderProtocolError
from athena.model.adapters.lm_studio_embeddings import LMStudioEmbeddingProvider


def _provider() -> LMStudioProvider:
    return LMStudioProvider(base_url="http://127.0.0.1:1234")


def test_embedding_provider_requires_lm_studio_provider() -> None:
    with pytest.raises(TypeError, match="must be an LMStudioProvider"):
        LMStudioEmbeddingProvider(model_provider=object())  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0, -1, math.nan, math.inf, -math.inf])
def test_embedding_provider_rejects_invalid_generation_timeout(value: object) -> None:
    with pytest.raises(ValueError, match="finite number > 0"):
        LMStudioEmbeddingProvider(
            model_provider=_provider(),
            generation_timeout_seconds=value,  # type: ignore[arg-type]
        )


def test_embedding_provider_normalizes_integer_generation_timeout() -> None:
    provider = LMStudioEmbeddingProvider(
        model_provider=_provider(),
        generation_timeout_seconds=30,
    )

    assert provider.generation_timeout_seconds == 30.0


@pytest.mark.parametrize("component", [True, False, math.nan, math.inf, -math.inf, "1"])
def test_embedding_vector_rejects_non_finite_or_non_numeric_components(component: object) -> None:
    with pytest.raises(ProviderProtocolError):
        LMStudioEmbeddingProvider._parse_vector([component])


def test_embedding_vector_accepts_finite_integer_and_float_components() -> None:
    assert LMStudioEmbeddingProvider._parse_vector([1, 2.5, -3]) == (1.0, 2.5, -3.0)
