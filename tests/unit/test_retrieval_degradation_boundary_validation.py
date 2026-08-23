from __future__ import annotations

import pytest

from athena.model.domain import ModelInfo
from athena.retrieval.degradation import (
    HYBRID_RETRIEVAL_MODE,
    SemanticRetrievalUnavailableError,
    resolve_embedding_model_for_retrieval,
)


@pytest.mark.parametrize("value", ["", "   ", 1, True, None])
def test_semantic_retrieval_error_reason_requires_text(value: object) -> None:
    with pytest.raises(ValueError):
        SemanticRetrievalUnavailableError(value)  # type: ignore[arg-type]


def test_semantic_retrieval_error_normalizes_reason() -> None:
    error = SemanticRetrievalUnavailableError("  embedding_unavailable  ")

    assert error.reason_code == "embedding_unavailable"
    assert str(error) == "embedding_unavailable"


@pytest.mark.parametrize("requested_model_id", [1, True, object()])
def test_retrieval_model_resolution_rejects_non_text_model_id(
    requested_model_id: object,
) -> None:
    with pytest.raises(ValueError):
        resolve_embedding_model_for_retrieval(
            object(),  # type: ignore[arg-type]
            requested_model_id,  # type: ignore[arg-type]
        )


def test_retrieval_model_resolution_rejects_provider_without_capability() -> None:
    with pytest.raises(ValueError):
        resolve_embedding_model_for_retrieval(
            object(),  # type: ignore[arg-type]
            None,
        )


def test_retrieval_model_resolution_preserves_duck_typed_resolver() -> None:
    model = ModelInfo(
        provider="test",
        backend_model_id="embed-model",
        display_name="Embed Model",
        model_type="embedding",
        context_capacity=None,
        quantization=None,
        loaded=True,
        vision=None,
        trained_for_tool_use=None,
    )

    class Resolver:
        def resolve_model(self, requested_model_id: str | None = None) -> ModelInfo:
            assert requested_model_id == "embed-model"
            return model

    resolution = resolve_embedding_model_for_retrieval(
        Resolver(),  # type: ignore[arg-type]
        " embed-model ",
    )

    assert resolution.model == model
    assert resolution.mode == HYBRID_RETRIEVAL_MODE
    assert resolution.warning is None
