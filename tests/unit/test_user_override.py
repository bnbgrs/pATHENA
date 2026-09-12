from __future__ import annotations

import uuid

import pytest

from athena.knowledge.user_override import (
    AutomaticUpdateDisposition,
    assess_automatic_update_after_user_override,
)


def test_automatic_update_without_new_evidence_is_rejected() -> None:
    user_revision_id = uuid.uuid4()
    evidence_a = uuid.uuid4()
    evidence_b = uuid.uuid4()

    assessment = assess_automatic_update_after_user_override(
        user_revision_id=user_revision_id,
        prior_evidence_revision_ids=(evidence_a, evidence_b),
        proposed_evidence_revision_ids=(evidence_b, evidence_a),
    )

    assert assessment.user_revision_id == user_revision_id
    assert assessment.disposition is AutomaticUpdateDisposition.REJECT_NO_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == ()


def test_automatic_update_with_new_evidence_requires_semantic_review() -> None:
    user_revision_id = uuid.uuid4()
    old_evidence = uuid.uuid4()
    new_evidence_a = uuid.uuid4()
    new_evidence_b = uuid.uuid4()

    assessment = assess_automatic_update_after_user_override(
        user_revision_id=user_revision_id,
        prior_evidence_revision_ids=(old_evidence,),
        proposed_evidence_revision_ids=(old_evidence, new_evidence_a, new_evidence_b),
    )

    assert assessment.disposition is AutomaticUpdateDisposition.REQUIRE_REVIEW_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == (new_evidence_a, new_evidence_b)


def test_automatic_update_with_only_removed_evidence_is_rejected() -> None:
    user_revision_id = uuid.uuid4()
    evidence_a = uuid.uuid4()
    evidence_b = uuid.uuid4()

    assessment = assess_automatic_update_after_user_override(
        user_revision_id=user_revision_id,
        prior_evidence_revision_ids=(evidence_a, evidence_b),
        proposed_evidence_revision_ids=(evidence_b,),
    )

    assert assessment.disposition is AutomaticUpdateDisposition.REJECT_NO_NEW_EVIDENCE
    assert assessment.new_evidence_revision_ids == ()


def test_duplicate_evidence_revision_ids_fail_closed() -> None:
    evidence_id = uuid.uuid4()

    with pytest.raises(ValueError, match="duplicate revision ids"):
        assess_automatic_update_after_user_override(
            user_revision_id=uuid.uuid4(),
            prior_evidence_revision_ids=(),
            proposed_evidence_revision_ids=(evidence_id, evidence_id),
        )


def test_non_uuid_revision_ids_fail_closed() -> None:
    with pytest.raises(TypeError, match="only UUID revision ids"):
        assess_automatic_update_after_user_override(
            user_revision_id=uuid.uuid4(),
            prior_evidence_revision_ids=(),
            proposed_evidence_revision_ids=("not-a-revision",),  # type: ignore[arg-type]
        )


def test_non_tuple_evidence_collection_fails_closed() -> None:
    with pytest.raises(TypeError, match="must be a tuple"):
        assess_automatic_update_after_user_override(
            user_revision_id=uuid.uuid4(),
            prior_evidence_revision_ids=(),
            proposed_evidence_revision_ids=[],  # type: ignore[arg-type]
        )
