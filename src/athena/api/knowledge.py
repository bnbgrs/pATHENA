"""Transport-neutral API facade for canonical Claims and contradiction reviews."""

from __future__ import annotations

import uuid
from typing import Protocol

from athena.api.contracts import (
    CanonicalClaimResponse,
    CanonicalClaimRevisionResponse,
    ClaimEvidenceResponse,
    ClaimProvenanceInputResponse,
    ContradictionReviewResponse,
)
from athena.knowledge.inspection_service import (
    ContradictionDecision,
    ContradictionReviewDetails,
    KnowledgeInspectionService,
)
from athena.knowledge.models import (
    ClaimEvidenceRef,
    ClaimRevision,
    ProvenanceInputRef,
)


class LocalActorProvider(Protocol):
    """Resolve the stable local user identity for explicit review decisions."""

    def ensure_local_user(self) -> uuid.UUID: ...


class KnowledgeApiService:
    """Versioned-contract adapter over canonical Knowledge inspection semantics."""

    def __init__(
        self,
        *,
        inspection: KnowledgeInspectionService,
        actors: LocalActorProvider,
    ) -> None:
        self._inspection = inspection
        self._actors = actors

    def list_claims(self, *, limit: int = 100) -> tuple[CanonicalClaimResponse, ...]:
        return tuple(
            self._claim_response(snapshot.claim_id)
            for snapshot in self._inspection.list_claims(limit=limit)
        )

    def load_claim(self, claim_id: str) -> CanonicalClaimResponse:
        return self._claim_response(uuid.UUID(claim_id))

    def claim_history(
        self,
        claim_id: str,
    ) -> tuple[CanonicalClaimRevisionResponse, ...]:
        return tuple(
            _claim_revision_response(revision)
            for revision in self._inspection.claim_history(uuid.UUID(claim_id))
        )

    def list_pending_contradictions(
        self,
        *,
        limit: int = 100,
    ) -> tuple[ContradictionReviewResponse, ...]:
        return tuple(
            _contradiction_review_response(details)
            for details in self._inspection.list_pending_contradictions(limit=limit)
        )

    def load_contradiction_review(
        self,
        review_id: str,
    ) -> ContradictionReviewResponse:
        return _contradiction_review_response(
            self._inspection.load_contradiction_review(uuid.UUID(review_id))
        )

    def resolve_contradiction_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> ContradictionReviewResponse:
        try:
            parsed_decision = ContradictionDecision(decision)
        except ValueError as exc:
            raise ValueError(
                "Contradiction decision must be 'confirm' or 'reject'."
            ) from exc
        return _contradiction_review_response(
            self._inspection.resolve_contradiction_review(
                uuid.UUID(review_id),
                actor_id=self._actors.ensure_local_user(),
                decision=parsed_decision,
            )
        )

    def _claim_response(self, claim_id: uuid.UUID) -> CanonicalClaimResponse:
        details = self._inspection.load_claim(claim_id)
        snapshot = details.snapshot
        return CanonicalClaimResponse(
            claim_id=str(snapshot.claim_id),
            lifecycle_state=snapshot.lifecycle_state,
            revision=_claim_revision_response(snapshot.revision),
            provenance_inputs=tuple(
                _provenance_response(item) for item in details.provenance_inputs
            ),
            evidence=tuple(_evidence_response(item) for item in details.evidence),
        )


def _claim_revision_response(revision: ClaimRevision) -> CanonicalClaimRevisionResponse:
    payload = revision.payload
    return CanonicalClaimRevisionResponse(
        claim_id=str(revision.claim_id),
        revision_id=str(revision.revision_id),
        revision_no=revision.revision_no,
        created_at_us=revision.created_at_us,
        created_by_actor_id=str(revision.created_by_actor_id),
        provenance_id=str(revision.provenance_id),
        claim_kind=payload.claim_kind.value,
        statement=payload.statement,
        epistemic_status=payload.epistemic_status.value,
        subject_entity_id=(
            None if payload.subject_entity_id is None else str(payload.subject_entity_id)
        ),
        predicate=payload.predicate,
        object_entity_id=(
            None if payload.object_entity_id is None else str(payload.object_entity_id)
        ),
        attributed_to_entity_id=(
            None
            if payload.attributed_to_entity_id is None
            else str(payload.attributed_to_entity_id)
        ),
        valid_from_us=payload.valid_from_us,
        valid_to_us=payload.valid_to_us,
    )


def _provenance_response(item: ProvenanceInputRef) -> ClaimProvenanceInputResponse:
    return ClaimProvenanceInputResponse(
        provenance_id=str(item.provenance_id),
        input_entity_id=str(item.input_entity_id),
        input_revision_id=(
            None if item.input_revision_id is None else str(item.input_revision_id)
        ),
        input_role=item.input_role,
        ordinal=item.ordinal,
    )


def _evidence_response(item: ClaimEvidenceRef) -> ClaimEvidenceResponse:
    return ClaimEvidenceResponse(
        evidence_role=item.evidence_role.value,
        provenance_id=str(item.provenance_id),
        anchor_id=None if item.anchor_id is None else str(item.anchor_id),
        message_id=None if item.message_id is None else str(item.message_id),
        evidence_entity_id=(
            None if item.evidence_entity_id is None else str(item.evidence_entity_id)
        ),
        evidence_revision_id=(
            None if item.evidence_revision_id is None else str(item.evidence_revision_id)
        ),
    )


def _contradiction_review_response(
    details: ContradictionReviewDetails,
) -> ContradictionReviewResponse:
    item = details.review
    return ContradictionReviewResponse(
        review_id=str(item.review_id),
        status=item.status.value,
        created_at_us=item.created_at_us,
        resolved_at_us=item.resolved_at_us,
        processing_run_id=str(item.processing_run_id),
        model_signature_id=str(item.model_signature_id),
        confidence=item.confidence,
        reason=item.reason,
        left_revision=_claim_revision_response(details.left_revision),
        right_revision=_claim_revision_response(details.right_revision),
        decision_actor_id=(
            None if item.decision_actor_id is None else str(item.decision_actor_id)
        ),
        decision_reason=item.decision_reason,
    )
