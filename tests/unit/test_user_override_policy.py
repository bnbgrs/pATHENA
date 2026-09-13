from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import EvidenceRole
from athena.knowledge.user_override_policy import (
    AutomaticRevisionDecision,
    UserOverridePolicy,
    UserOverrideSnapshot,
)


def _snapshot(*evidence: uuid.UUID) -> UserOverrideSnapshot:
    return UserOverrideSnapshot.create(
        entity_id=uuid.uuid4(),
        correction_revision_id=uuid.uuid4(),
        evidence_revision_ids=evidence,
    )


def test_automatic_revision_without_new_evidence_is_blocked() -> None:
    evidence = uuid.uuid4()
    assessment = UserOverridePolicy.assess_automatic_revision(
        _snapshot(evidence),
        incoming_evidence_revision_ids=(evidence,),
    )

    assert assessment.decision is AutomaticRevisionDecision.BLOCK_NO_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == frozenset()
    assert assessment.automatic_commit_allowed is False
    assert assessment.requires_semantic_review is False


def test_empty_evidence_cannot_reverse_user_correction() -> None:
    assessment = UserOverridePolicy.assess_automatic_revision(
        _snapshot(),
        incoming_evidence_revision_ids=(),
    )

    assert assessment.decision is AutomaticRevisionDecision.BLOCK_NO_NEW_EVIDENCE
    assert assessment.automatic_commit_allowed is False


def test_new_evidence_routes_to_review_but_never_silent_commit() -> None:
    old_evidence = uuid.uuid4()
    new_evidence = uuid.uuid4()
    assessment = UserOverridePolicy.assess_automatic_revision(
        _snapshot(old_evidence),
        incoming_evidence_revision_ids=(old_evidence, new_evidence),
    )

    assert assessment.decision is AutomaticRevisionDecision.REQUIRE_REVIEW_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == frozenset({new_evidence})
    assert assessment.requires_semantic_review is True
    assert assessment.automatic_commit_allowed is False


def test_duplicate_old_evidence_does_not_count_as_new() -> None:
    evidence = uuid.uuid4()
    assessment = UserOverridePolicy.assess_automatic_revision(
        _snapshot(evidence),
        incoming_evidence_revision_ids=(evidence, evidence),
    )

    assert assessment.decision is AutomaticRevisionDecision.BLOCK_NO_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == frozenset()


def test_snapshot_and_assessment_reject_non_uuid_evidence() -> None:
    with pytest.raises(TypeError, match="only UUID"):
        UserOverrideSnapshot.create(
            entity_id=uuid.uuid4(),
            correction_revision_id=uuid.uuid4(),
            evidence_revision_ids=("not-a-uuid",),  # type: ignore[arg-type]
        )

    with pytest.raises(TypeError, match="only UUID"):
        UserOverridePolicy.assess_automatic_revision(
            _snapshot(),
            incoming_evidence_revision_ids=("not-a-uuid",),  # type: ignore[arg-type]
        )


def test_contradicting_external_evidence_remains_visible_without_delete_authority() -> None:
    contradiction = uuid.uuid4()
    support = uuid.uuid4()
    assessment = UserOverridePolicy.assess_source_conflict(
        _snapshot(),
        evidence=(
            (support, EvidenceRole.SUPPORTS),
            (contradiction, EvidenceRole.CONTRADICTS),
        ),
    )

    assert assessment.contradicting_evidence_revision_ids == frozenset({contradiction})
    assert assessment.conflict_visible is True
    assert assessment.source_deletion_allowed is False


def test_noncontradictory_evidence_does_not_fabricate_visible_conflict() -> None:
    assessment = UserOverridePolicy.assess_source_conflict(
        _snapshot(),
        evidence=((uuid.uuid4(), EvidenceRole.MENTIONS),),
    )

    assert assessment.contradicting_evidence_revision_ids == frozenset()
    assert assessment.conflict_visible is False
    assert assessment.source_deletion_allowed is False


def test_duplicate_contradiction_revision_is_deduplicated_without_hiding_conflict() -> None:
    contradiction = uuid.uuid4()
    assessment = UserOverridePolicy.assess_source_conflict(
        _snapshot(),
        evidence=(
            (contradiction, EvidenceRole.CONTRADICTS),
            (contradiction, EvidenceRole.CONTRADICTS),
        ),
    )

    assert assessment.contradicting_evidence_revision_ids == frozenset({contradiction})
    assert assessment.conflict_visible is True


@pytest.mark.parametrize(
    "bad_evidence",
    [
        (("not-a-uuid", EvidenceRole.CONTRADICTS),),
        ((uuid.UUID(int=1), "contradicts"),),
        ((uuid.UUID(int=1),),),
    ],
)
def test_source_conflict_rejects_malformed_runtime_evidence(
    bad_evidence: object,
) -> None:
    with pytest.raises(TypeError):
        UserOverridePolicy.assess_source_conflict(
            _snapshot(),
            evidence=bad_evidence,  # type: ignore[arg-type]
        )
