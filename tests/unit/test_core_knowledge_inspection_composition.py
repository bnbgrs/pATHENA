from __future__ import annotations

import uuid
from typing import cast

import pytest

from athena.api.service import CoreApiFacade
from athena.chat.service import ChatService
from athena.core.knowledge_inspection import (
    attach_knowledge_inspection_api,
    build_knowledge_inspection_api,
)
from athena.knowledge.claim_repository import ClaimRepository
from athena.knowledge.claim_service import ClaimService
from athena.knowledge.models import ClaimSnapshot
from athena.knowledge.review_service import ReviewService
from athena.model.ports import ModelDiscoveryProvider
from athena.observability.health import HealthService


class _ReadOnlyClaimRepository:
    """Small runtime probe for the ClaimService read path used by inspection."""

    def list_current(self, *, limit: int = 50) -> tuple[ClaimSnapshot, ...]:
        assert limit == 7
        return ()


def _claims() -> ClaimService:
    repository = cast(ClaimRepository, _ReadOnlyClaimRepository())
    return ClaimService(repository, cast(ChatService, object()))


def _facade() -> CoreApiFacade:
    return CoreApiFacade(
        health=HealthService(),
        chat=cast(ChatService, object()),
        model_provider=cast(ModelDiscoveryProvider, object()),
    )


def test_claim_inspection_composition_reuses_canonical_dependencies() -> None:
    claims = _claims()
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


def test_claim_inspection_attachment_reuses_exact_api_instance() -> None:
    claims = _claims()
    reviews = cast(ReviewService, object())
    facade = _facade()
    actor_id = uuid.uuid4()

    def actor_id_provider() -> uuid.UUID:
        return actor_id

    assert "knowledge.claim.inspect" not in facade.capabilities().features
    assert "knowledge.review.contradiction" not in facade.capabilities().features

    inspection_api = attach_knowledge_inspection_api(
        facade=facade,
        claims=claims,
        reviews=reviews,
        actor_id_provider=actor_id_provider,
    )

    assert facade._knowledge_inspection is inspection_api
    assert inspection_api._inspection._claims is claims
    assert inspection_api._inspection._reviews is reviews
    assert inspection_api._actor_id_provider is actor_id_provider
    assert "knowledge.claim.inspect" in facade.capabilities().features
    assert "knowledge.review.contradiction" in facade.capabilities().features
    assert facade.list_claims(limit=7) == ()

    with pytest.raises(RuntimeError, match="already attached"):
        attach_knowledge_inspection_api(
            facade=facade,
            claims=claims,
            reviews=reviews,
            actor_id_provider=actor_id_provider,
        )
