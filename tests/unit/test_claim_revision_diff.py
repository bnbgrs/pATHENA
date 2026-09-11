from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import ClaimDraft, ClaimKind, ClaimRevision, EpistemicStatus
from athena.knowledge.revision_diff import diff_claim_revisions


def _revision(
    *,
    claim_id: uuid.UUID,
    revision_no: int,
    statement: str = "Alpha",
    status: EpistemicStatus = EpistemicStatus.ASSERTED,
    subject_entity_id: uuid.UUID | None = None,
    valid_from_us: int | None = None,
) -> ClaimRevision:
    return ClaimRevision(
        claim_id=claim_id,
        revision_id=uuid.uuid4(),
        revision_no=revision_no,
        created_at_us=revision_no,
        created_by_actor_id=uuid.uuid4(),
        provenance_id=uuid.uuid4(),
        payload=ClaimDraft(
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
            statement=statement,
            epistemic_status=status,
            subject_entity_id=subject_entity_id,
            valid_from_us=valid_from_us,
        ),
    )


def test_diff_reports_only_changed_semantic_fields_in_stable_order() -> None:
    claim_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    before = _revision(claim_id=claim_id, revision_no=1)
    after = _revision(
        claim_id=claim_id,
        revision_no=2,
        statement="Beta",
        status=EpistemicStatus.SUPPORTED,
        subject_entity_id=subject_id,
        valid_from_us=42,
    )

    result = diff_claim_revisions(before, after)

    assert result.claim_id == claim_id
    assert result.from_revision_id == before.revision_id
    assert result.to_revision_id == after.revision_id
    assert tuple(change.field for change in result.changes) == (
        "statement",
        "epistemic_status",
        "subject_entity_id",
        "valid_from_us",
    )
    assert result.changes[1].before == "asserted"
    assert result.changes[1].after == "supported"
    assert result.changes[2].before is None
    assert result.changes[2].after == str(subject_id)


def test_diff_is_empty_when_payload_is_unchanged() -> None:
    claim_id = uuid.uuid4()
    before = _revision(claim_id=claim_id, revision_no=1)
    after = _revision(claim_id=claim_id, revision_no=2)

    assert diff_claim_revisions(before, after).changes == ()


def test_diff_allows_non_adjacent_forward_history_comparison() -> None:
    claim_id = uuid.uuid4()
    before = _revision(claim_id=claim_id, revision_no=1, statement="Alpha")
    after = _revision(claim_id=claim_id, revision_no=4, statement="Delta")

    result = diff_claim_revisions(before, after)

    assert tuple(change.field for change in result.changes) == ("statement",)
    assert result.changes[0].before == "Alpha"
    assert result.changes[0].after == "Delta"


def test_diff_rejects_revisions_from_different_claims() -> None:
    with pytest.raises(ValueError, match="different Claims"):
        diff_claim_revisions(
            _revision(claim_id=uuid.uuid4(), revision_no=1),
            _revision(claim_id=uuid.uuid4(), revision_no=2),
        )


def test_diff_rejects_same_or_backward_revision_order() -> None:
    claim_id = uuid.uuid4()
    later = _revision(claim_id=claim_id, revision_no=2)
    same_number = _revision(claim_id=claim_id, revision_no=2)
    earlier = _revision(claim_id=claim_id, revision_no=1)

    with pytest.raises(ValueError, match="later Claim revision"):
        diff_claim_revisions(later, same_number)
    with pytest.raises(ValueError, match="later Claim revision"):
        diff_claim_revisions(later, earlier)
