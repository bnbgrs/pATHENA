from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.models import JobState
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.research.models import ResearchWorkState


@dataclass
class _ResearchProvider:
    calls: list[tuple[str, tuple[ModelChatMessage, ...]]] = field(default_factory=list)

    @property
    def provider_id(self) -> str:
        return "fake"

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (
            ModelInfo(
                provider="fake",
                backend_model_id="research-primary",
                display_name="Research Primary",
                model_type="llm",
                context_capacity=2_000,
                loaded_context_length=2_000,
                quantization="Q4",
                loaded=True,
                vision=False,
                trained_for_tool_use=False,
            ),
        )

    def generate_structured(
        self,
        *,
        model_id: str,
        messages: tuple[ModelChatMessage, ...],
        schema_id: str,
        json_schema,
        max_output_tokens: int | None = None,
    ):
        del json_schema, max_output_tokens
        assert model_id == "research-primary"
        self.calls.append((schema_id, messages))
        text = "\n".join(message.content for message in messages)
        if "map" in schema_id:
            marker = next(
                line for line in text.splitlines() if line.startswith("resume-source-")
            )
            return {
                "relevant": True,
                "summary": f"map summary {marker}",
                "findings": [f"finding {marker}"],
                "contradictions": [],
                "uncertainty": "",
            }
        return {
            "summary": "synthesis summary",
            "findings": ["synthesis finding"],
            "contradictions": [],
            "uncertainty": "",
        }

    def stream_chat(self, *, model_id: str, messages):
        del model_id, messages
        yield "unused"


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start()
    app.source_analysis_service.provider = _ResearchProvider()
    return app


def _capture_and_preprocess(app: AthenaApplication, path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="")
    source = app.sources.capture_file(path).source
    child = app.source_processing.enqueue(source.source_id)
    completed = app.source_processing.run_to_completion(
        child.job_id,
        worker_id="research-resume-preprocess",
    )
    assert completed.done is True
    return source


def _acquire_parent(app: AthenaApplication, job_id, *, worker: str):
    current = app.jobs.get(job_id)
    if current.state is JobState.WAITING:
        app.jobs.wake(job_id)
    queued = app.jobs.get(job_id)
    assert queued.state is JobState.QUEUED
    leased = app.jobs.acquire(job_id, worker_id=worker, lease_seconds=120)
    assert leased.lease_token is not None
    return leased.lease_token


def _advance_until_wait(app: AthenaApplication, job_id, *, worker: str):
    lease_token = _acquire_parent(app, job_id, worker=worker)
    for _ in range(50):
        result = app.research_worker.step(
            job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        if result.waiting or result.done:
            return result
    raise AssertionError("Research parent did not reach a wait/terminal boundary.")


def _run_queued_children(app: AthenaApplication, job_id) -> None:
    scope = app.research.initialize(job_id)
    for work in app.research_repository.list_work_items(scope.scope_id):
        if work.source_processing_job_id is not None:
            child = app.jobs.get(work.source_processing_job_id)
            if child.state is JobState.QUEUED:
                result = app.source_processing.run_to_completion(
                    child.job_id,
                    worker_id="research-resume-source-child",
                )
                assert result.done is True
        refreshed = app.research_repository.get_work_item(work.work_item_id)
        if refreshed.source_analysis_job_id is not None:
            child = app.jobs.get(refreshed.source_analysis_job_id)
            if child.state is JobState.QUEUED:
                result = app.source_analysis.run_to_completion(
                    child.job_id,
                    worker_id="research-resume-analysis-child",
                )
                assert result.done is True


def _successful_finding_snapshots(app: AthenaApplication, job_id):
    scope = app.research.initialize(job_id)
    successful = tuple(
        item
        for item in app.research_repository.list_work_items(scope.scope_id)
        if item.state is ResearchWorkState.SUCCESSFUL
    )
    repository = app.source_analysis_service.repository
    snapshots = []
    for item in successful:
        assert item.source_analysis_job_id is not None
        analysis = repository.get_analysis_for_job(item.source_analysis_job_id)
        assert analysis is not None
        assert analysis.final_artifact_id is not None
        artifact = repository.get_artifact(analysis.final_artifact_id)
        content = json.loads(artifact.content_json)
        snapshots.append(
            (
                item.work_item_id,
                item.source_analysis_job_id,
                artifact.artifact_id,
                artifact.content_hash,
                tuple(content["findings"]),
            )
        )
    return tuple(sorted(snapshots, key=lambda item: item[0].bytes))


def test_exhaustive_research_restart_at_sixty_percent_preserves_findings_without_duplicates(
    tmp_path: Path,
) -> None:
    runtime = tmp_path / "runtime"
    app = _app(runtime)
    sources = tuple(
        _capture_and_preprocess(
            app,
            tmp_path / f"source-{ordinal}.txt",
            f"resume-source-{ordinal}\nrelevant evidence {ordinal}",
        )
        for ordinal in range(5)
    )
    job = app.research.enqueue_local(
        query="Resume five-source research without duplicate findings.",
        explicit_source_ids=tuple(source.source_id for source in sources),
    )

    waiting = _advance_until_wait(app, job.job_id, worker="research-resume-parent-0")
    assert waiting.completed_stage == "waiting_source_analysis"

    for ordinal in range(3):
        _run_queued_children(app, job.job_id)
        lease_token = _acquire_parent(
            app,
            job.job_id,
            worker=f"research-resume-classify-{ordinal}",
        )
        classified = app.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        assert classified.completed_stage == "source_analysis_classified"
        next_wait = app.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        assert next_wait.waiting is True
        assert next_wait.completed_stage == "waiting_source_analysis"

    before_restart = _successful_finding_snapshots(app, job.job_id)
    assert len(before_restart) == 3
    assert app.research.coverage(job.job_id).coverage_ratio == 0.6
    app.stop()

    resumed = _app(runtime)
    after_restart = _successful_finding_snapshots(resumed, job.job_id)
    assert after_restart == before_restart
    assert resumed.research.coverage(job.job_id).coverage_ratio == 0.6

    for ordinal in range(3, 5):
        _run_queued_children(resumed, job.job_id)
        lease_token = _acquire_parent(
            resumed,
            job.job_id,
            worker=f"research-resumed-classify-{ordinal}",
        )
        classified = resumed.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        assert classified.completed_stage == "source_analysis_classified"
        next_result = resumed.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        if ordinal == 3:
            assert next_result.waiting is True
            assert next_result.completed_stage == "waiting_source_analysis"
        else:
            assert next_result.waiting is True
            assert next_result.completed_stage == "awaiting_synthesis"

    final_snapshots = _successful_finding_snapshots(resumed, job.job_id)
    assert len(final_snapshots) == 5
    final_by_work_item = {item[0]: item for item in final_snapshots}
    assert all(final_by_work_item[item[0]] == item for item in before_restart)
    assert len({item[0] for item in final_snapshots}) == 5
    assert len({item[1] for item in final_snapshots}) == 5
    assert len({item[2] for item in final_snapshots}) == 5
    assert len({item[4] for item in final_snapshots}) == 5
    assert resumed.research.coverage(job.job_id).coverage_ratio == 1.0
    resumed.stop()
