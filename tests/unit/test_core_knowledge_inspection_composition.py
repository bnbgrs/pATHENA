from __future__ import annotations

import uuid
from typing import cast

from athena.chat.service import ChatService
from athena.core.knowledge_inspection import build_knowledge_inspection_api
from athena.knowledge.claim_repository import ClaimRepository
from athena.knowledge.claim_service import ClaimService
from athena.knowledge.models import ClaimSnapshot
from athena.knowledge.review_service import ReviewService


class _ReadOnlyClaimRepository:
    """Small runtime probe for the ClaimService read path used by inspection."""

    def list_current(self, *, limit: int = 50) -> tuple[ClaimSnapshot, ...]:
        assert limit == 7
        return ()


def test_claim_inspection_composition_reuses_canonical_dependencies() -> None:
    repository = cast(ClaimRepository, _ReadOnlyClaimRepository())
    claims = ClaimService(repository, cast(ChatService, object()))
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

    # Exercise the composed runtime boundary. Passing ClaimRepository directly
    # used to type-check at the builder boundary but failed here because it does
    # not expose ClaimReader.list/load/history/evidence method names.
    assert api.list_claims(limit=7) == ()
