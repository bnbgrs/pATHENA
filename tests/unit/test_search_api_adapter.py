from __future__ import annotations

import uuid

import pytest

from athena.api.search_adapter import hybrid_search_result_response
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType


def _hybrid_result(*, rank: int | None = 1) -> HybridSearchResult:
    return HybridSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=SearchEntityType.KNOWLEDGE,
        title="Durable knowledge",
        text="Canonical content",
        score=1.0,
        lexical_score=0.5,
        semantic_score=0.5,
        authority_score=1.0,
        contradiction_count=0,
        duplicate_count=0,
        retrieval_methods=("lexical", "semantic"),
        rank=rank,
    )


def test_hybrid_adapter_preserves_rank_methods_revision_and_unprotected_boundary() -> None:
    result = _hybrid_result()

    response = hybrid_search_result_response(result)

    assert response.result_ref == f"knowledge:{result.entity_id}"
    assert response.title == result.title
    assert response.preview == result.text
    assert response.entity_type == "knowledge"
    assert response.revision_id == str(result.revision_id)
    assert response.rank == 1
    assert response.retrieval_methods == ("lexical", "semantic")
    assert response.source_anchor is None
    assert response.protection.state == "unprotected"
    assert response.protection.protection_scope_id is None


def test_hybrid_adapter_rejects_result_without_final_rank() -> None:
    with pytest.raises(ValueError, match="final rank"):
        hybrid_search_result_response(_hybrid_result(rank=None))


def test_hybrid_adapter_rejects_wrong_result_type() -> None:
    with pytest.raises(TypeError, match="HybridSearchResult"):
        hybrid_search_result_response(object())  # type: ignore[arg-type]
