from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge_inspection import KnowledgeInspectionApiService
from athena.knowledge.inspection_service import (
    ClaimDetails,
    ContradictionDecision,
    ContradictionReviewDetails,
)
from athena.knowledge.models import (
    ClaimDraft,
    ClaimEvidenceRef,
    ClaimKind,
    ClaimRevision,
    ClaimSnapshot,
    EpistemicStatus,
    EvidenceRole,
    ProvenanceInputRef,
)
from athena.knowledge.review_service import ReviewItem, ReviewStatus


def _revision(claim_id: uuid.UUID, statement: str) -> ClaimRevision:
    return ClaimRevision(
        claim_id=claim_id,
        revision_id=uuid.uuid4(),
        revision_no=1,
        created_at_us=10,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement=statement,
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )


class _Inspection:
    def __init__(self) -> None:
        self.left = _revision(uuid.uuid4(), "Left statement")
        self.right = _revision(uuid.uuid4(), "Right statement")
        self.snapshot = ClaimSnapshot(
            claim_id=self.left.claim_id,
            lifecycle_state="active",
            revision=self.left,
        )
        self.provenance = ProvenanceInputRef(
            provenance_id=self.left.provenance_id,
            input_entity_id=uuid.uuid4(),
            input_revision_id=uuid.uuid4(),
            input_role="chat_message_source",
            ordinal=0,
        )
        self.evidence = ClaimEvidenceRef(
            evidence_role=EvidenceRole.SUPPORTS,
            provenance_id=self.left.provenance_id,
            message_id=uuid.uuid4(),
        )
        self.review = ReviewItem(
            review_id=uuid.uuid4(),
            review_type="contradiction",
            status=ReviewStatus.PENDING,
            created_at_us=20,
            resolved_at_us=None,
            processing_run_id=uuid.uuid4(),
            model_signature_id=uuid.uuid4(),
            left_entity_id=self.left.claim_id,
            left_revision_id=self.left.revision_id,
            right_entity_id=self.right.claim_id,
            right_revision_id=self.right.revision_id,
            confidence=0.9,
            reason="semantic contradiction",
            decision_actor_id=None,
            decision_reason=None,
        )
        self.resolved_actor_id: uuid.UUID | None = None
        self.resolved_decision: ContradictionDecision | None = None

    def list_claims(self, *, limit: int = 100) -> tuple[ClaimSnapshot, ...]:
        assert limit == 7
        return (self.snapshot,)

    def load_claim(self, claim_id: uuid.UUID) -> ClaimDetails:
        assert claim_id == self.left.claim_id
        return ClaimDetails(
            snapshot=self.snapshot,
            provenance_inputs=(self.provenance,),
            evidence=(self.evidence,),
        )

    def claim_history(self, claim_id: uuid.UUID) -> tuple[ClaimRevision, ...]:
        assert claim_id == self.left.claim_id
        return (self.left,)

    def list_pending_contradictions(
        self,
        *,
        limit: int = 100,
    ) -> tuple[ContradictionReviewDetails, ...]:
        assert limit == 5
        return (self._review_details(),)

    def load_contradiction_review(
        self,
        review_id: uuid.UUID,
    ) -> ContradictionReviewDetails:
        assert review_id == self.review.review_id
        return self._review_details()

    def resolve_contradiction_review(
        self,
        review_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        decision: ContradictionDecision,
    ) -> ContradictionReviewDetails:
        assert review_id == self.review.review_id
        self.resolved_actor_id = actor_id
        self.resolved_decision = decision
        return self._review_details()

    def _review_details(self) -> ContradictionReviewDetails:
        return ContradictionReviewDetails(
            review=self.review,
            left_revision=self.left,
            right_revision=self.right,
        )


def test_claim_inspection_adapter_returns_json_safe_canonical_claim_dtos() -> None:
    inspection = _Inspection()
    api = KnowledgeInspectionApiService(
        inspection=inspection,
        actor_id_provider=uuid.uuid4,
    )

    response = api.list_claims(limit=7)[0]

    assert response.claim_id == str(inspection.left.claim_id)
    assert response.revision.statement == "Left statement"
    assert response.revision.epistemic_status == "supported"
    assert response.provenance_inputs[0].input_role == "chat_message_source"
    assert response.evidence[0].evidence_role == "supports"
    assert response.to_dict()["claim_id"] == str(inspection.left.claim_id)


def test_contradiction_adapter_uses_local_actor_and_typed_decision() -> None:
    inspection = _Inspection()
    actor_id = uuid.uuid4()
    api = KnowledgeInspectionApiService(
        inspection=inspection,
        actor_id_provider=lambda: actor_id,
    )

    response = api.resolve_contradiction_review(
        str(inspection.review.review_id),
        decision="confirm",
    )

    assert response.review_id == str(inspection.review.review_id)
    assert inspection.resolved_actor_id == actor_id
    assert inspection.resolved_decision is ContradictionDecision.CONFIRM


def test_contradiction_adapter_rejects_unknown_decision_before_domain_call() -> None:
    inspection = _Inspection()
    api = KnowledgeInspectionApiService(
        inspection=inspection,
        actor_id_provider=uuid.uuid4,
    )

    with pytest.raises(ValueError, match="confirm.*reject"):
        api.resolve_contradiction_review(
            str(inspection.review.review_id),
            decision="merge",
        )

    assert inspection.resolved_actor_id is None
    assert inspection.resolved_decision is None
