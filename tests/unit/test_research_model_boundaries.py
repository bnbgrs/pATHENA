from __future__ import annotations

import uuid

import pytest

from athena.research.models import (
    ResearchCandidateEligibility,
    ResearchCandidateRecord,
    ResearchCandidateSetRecord,
    ResearchCandidateSetState,
    ResearchCoverage,
    ResearchSynthesisInputKind,
    ResearchSynthesisWorkInputRecord,
)


def test_research_candidate_set_requires_consistent_counts() -> None:
    with pytest.raises(ValueError, match="counts are internally inconsistent"):
        ResearchCandidateSetRecord(
            candidate_set_id=uuid.uuid4(),
            scope_id=uuid.uuid4(),
            snapshot_commit_seq=0,
            state=ResearchCandidateSetState.FROZEN,
            candidate_total=3,
            eligible_count=2,
            excluded_count=0,
            created_at_us=1,
            frozen_at_us=1,
        )


def test_research_duplicate_candidate_requires_distinct_duplicate_reference() -> None:
    candidate_id = uuid.uuid4()
    with pytest.raises(ValueError, match="cannot duplicate itself"):
        ResearchCandidateRecord(
            candidate_id=candidate_id,
            candidate_set_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            ordinal=0,
            content_sha256=b"a" * 32,
            eligibility=ResearchCandidateEligibility.EXCLUDED_DUPLICATE,
            duplicate_of_candidate_id=candidate_id,
            created_at_us=0,
        )


def test_research_coverage_requires_terminal_counts_to_match_processed() -> None:
    with pytest.raises(ValueError, match="terminal counts"):
        ResearchCoverage(
            candidate_total=4,
            processed_count=2,
            successful_count=1,
            irrelevant_count=0,
            failed_count=0,
            unavailable_count=0,
            excluded_count=1,
            eligible_count=3,
            coverage_ratio=0.5,
        )


def test_research_synthesis_input_requires_matching_tagged_reference() -> None:
    with pytest.raises(ValueError, match="tagged reference"):
        ResearchSynthesisWorkInputRecord(
            work_item_id=uuid.uuid4(),
            ordinal=0,
            input_kind=ResearchSynthesisInputKind.SOURCE_ANALYSIS_ARTIFACT,
            source_analysis_artifact_id=None,
            research_synthesis_artifact_id=uuid.uuid4(),
        )
