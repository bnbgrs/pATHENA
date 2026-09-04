"""Compose source-internal Research coverage from persisted domain records."""

from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from athena.research.errors import ResearchStateError
from athena.research.models import (
    ResearchCandidateEligibility,
    ResearchCandidateRecord,
    ResearchWorkItemRecord,
    ResearchWorkState,
)
from athena.research.source_coverage import SourceCoverage

SOURCE_COVERAGE_RESULT_KEY = "source_coverage"


def source_coverages_from_records(
    candidates: Iterable[ResearchCandidateRecord],
    work_items: Iterable[ResearchWorkItemRecord],
) -> tuple[SourceCoverage, ...]:
    """Derive truthful per-source coverage from candidate/work-record identity."""

    candidate_by_id: dict[uuid.UUID, ResearchCandidateRecord] = {}
    source_candidates: dict[uuid.UUID, list[ResearchCandidateRecord]] = defaultdict(list)
    for candidate in candidates:
        if candidate.candidate_id in candidate_by_id:
            raise ResearchStateError("duplicate Research candidate identity in coverage input.")
        candidate_by_id[candidate.candidate_id] = candidate
        source_candidates[candidate.source_id].append(candidate)

    state_by_candidate: dict[uuid.UUID, ResearchWorkState] = {}
    for work_item in work_items:
        work_candidate = candidate_by_id.get(work_item.candidate_id)
        if work_candidate is None:
            raise ResearchStateError("Research work item references an unknown candidate.")
        if work_item.candidate_id in state_by_candidate:
            raise ResearchStateError("multiple Research work items reference one candidate.")
        state_by_candidate[work_item.candidate_id] = work_item.state

    result: list[SourceCoverage] = []
    for source_id in sorted(source_candidates, key=str):
        source_records = source_candidates[source_id]
        excluded_count = sum(
            candidate.eligibility is not ResearchCandidateEligibility.ELIGIBLE
            for candidate in source_records
        )
        counts = {state: 0 for state in ResearchWorkState}
        for candidate in source_records:
            if candidate.eligibility is not ResearchCandidateEligibility.ELIGIBLE:
                continue
            state = state_by_candidate.get(candidate.candidate_id, ResearchWorkState.PENDING)
            counts[state] += 1

        result.append(
            SourceCoverage(
                source_id=source_id,
                unit_total=len(source_records),
                successful_count=counts[ResearchWorkState.SUCCESSFUL],
                irrelevant_count=counts[ResearchWorkState.IRRELEVANT],
                failed_count=counts[ResearchWorkState.FAILED],
                unavailable_count=counts[ResearchWorkState.UNAVAILABLE],
                excluded_count=excluded_count,
            )
        )

    return tuple(result)


def source_coverage_result_payloads_from_records(
    candidates: Iterable[ResearchCandidateRecord],
    work_items: Iterable[ResearchWorkItemRecord],
) -> tuple[dict[str, int | float | str], ...]:
    """Return deterministic Core-owned payloads ready for ResearchResult storage."""

    return tuple(
        coverage.result_payload()
        for coverage in source_coverages_from_records(candidates, work_items)
    )


def research_result_content_with_source_coverage(
    semantic_content: Mapping[str, Any],
    candidates: Iterable[ResearchCandidateRecord],
    work_items: Iterable[ResearchWorkItemRecord],
) -> dict[str, Any]:
    """Add the reserved source-coverage field to ResearchResult semantic content."""

    if SOURCE_COVERAGE_RESULT_KEY in semantic_content:
        raise ResearchStateError(
            "ResearchResult semantic content contains Core-owned source coverage."
        )
    payload = dict(semantic_content)
    payload[SOURCE_COVERAGE_RESULT_KEY] = list(
        source_coverage_result_payloads_from_records(candidates, work_items)
    )
    return payload
