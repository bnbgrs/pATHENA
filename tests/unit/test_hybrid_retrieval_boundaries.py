from __future__ import annotations

import pytest

from athena.retrieval.hybrid import HybridRetrievalService


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "60", None])
def test_hybrid_retrieval_rejects_invalid_rrf_k(value: object) -> None:
    with pytest.raises(ValueError, match="RRF k must be a positive integer"):
        HybridRetrievalService(
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            rrf_k=value,  # type: ignore[arg-type]
        )


def test_hybrid_retrieval_accepts_positive_integer_rrf_k() -> None:
    service = HybridRetrievalService(
        object(),  # type: ignore[arg-type]
        object(),  # type: ignore[arg-type]
        rrf_k=17,
    )
    assert service.rrf_k == 17


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "20", None, 201])
def test_hybrid_search_limit_rejects_noncanonical_values(value: object) -> None:
    with pytest.raises(ValueError):
        HybridRetrievalService._validate_limit(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [1, 20, 200])
def test_hybrid_search_limit_accepts_integer_boundary_values(value: int) -> None:
    HybridRetrievalService._validate_limit(value)
