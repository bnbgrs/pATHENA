from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.api.research import ResearchApiService, build_research_api
from athena.jobs.models import JobPriority, JobState


@dataclass(frozen=True)
class _Job:
    job_id: uuid.UUID
    job_type: str
    priority: JobPriority
    state: JobState


class _Research:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.job = _Job(
            job_id=uuid.uuid4(),
            job_type="research.local_exhaustive",
            priority=JobPriority.INTERACTIVE,
            state=JobState.QUEUED,
        )

    def enqueue_local(
        self,
        *,
        query: str,
        priority: JobPriority = JobPriority.NORMAL,
        coverage_target: float = 1.0,
        requested_model_id: str | None = None,
    ) -> _Job:
        self.calls.append(
            {
                "query": query,
                "priority": priority,
                "coverage_target": coverage_target,
                "requested_model_id": requested_model_id,
            }
        )
        return self.job


def test_research_api_delegates_to_existing_durable_orchestrator() -> None:
    research = _Research()
    api = ResearchApiService(research=research)

    response = api.start_local(
        "What changed?",
        priority=JobPriority.INTERACTIVE,
        coverage_target=0.75,
        requested_model_id="local-model",
    )

    assert research.calls == [
        {
            "query": "What changed?",
            "priority": JobPriority.INTERACTIVE,
            "coverage_target": 0.75,
            "requested_model_id": "local-model",
        }
    ]
    assert response.job_id == str(research.job.job_id)
    assert response.job_type == research.job.job_type
    assert response.priority == int(JobPriority.INTERACTIVE)
    assert response.state == JobState.QUEUED.value


def test_research_api_does_not_synthesize_or_rewrite_job_identity() -> None:
    research = _Research()
    api = ResearchApiService(research=research)

    first = api.start_local("A")
    second = api.start_local("B")

    assert first.job_id == second.job_id == str(research.job.job_id)
    assert first.job_type == second.job_type == research.job.job_type


def test_build_research_api_wraps_the_exact_existing_orchestrator() -> None:
    research = _Research()
    api = build_research_api(research=research)

    response = api.start_local("C", requested_model_id="model-c")

    assert research.calls == [
        {
            "query": "C",
            "priority": JobPriority.NORMAL,
            "coverage_target": 1.0,
            "requested_model_id": "model-c",
        }
    ]
    assert response.job_id == str(research.job.job_id)
