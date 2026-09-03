from __future__ import annotations

import uuid

import pytest

from athena.retrieval.hybrid import HybridSearchResult, _Candidate, _diversify, _score
from athena.retrieval.search import SearchEntityType


def _candidate(*, lexical_score: float, semantic_score: float) -> _Candidate:
    entity_id = uuid.uuid4()
    return _Candidate(
        entity_id=entity_id,
        revision_id=uuid.uuid4(),
        entity_type=SearchEntityType.KNOWLEDGE,
        title=None,
        text="evidence",
        lexical_score=lexical_score,
        semantic_score=semantic_score,
        contradiction_count=0,
        member_entity_ids=frozenset((entity_id,)),
    )


@pytest.mark.parametrize(
    ("lexical_score", "semantic_score", "expected"),
    [
        (0.1, 0.0, ("lexical",)),
        (0.0, 0.1, ("semantic",)),
        (0.1, 0.2, ("lexical", "semantic")),
    ],
)
def test_hybrid_score_exposes_contributing_retrieval_methods(
    lexical_score: float,
    semantic_score: float,
    expected: tuple[str, ...],
) -> None:
    result = _score(
        _candidate(
            lexical_score=lexical_score,
            semantic_score=semantic_score,
        )
    )

    assert result.retrieval_methods == expected


def _result(*, retrieval_methods: object, score: float = 0.2, rank: object = None) -> HybridSearchResult:
    return HybridSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=SearchEntityType.KNOWLEDGE,
        title=None,
        text="evidence",
        score=score,
        lexical_score=0.1,
        semantic_score=0.1,
        authority_score=1.0,
        contradiction_count=0,
        duplicate_count=0,
        retrieval_methods=retrieval_methods,  # type: ignore[arg-type]
        rank=rank,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "retrieval_methods",
    [
        ["lexical"],
        ("unknown",),
        ("semantic", "lexical"),
        ("lexical", "lexical"),
    ],
)
def test_hybrid_result_rejects_noncanonical_retrieval_methods(
    retrieval_methods: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _result(retrieval_methods=retrieval_methods)


@pytest.mark.parametrize("rank", [0, -1, True, "1"])
def test_hybrid_result_rejects_invalid_rank(rank: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _result(retrieval_methods=("lexical",), rank=rank)


def test_hybrid_result_keeps_backward_compatible_empty_provenance_default() -> None:
    result = HybridSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=SearchEntityType.KNOWLEDGE,
        title=None,
        text="evidence",
        score=0.0,
        lexical_score=0.0,
        semantic_score=0.0,
        authority_score=1.0,
        contradiction_count=0,
        duplicate_count=0,
    )

    assert result.retrieval_methods == ()
    assert result.rank is None


def test_diversified_hybrid_results_expose_final_contiguous_rank() -> None:
    results = (
        _result(retrieval_methods=("lexical",), score=0.3),
        _result(retrieval_methods=("semantic",), score=0.2),
        _result(retrieval_methods=("lexical", "semantic"), score=0.1),
    )

    diversified = _diversify(results, limit=3)

    assert tuple(item.rank for item in diversified) == (1, 2, 3)
