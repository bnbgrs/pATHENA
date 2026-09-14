from __future__ import annotations

import uuid
from typing import cast

from athena.knowledge.claim_repository import ClaimRepository
from athena.knowledge.review_service import ReviewService
from athena.core.knowledge_inspection import build_knowledge_inspection_api


def test_claim_inspection_composition_reuses_canonical_dependencies() -> None:
    claims = cast(ClaimRepository, object())
    reviews = cast(ReviewService, object())
    actor_id = uuid.uuid4()

    def actor_id_provider() -> uuid.UUID:
        return actor_id

    api = build_knowledge_inspection_api(
        claims=claims,
        reviews=reviews,
        actor_id_provider=actor_id_provider,
    )

    inspection = api._inspection
    assert inspection._claims is claims
    assert inspection._reviews is reviews
    assert api._actor_id_provider is actor_id_provider
    assert api._actor_id_provider() == actor_id
