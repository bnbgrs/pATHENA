from __future__ import annotations

from typing import cast

import pytest

from athena.api.knowledge_inspection import KnowledgeInspectionApiService
from athena.api.service import CoreApiFacade
from athena.chat.service import ChatService
from athena.model.ports import ModelDiscoveryProvider
from athena.observability.health import HealthService


class _InspectionApiStub:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []
        self.claims = object()
        self.claim = object()
        self.history = object()
        self.pending = object()
        self.review = object()
        self.resolved = object()

    def list_claims(self, *, limit: int = 100) -> object:
        self.calls.append(("list_claims", limit))
        return self.claims

    def load_claim(self, claim_id: str) -> object:
        self.calls.append(("load_claim", claim_id))
        return self.claim

    def claim_history(self, claim_id: str) -> object:
        self.calls.append(("claim_history", claim_id))
        return self.history

    def list_pending_contradictions(self, *, limit: int = 100) -> object:
        self.calls.append(("list_pending_contradictions", limit))
        return self.pending

    def load_contradiction_review(self, review_id: str) -> object:
        self.calls.append(("load_contradiction_review", review_id))
        return self.review

    def resolve_contradiction_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> object:
        self.calls.append(("resolve_contradiction_review", review_id, decision))
        return self.resolved


def _facade() -> CoreApiFacade:
    return CoreApiFacade(
        health=cast(HealthService, object()),
        chat=cast(ChatService, object()),
        model_provider=cast(ModelDiscoveryProvider, object()),
    )


def _inspection_stub() -> tuple[KnowledgeInspectionApiService, _InspectionApiStub]:
    stub = _InspectionApiStub()
    return cast(KnowledgeInspectionApiService, stub), stub


def test_knowledge_inspection_capabilities_follow_attachment() -> None:
    facade = _facade()
    inspection, _stub = _inspection_stub()

    assert "knowledge.claim.inspect" not in facade.capabilities().features
    assert "knowledge.review.contradiction" not in facade.capabilities().features

    facade.attach_knowledge_inspection(inspection)

    assert "knowledge.claim.inspect" in facade.capabilities().features
    assert "knowledge.review.contradiction" in facade.capabilities().features

    with pytest.raises(RuntimeError, match="already attached"):
        facade.attach_knowledge_inspection(inspection)


def test_knowledge_inspection_calls_fail_closed_before_attachment() -> None:
    facade = _facade()

    with pytest.raises(RuntimeError, match="Knowledge inspection is unavailable"):
        facade.list_claims()

    with pytest.raises(RuntimeError, match="Knowledge inspection is unavailable"):
        facade.load_claim("00000000-0000-0000-0000-000000000001")


def test_knowledge_inspection_facade_delegates_without_rewriting_identity() -> None:
    facade = _facade()
    inspection, stub = _inspection_stub()
    facade.attach_knowledge_inspection(inspection)

    claim_id = "00000000-0000-0000-0000-000000000001"
    review_id = "00000000-0000-0000-0000-000000000002"

    assert facade.list_claims(limit=7) is stub.claims
    assert facade.load_claim(claim_id) is stub.claim
    assert facade.claim_history(claim_id) is stub.history
    assert facade.list_pending_contradictions(limit=3) is stub.pending
    assert facade.load_contradiction_review(review_id) is stub.review
    assert (
        facade.resolve_contradiction_review(review_id, decision="confirm")
        is stub.resolved
    )

    assert stub.calls == [
        ("list_claims", 7),
        ("load_claim", claim_id),
        ("claim_history", claim_id),
        ("list_pending_contradictions", 3),
        ("load_contradiction_review", review_id),
        ("resolve_contradiction_review", review_id, "confirm"),
    ]
