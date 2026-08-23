from __future__ import annotations

import uuid

import pytest

from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType


def _result(**overrides: object) -> HybridSearchResult:
    values: dict[str, object] = {
        "entity_id": uuid.uuid4(),
        "revision_id": uuid.uuid4(),
        "entity_type": SearchEntityType.KNOWLEDGE,
        "title": None,
        "text": "evidence",
        "score": 0.2,
        "lexical_score": 0.1,
        "semantic_score": 0.1,
        "authority_score": 1.0,
        "contradiction_count": 0,
        "duplicate_count": 0,
    }
    values.update(overrides)
    return HybridSearchResult(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["entity_id", "revision_id"])
def test_hybrid_result_rejects_non_uuid_identity(field: str) -> None:
    with pytest.raises(TypeError, match="must be a UUID"):
        _result(**{field: "not-a-uuid"})


@pytest.mark.parametrize(
    "field,value",
    [
        ("score", float("nan")),
        ("score", float("inf")),
        ("lexical_score", float("-inf")),
        ("semantic_score", True),
        ("authority_score", 1.1),
        ("authority_score", 10**400),
    ],
)
def test_hybrid_result_rejects_invalid_scores(field: str, value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _result(**{field: value})


@pytest.mark.parametrize("field", ["contradiction_count", "duplicate_count"])
@pytest.mark.parametrize("value", [True, False, -1, 1.5, "1"])
def test_hybrid_result_rejects_invalid_counts(field: str, value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _result(**{field: value})


def test_hybrid_result_accepts_finite_valid_boundary_values() -> None:
    result = _result(
        score=0,
        lexical_score=0,
        semantic_score=0,
        authority_score=0,
        contradiction_count=0,
        duplicate_count=0,
    )

    assert result.score == 0
    assert result.authority_score == 0
