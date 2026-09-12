from __future__ import annotations

import uuid

import pytest

from athena.knowledge.revalidation_job import (
    RevalidationPlanner,
    RevalidationResult,
)
from athena.knowledge.stale_policy import StaleKnowledgePolicy


def _stale_assessment():
    return StaleKnowledgePolicy.assess(now_us=20, valid_to_us=10)


def _current_assessment():
    return StaleKnowledgePolicy.assess(now_us=10, valid_to_us=20)


def test_important_stale_claim_creates_revalidation_job() -> None:
    claim_id = uuid.uuid4()
    claim_revision_id = uuid.uuid4()
    evidence_revision_id = uuid.uuid4()

    job = RevalidationPlanner.create_job(
        claim_id=claim_id,
        claim_revision_id=claim_revision_id,
        baseline_evidence_revision_ids=(evidence_revision_id,),
        stale_assessment=_stale_assessment(),
        important=True,
        requested_at_us=30,
    )

    assert job is not None
    assert job.claim_id == claim_id
    assert job.claim_revision_id == claim_revision_id
    assert job.baseline_evidence_revision_ids == (evidence_revision_id,)
    assert job.requested_at_us == 30


def test_unimportant_or_current_claim_does_not_create_revalidation_job() -> None:
    common = {
        "claim_id": uuid.uuid4(),
        "claim_revision_id": uuid.uuid4(),
        "baseline_evidence_revision_ids": (),
        "requested_at_us": 30,
    }

    assert (
        RevalidationPlanner.create_job(
            **common,
            stale_assessment=_stale_assessment(),
            important=False,
        )
        is None
    )
    assert (
        RevalidationPlanner.create_job(
            **common,
            stale_assessment=_current_assessment(),
            important=True,
        )
        is None
    )


def test_no_new_evidence_keeps_historical_claim() -> None:
    first = uuid.uuid4()
    second = uuid.uuid4()
    job = RevalidationPlanner.create_job(
        claim_id=uuid.uuid4(),
        claim_revision_id=uuid.uuid4(),
        baseline_evidence_revision_ids=(first, second),
        stale_assessment=_stale_assessment(),
        important=True,
        requested_at_us=30,
    )
    assert job is not None

    result = RevalidationPlanner.assess_result(
        job,
        observed_evidence_revision_ids=(second,),
    )

    assert result is RevalidationResult.KEEP_CLAIM_NO_NEW_EVIDENCE


def test_new_evidence_requires_review_without_automatic_claim_rewrite() -> None:
    existing = uuid.uuid4()
    discovered = uuid.uuid4()
    job = RevalidationPlanner.create_job(
        claim_id=uuid.uuid4(),
        claim_revision_id=uuid.uuid4(),
        baseline_evidence_revision_ids=(existing,),
        stale_assessment=_stale_assessment(),
        important=True,
        requested_at_us=30,
    )
    assert job is not None

    result = RevalidationPlanner.assess_result(
        job,
        observed_evidence_revision_ids=(existing, discovered),
    )

    assert result is RevalidationResult.REQUIRE_REVIEW_NEW_EVIDENCE
    assert job.claim_revision_id is not None


def test_duplicate_evidence_revisions_fail_closed() -> None:
    duplicate = uuid.uuid4()

    with pytest.raises(ValueError, match="unique"):
        RevalidationPlanner.create_job(
            claim_id=uuid.uuid4(),
            claim_revision_id=uuid.uuid4(),
            baseline_evidence_revision_ids=(duplicate, duplicate),
            stale_assessment=_stale_assessment(),
            important=True,
            requested_at_us=30,
        )


def test_runtime_boundaries_reject_non_tuple_evidence_and_bool_timestamp() -> None:
    with pytest.raises(TypeError, match="tuple"):
        RevalidationPlanner.create_job(
            claim_id=uuid.uuid4(),
            claim_revision_id=uuid.uuid4(),
            baseline_evidence_revision_ids=[],  # type: ignore[arg-type]
            stale_assessment=_stale_assessment(),
            important=True,
            requested_at_us=30,
        )

    with pytest.raises(ValueError, match="non-negative integer"):
        RevalidationPlanner.create_job(
            claim_id=uuid.uuid4(),
            claim_revision_id=uuid.uuid4(),
            baseline_evidence_revision_ids=(),
            stale_assessment=_stale_assessment(),
            important=True,
            requested_at_us=True,  # type: ignore[arg-type]
        )
