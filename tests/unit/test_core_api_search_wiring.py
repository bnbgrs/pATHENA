from __future__ import annotations

import uuid

import pytest

from athena.api.service import CoreApiFacade
from athena.retrieval.degradation import SemanticRetrievalUnavailableError
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType


class _FakeNormalSearch:
    def __init__(
        self,
        *,
        results: tuple[HybridSearchResult, ...] = (),
        error: Exception | None = None,
    ) -> None:
        self.results = results
        self.error = error
        self.calls: list[tuple[str, str, int, SearchEntityType | None]] = []

    def search(
        self,
        query: str,
        *,
        model_id: str,
        limit: int = 20,
        entity_type: SearchEntityType | None = None,
    ) -> tuple[HybridSearchResult, ...]:
        self.calls.append((query, model_id, limit, entity_type))
        if self.error is not None:
            raise self.error
        return self.results


def _facade() -> CoreApiFacade:
    return CoreApiFacade(
        health=object(),  # type: ignore[arg-type]
        chat=object(),  # type: ignore[arg-type]
        model_provider=object(),  # type: ignore[arg-type]
    )


def _result() -> HybridSearchResult:
    return HybridSearchResult(
        entity_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        revision_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        entity_type=SearchEntityType.KNOWLEDGE,
        title="Canonical title",
        text="Canonical preview",
        score=0.9,
        lexical_score=0.8,
        semantic_score=0.7,
        authority_score=1.0,
        contradiction_count=0,
        duplicate_count=0,
        retrieval_methods=("lexical", "semantic"),
        rank=1,
    )


def test_normal_search_capability_tracks_attachment() -> None:
    facade = _facade()
    assert "search.normal.hybrid" not in facade.capabilities().features

    facade.attach_normal_search(_FakeNormalSearch())

    assert "search.normal.hybrid" in facade.capabilities().features


def test_normal_search_attachment_is_one_time_and_preserves_first_service() -> None:
    facade = _facade()
    first = _FakeNormalSearch()
    second = _FakeNormalSearch()
    facade.attach_normal_search(first)

    with pytest.raises(RuntimeError, match="already attached"):
        facade.attach_normal_search(second)

    assert facade._normal_search is first


def test_normal_search_delegates_exact_arguments_and_uses_canonical_dto() -> None:
    facade = _facade()
    service = _FakeNormalSearch(results=(_result(),))
    facade.attach_normal_search(service)

    response = facade.search(
        "durable knowledge",
        model_id="embedding-model",
        limit=7,
        entity_type=SearchEntityType.KNOWLEDGE,
    )

    assert service.calls == [
        (
            "durable knowledge",
            "embedding-model",
            7,
            SearchEntityType.KNOWLEDGE,
        )
    ]
    assert len(response) == 1
    item = response[0]
    assert item.result_ref == "knowledge:11111111-1111-1111-1111-111111111111"
    assert item.title == "Canonical title"
    assert item.preview == "Canonical preview"
    assert item.entity_type == "knowledge"
    assert item.revision_id == "22222222-2222-2222-2222-222222222222"
    assert item.rank == 1
    assert item.retrieval_methods == ("lexical", "semantic")
    assert item.source_anchor is None
    assert item.protection.state == "unprotected"
    assert item.protection.protection_scope_id is None


def test_normal_search_propagates_semantic_unavailable_error() -> None:
    facade = _facade()
    error = SemanticRetrievalUnavailableError("knowledge_semantic_unavailable")
    facade.attach_normal_search(_FakeNormalSearch(error=error))

    with pytest.raises(SemanticRetrievalUnavailableError) as exc_info:
        facade.search("query", model_id="embedding-model")

    assert exc_info.value is error
