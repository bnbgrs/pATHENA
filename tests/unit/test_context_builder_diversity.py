from __future__ import annotations

import uuid

from athena.retrieval.context import ContextBuilderService
from athena.retrieval.ranking import RankedSearchResult
from athena.retrieval.search import SearchEntityType


def _ranked(
    text: str,
    *,
    score: float,
    entity_type: SearchEntityType = SearchEntityType.KNOWLEDGE,
    contradictions: int = 0,
) -> RankedSearchResult:
    return RankedSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=entity_type,
        title="Test",
        snippet=text,
        text=text,
        score=score,
        lexical_score=1.0,
        authority_score=1.0,
        contradiction_score=min(1.0, contradictions / 2.0),
        contradiction_count=contradictions,
        duplicate_count=0,
        duplicate_entity_ids=(),
    )


def test_context_max_items_prefers_diverse_source_over_near_duplicate() -> None:
    first = _ranked(
        "Berlin Germany capital government parliament city facts",
        score=0.95,
    )
    duplicate = _ranked(
        "Berlin Germany capital government parliament city facts update",
        score=0.94,
    )
    diverse = _ranked(
        "Munich Bavaria economy technology universities research",
        score=0.80,
    )

    bundle = ContextBuilderService().build_from_ranked(
        query="German cities",
        results=(first, duplicate, diverse),
        max_estimated_tokens=1200,
        max_items=2,
    )

    assert [item.entity_id for item in bundle.items] == [
        first.entity_id,
        diverse.entity_id,
    ]
    assert bundle.omitted_count == 1


def test_context_diversity_never_defers_contradiction_bearing_claim() -> None:
    first = _ranked(
        "Berlin Germany capital government parliament city facts",
        score=0.95,
    )
    contradictory_claim = _ranked(
        "Berlin Germany capital government parliament city facts update",
        score=0.94,
        entity_type=SearchEntityType.CLAIM,
        contradictions=1,
    )
    diverse = _ranked(
        "Munich Bavaria economy technology universities research",
        score=0.80,
    )

    bundle = ContextBuilderService().build_from_ranked(
        query="German cities",
        results=(first, contradictory_claim, diverse),
        max_estimated_tokens=1200,
        max_items=2,
    )

    assert [item.entity_id for item in bundle.items] == [
        first.entity_id,
        contradictory_claim.entity_id,
    ]
    assert bundle.items[1].contradiction_count == 1
