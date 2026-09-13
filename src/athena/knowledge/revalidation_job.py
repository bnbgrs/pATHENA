"""Bounded revalidation planning for important stale claims."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.knowledge.stale_policy import StaleKnowledgeAssessment


class RevalidationResult(str, Enum):
    """Outcome of a revalidation evidence comparison without claim mutation."""

    KEEP_CLAIM_NO_NEW_EVIDENCE = "keep_claim_no_new_evidence"
    REQUIRE_REVIEW_NEW_EVIDENCE = "require_review_new_evidence"


@dataclass(frozen=True, slots=True)
class RevalidationJob:
    """Immutable work request pinned to one historical Claim revision."""

    claim_id: uuid.UUID
    claim_revision_id: uuid.UUID
    baseline_evidence_revision_ids: tuple[uuid.UUID, ...]
    stale_assessment: StaleKnowledgeAssessment
    requested_at_us: int


class RevalidationPlanner:
    """Create and resolve Beta §64 revalidation work without destructive writes."""

    @staticmethod
    def create_job(
        *,
        claim_id: uuid.UUID,
        claim_revision_id: uuid.UUID,
        baseline_evidence_revision_ids: tuple[uuid.UUID, ...],
        stale_assessment: StaleKnowledgeAssessment,
        important: bool,
        requested_at_us: int,
    ) -> RevalidationJob | None:
        """Create a job only for important claims with an active stale signal."""

        RevalidationPlanner._require_uuid("claim_id", claim_id)
        RevalidationPlanner._require_uuid("claim_revision_id", claim_revision_id)
        evidence = RevalidationPlanner._require_evidence_revisions(
            baseline_evidence_revision_ids
        )
        if not isinstance(stale_assessment, StaleKnowledgeAssessment):
            raise TypeError("stale_assessment must be a StaleKnowledgeAssessment.")
        if type(important) is not bool:
            raise TypeError("important must be a bool.")
        RevalidationPlanner._require_non_negative_int("requested_at_us", requested_at_us)

        if not important or not stale_assessment.requires_revalidation:
            return None

        return RevalidationJob(
            claim_id=claim_id,
            claim_revision_id=claim_revision_id,
            baseline_evidence_revision_ids=evidence,
            stale_assessment=stale_assessment,
            requested_at_us=requested_at_us,
        )

    @staticmethod
    def assess_result(
        job: RevalidationJob,
        *,
        observed_evidence_revision_ids: tuple[uuid.UUID, ...],
    ) -> RevalidationResult:
        """Require review only when revalidation discovered genuinely new evidence.

        Absence of new evidence keeps the historical Claim intact.  This boundary never
        deletes, retracts, supersedes, or otherwise mutates the Claim itself.
        """

        if not isinstance(job, RevalidationJob):
            raise TypeError("job must be a RevalidationJob.")
        observed = RevalidationPlanner._require_evidence_revisions(
            observed_evidence_revision_ids
        )
        baseline = set(job.baseline_evidence_revision_ids)
        if any(revision_id not in baseline for revision_id in observed):
            return RevalidationResult.REQUIRE_REVIEW_NEW_EVIDENCE
        return RevalidationResult.KEEP_CLAIM_NO_NEW_EVIDENCE

    @staticmethod
    def _require_uuid(name: str, value: object) -> None:
        if not isinstance(value, uuid.UUID):
            raise TypeError(f"{name} must be a UUID.")

    @staticmethod
    def _require_non_negative_int(name: str, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer timestamp.")

    @staticmethod
    def _require_evidence_revisions(
        value: object,
    ) -> tuple[uuid.UUID, ...]:
        if not isinstance(value, tuple):
            raise TypeError("evidence revision ids must be a tuple.")
        seen: set[uuid.UUID] = set()
        result: list[uuid.UUID] = []
        for revision_id in value:
            if not isinstance(revision_id, uuid.UUID):
                raise TypeError("every evidence revision id must be a UUID.")
            if revision_id in seen:
                raise ValueError("evidence revision ids must be unique.")
            seen.add(revision_id)
            result.append(revision_id)
        return tuple(result)
