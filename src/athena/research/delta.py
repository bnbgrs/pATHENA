"""Explicit-source Delta Research composition.

Delta Research never mutates an existing frozen ResearchScope. Callers identify the
newly relevant, already-captured Sources and enqueue a new exhaustive Research job
whose scope is restricted to those canonical Source identities.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from athena.jobs.models import JobPriority, JobRecord
from athena.research.models import ResearchMode
from athena.research.service import ResearchConfigurationError, ResearchService
from athena.source.analysis_service import DEFAULT_MAX_HIERARCHY_DEPTH


def enqueue_delta(
    research: ResearchService,
    *,
    query: str,
    explicit_source_ids: Sequence[uuid.UUID],
    priority: JobPriority = JobPriority.NORMAL,
    coverage_target: float = 1.0,
    requested_model_id: str | None = None,
    context_limit: int | None = None,
    output_reserve: int | None = None,
    safety_margin: int | None = None,
    max_hierarchy_depth: int = DEFAULT_MAX_HIERARCHY_DEPTH,
) -> JobRecord:
    """Enqueue a new Delta Research job over explicit canonical Sources only."""
    if (
        isinstance(explicit_source_ids, (str, bytes, bytearray))
        or not isinstance(explicit_source_ids, Sequence)
        or any(not isinstance(item, uuid.UUID) for item in explicit_source_ids)
    ):
        raise ResearchConfigurationError(
            "Delta Research explicit_source_ids must contain UUID values only."
        )
    normalized_sources = tuple(
        sorted(set(explicit_source_ids), key=lambda item: item.bytes)
    )
    if not normalized_sources:
        raise ResearchConfigurationError(
            "Delta Research requires at least one captured Source."
        )

    return research._enqueue(
        mode=ResearchMode.DELTA,
        query=query,
        priority=priority,
        domains=(),
        project_ids=(),
        source_types=(),
        explicit_source_ids=normalized_sources,
        time_start_us=None,
        time_end_us=None,
        coverage_target=coverage_target,
        requested_model_id=requested_model_id,
        context_limit=context_limit,
        output_reserve=output_reserve,
        safety_margin=safety_margin,
        max_hierarchy_depth=max_hierarchy_depth,
    )
