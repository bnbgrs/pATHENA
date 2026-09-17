"""Transport-neutral API projection for existing Exhaustive Research orchestration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol

from athena.jobs.models import JobPriority, JobState


class ResearchJobLike(Protocol):
    """Minimal durable job projection returned by the existing Research service."""

    @property
    def job_id(self) -> uuid.UUID: ...

    @property
    def job_type(self) -> str: ...

    @property
    def priority(self) -> JobPriority: ...

    @property
    def state(self) -> JobState: ...


class LocalResearchEnqueuer(Protocol):
    """Existing local Exhaustive Research enqueue boundary."""

    def enqueue_local(
        self,
        *,
        query: str,
        priority: JobPriority = JobPriority.NORMAL,
        coverage_target: float = 1.0,
        requested_model_id: str | None = None,
    ) -> ResearchJobLike: ...


@dataclass(frozen=True, slots=True)
class ResearchJobResponse:
    """Stable API projection of one durable Research job."""

    job_id: str
    job_type: str
    priority: int
    state: str


class ResearchApiService:
    """Expose local Exhaustive Research without bypassing its durable orchestrator."""

    def __init__(self, *, research: LocalResearchEnqueuer) -> None:
        self._research = research

    def start_local(
        self,
        query: str,
        *,
        priority: JobPriority = JobPriority.NORMAL,
        coverage_target: float = 1.0,
        requested_model_id: str | None = None,
    ) -> ResearchJobResponse:
        """Start real local Exhaustive Research and return its durable job identity."""

        job = self._research.enqueue_local(
            query=query,
            priority=priority,
            coverage_target=coverage_target,
            requested_model_id=requested_model_id,
        )
        return ResearchJobResponse(
            job_id=str(job.job_id),
            job_type=job.job_type,
            priority=int(job.priority),
            state=job.state.value,
        )


def build_research_api(*, research: LocalResearchEnqueuer) -> ResearchApiService:
    """Build the canonical adapter around an existing durable Research service."""

    return ResearchApiService(research=research)
