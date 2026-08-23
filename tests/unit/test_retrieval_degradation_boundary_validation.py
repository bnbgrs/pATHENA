from __future__ import annotations

import pytest

from athena.retrieval.degradation import (
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


def test_retrieval_model_resolution_rejects_untyped_provider_first() -> None:
    with pytest.raises(ValueError):
        resolve_embedding_model_for_retrieval(
            object(),  # type: ignore[arg-type]
            None,
        )
