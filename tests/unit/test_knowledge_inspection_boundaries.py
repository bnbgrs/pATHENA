from __future__ import annotations

import uuid

import pytest

from athena.knowledge.inspection_service import (
    ContradictionDecision,
    KnowledgeInspectionService,
)


class _ClaimsStub:
    def __init__(self) -> None:
        self.list_calls = 0

    def list(self, *, limit: int = 50) -> tuple[object, ...]:
        del limit
        self.list_calls += 1
        return ()


class _ReviewsStub:
    def __init__(self) -> None:
        self.list_calls = 0
        self.get_calls = 0
        self.accept_calls = 0
        self.reject_calls = 0

    def list_pending(
        self,
        *,
        review_type: str | None = None,
        limit: int = 100,
    ) -> tuple[object, ...]:
        del review_type, limit
        self.list_calls += 1
        return ()

    def get(self, review_id: uuid.UUID) -> object:
        del review_id
        self.get_calls += 1
        raise AssertionError("unexpected review load")

    def accept(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> object:
        del review_id, actor_id
        self.accept_calls += 1
        raise AssertionError("unexpected accept")

    def reject(self, review_id: uuid.UUID, *, actor_id: uuid.UUID) -> object:
        del review_id, actor_id
        self.reject_calls += 1
        raise AssertionError("unexpected reject")


@pytest.mark.parametrize("limit", [True, False, 0, -1, 1.0, 1.5, "10", None, 501])
def test_claim_list_rejects_invalid_limit_before_reader(limit: object) -> None:
    claims = _ClaimsStub()
    service = KnowledgeInspectionService(
        claims=claims,  # type: ignore[arg-type]
        reviews=_ReviewsStub(),  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError):
        service.list_claims(limit=limit)  # type: ignore[arg-type]

    assert claims.list_calls == 0


@pytest.mark.parametrize("limit", [True, False, 0, -1, 1.0, 1.5, "10", None, 501])
def test_pending_review_list_rejects_invalid_limit_before_queue(limit: object) -> None:
    reviews = _ReviewsStub()
    service = KnowledgeInspectionService(
        claims=_ClaimsStub(),  # type: ignore[arg-type]
        reviews=reviews,  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError):
        service.list_pending_contradictions(limit=limit)  # type: ignore[arg-type]

    assert reviews.list_calls == 0


def test_raw_string_decision_is_rejected_before_review_load_or_mutation() -> None:
    reviews = _ReviewsStub()
    service = KnowledgeInspectionService(
        claims=_ClaimsStub(),  # type: ignore[arg-type]
        reviews=reviews,  # type: ignore[arg-type]
    )

    with pytest.raises(TypeError, match="ContradictionDecision"):
        service.resolve_contradiction_review(
            uuid.uuid4(),
            actor_id=uuid.uuid4(),
            decision="confirm",  # type: ignore[arg-type]
        )

    assert reviews.get_calls == 0
    assert reviews.accept_calls == 0
    assert reviews.reject_calls == 0


@pytest.mark.parametrize("field", ["review_id", "actor_id"])
def test_resolution_rejects_non_uuid_identity_before_review_load(field: str) -> None:
    reviews = _ReviewsStub()
    service = KnowledgeInspectionService(
        claims=_ClaimsStub(),  # type: ignore[arg-type]
        reviews=reviews,  # type: ignore[arg-type]
    )
    values: dict[str, object] = {
        "review_id": uuid.uuid4(),
        "actor_id": uuid.uuid4(),
    }
    values[field] = "not-a-uuid"

    with pytest.raises(TypeError, match="must be a UUID"):
        service.resolve_contradiction_review(
            values["review_id"],  # type: ignore[arg-type]
            actor_id=values["actor_id"],  # type: ignore[arg-type]
            decision=ContradictionDecision.CONFIRM,
        )

    assert reviews.get_calls == 0
