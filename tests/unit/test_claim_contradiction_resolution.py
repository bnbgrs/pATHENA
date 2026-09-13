from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from athena.knowledge.claim_service import ClaimService, ContradictionResolutionError
from athena.knowledge.models import (
    ClaimDraft,
    ClaimEvidenceRef,
    ClaimKind,
    ClaimRevision,
    ClaimSnapshot,
    EpistemicStatus,
    EvidenceRole,
)


def _snapshot(*, status: EpistemicStatus = EpistemicStatus.CONTRADICTED) -> ClaimSnapshot:
    claim_id = uuid.uuid4()
    return ClaimSnapshot(
        claim_id=claim_id,
        lifecycle_state="active",
        revision=ClaimRevision(
            claim_id=claim_id,
            revision_id=uuid.uuid4(),
            revision_no=3,
            created_at_us=123,
            created_by_actor_id=uuid.uuid4(),
            provenance_id=uuid.uuid4(),
            payload=ClaimDraft(
                claim_kind=ClaimKind.FACTUAL_ASSERTION,
                statement="The deployment window is Friday.",
                epistemic_status=status,
                predicate="deployment_window",
                valid_from_us=10,
                valid_to_us=20,
            ),
        ),
    )


def _contradiction_ref(other_claim_id: uuid.UUID | None = None) -> ClaimEvidenceRef:
    return ClaimEvidenceRef(
        evidence_role=EvidenceRole.CONTRADICTS,
        provenance_id=uuid.uuid4(),
        evidence_entity_id=other_claim_id or uuid.uuid4(),
        evidence_revision_id=uuid.uuid4(),
    )


def test_resolve_contradiction_revises_status_without_rewriting_claim() -> None:
    repository = Mock()
    chat = Mock()
    current = _snapshot()
    actor_id = uuid.uuid4()
    revised = ClaimRevision(
        claim_id=current.claim_id,
        revision_id=uuid.uuid4(),
        revision_no=4,
        created_at_us=124,
        created_by_actor_id=actor_id,
        provenance_id=uuid.uuid4(),
        payload=ClaimDraft(
            claim_kind=current.revision.payload.claim_kind,
            statement=current.revision.payload.statement,
            epistemic_status=EpistemicStatus.SUPPORTED,
            predicate=current.revision.payload.predicate,
            valid_from_us=current.revision.payload.valid_from_us,
            valid_to_us=current.revision.payload.valid_to_us,
        ),
    )
    repository.load_current.return_value = current
    repository.list_evidence.return_value = (_contradiction_ref(),)
    repository.revise_claim.return_value = revised
    chat.ensure_local_user.return_value = actor_id

    result = ClaimService(repository, chat).resolve_contradiction(
        claim_id=current.claim_id,
        epistemic_status=EpistemicStatus.SUPPORTED,
    )

    assert result is revised
    call = repository.revise_claim.call_args.kwargs
    assert call["claim_id"] == current.claim_id
    assert call["expected_revision_id"] == current.revision.revision_id
    assert call["actor_id"] == actor_id
    assert call["reason"] == "explicit user contradiction resolution"
    assert call["draft"] == ClaimDraft(
        claim_kind=current.revision.payload.claim_kind,
        statement=current.revision.payload.statement,
        epistemic_status=EpistemicStatus.SUPPORTED,
        subject_entity_id=current.revision.payload.subject_entity_id,
        predicate=current.revision.payload.predicate,
        object_entity_id=current.revision.payload.object_entity_id,
        attributed_to_entity_id=current.revision.payload.attributed_to_entity_id,
        valid_from_us=current.revision.payload.valid_from_us,
        valid_to_us=current.revision.payload.valid_to_us,
    )


def test_resolve_contradiction_requires_concrete_contradiction_evidence() -> None:
    repository = Mock()
    chat = Mock()
    current = _snapshot()
    repository.load_current.return_value = current
    repository.list_evidence.return_value = (
        ClaimEvidenceRef(
            evidence_role=EvidenceRole.SUPPORTS,
            provenance_id=uuid.uuid4(),
            evidence_entity_id=uuid.uuid4(),
        ),
    )

    with pytest.raises(ContradictionResolutionError, match="no contradiction evidence"):
        ClaimService(repository, chat).resolve_contradiction(
            claim_id=current.claim_id,
            epistemic_status=EpistemicStatus.UNCERTAIN,
        )

    repository.revise_claim.assert_not_called()
    chat.ensure_local_user.assert_not_called()


def test_resolve_contradiction_rejects_still_contradicted_target() -> None:
    repository = Mock()
    chat = Mock()

    with pytest.raises(ContradictionResolutionError, match="non-contradicted"):
        ClaimService(repository, chat).resolve_contradiction(
            claim_id=uuid.uuid4(),
            epistemic_status=EpistemicStatus.CONTRADICTED,
        )

    repository.load_current.assert_not_called()
    repository.revise_claim.assert_not_called()


def test_resolve_contradiction_rejects_noop_revision() -> None:
    repository = Mock()
    chat = Mock()
    current = _snapshot(status=EpistemicStatus.SUPPORTED)
    repository.load_current.return_value = current
    repository.list_evidence.return_value = (_contradiction_ref(),)

    with pytest.raises(ContradictionResolutionError, match="semantic status change"):
        ClaimService(repository, chat).resolve_contradiction(
            claim_id=current.claim_id,
            epistemic_status=EpistemicStatus.SUPPORTED,
        )

    repository.revise_claim.assert_not_called()
    chat.ensure_local_user.assert_not_called()


def test_resolve_contradiction_rejects_non_status_boundary_value() -> None:
    repository = Mock()
    chat = Mock()

    with pytest.raises(TypeError, match="EpistemicStatus"):
        ClaimService(repository, chat).resolve_contradiction(
            claim_id=uuid.uuid4(),
            epistemic_status="supported",  # type: ignore[arg-type]
        )

    repository.load_current.assert_not_called()
