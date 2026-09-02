from __future__ import annotations

import pytest

from athena.model.adapters.lm_studio import ModelProviderError
from athena.model.domain import ModelInfo
from athena.retrieval.degradation import (
    EMBEDDING_MODEL_NOT_LOADED_WARNING,
    EMBEDDING_MODEL_UNAVAILABLE_WARNING,
    HYBRID_RETRIEVAL_MODE,
    LEXICAL_FALLBACK_RETRIEVAL_MODE,
    EmbeddingRetrievalResolution,
    resolve_embedding_model_for_retrieval,
)


def _model(*, loaded: bool) -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="embedding-model",
        display_name="Embedding Model",
        model_type="embedding",
        context_capacity=4096,
        quantization=None,
        loaded=loaded,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=4096,
    )


def test_hybrid_resolution_requires_loaded_model_without_warning() -> None:
    resolution = EmbeddingRetrievalResolution(
        model=_model(loaded=True),
        mode=HYBRID_RETRIEVAL_MODE,
        warning=None,
    )
    assert resolution.model is not None


@pytest.mark.parametrize(
    ("model", "warning"),
    [
        (None, None),
        (_model(loaded=False), None),
        (_model(loaded=True), EMBEDDING_MODEL_UNAVAILABLE_WARNING),
    ],
)
def test_hybrid_resolution_rejects_inconsistent_state(
    model: ModelInfo | None,
    warning: str | None,
) -> None:
    with pytest.raises(ValueError):
        EmbeddingRetrievalResolution(
            model=model,
            mode=HYBRID_RETRIEVAL_MODE,
            warning=warning,
        )


def test_fallback_resolution_requires_known_warning_and_no_model() -> None:
    with pytest.raises(ValueError):
        EmbeddingRetrievalResolution(
            model=None,
            mode=LEXICAL_FALLBACK_RETRIEVAL_MODE,
            warning="unknown_warning",
        )
    with pytest.raises(ValueError):
        EmbeddingRetrievalResolution(
            model=_model(loaded=True),
            mode=LEXICAL_FALLBACK_RETRIEVAL_MODE,
            warning=EMBEDDING_MODEL_NOT_LOADED_WARNING,
        )


class _Resolver:
    def __init__(self, result: ModelInfo | Exception) -> None:
        self.result = result

    def resolve_model(self, requested_model_id: str | None = None) -> ModelInfo:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_resolver_returns_lexical_fallback_when_provider_is_unavailable() -> None:
    resolution = resolve_embedding_model_for_retrieval(
        _Resolver(ModelProviderError("offline")),  # type: ignore[arg-type]
        None,
    )
    assert resolution.mode == LEXICAL_FALLBACK_RETRIEVAL_MODE
    assert resolution.warning == EMBEDDING_MODEL_UNAVAILABLE_WARNING


def test_resolver_returns_lexical_fallback_when_model_is_not_loaded() -> None:
    resolution = resolve_embedding_model_for_retrieval(
        _Resolver(_model(loaded=False)),  # type: ignore[arg-type]
        None,
    )
    assert resolution.mode == LEXICAL_FALLBACK_RETRIEVAL_MODE
    assert resolution.warning == EMBEDDING_MODEL_NOT_LOADED_WARNING


def test_resolver_rejects_non_model_return() -> None:
    resolver = _Resolver(_model(loaded=True))
    resolver.result = object()  # type: ignore[assignment]
    with pytest.raises(ValueError, match="invalid model"):
        resolve_embedding_model_for_retrieval(
            resolver,  # type: ignore[arg-type]
            None,
        )
