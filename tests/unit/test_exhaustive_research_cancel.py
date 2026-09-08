from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.models import JobState
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.research.models import (
    ResearchScopeState,
    ResearchSynthesisStage,
    ResearchSynthesisWorkState,
)
from athena.research.synthesis_service import ResearchSynthesisService


@dataclass
class _CancelProvider:
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
                context_capacity=4_000,
                loaded_context_length=4_000,
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
        if schema_id.startswith("athena_research_synthesis_"):
            refs = sorted(
                set(
                    re.findall(
                        r"INPUT-\d{3}-(?:FINDING|CONTRADICTION)-\d{3}",
                        text,
                    )
                    + re.findall(
                        r"(INPUT-\d{3}) kind=source_analysis_artifact",
                        text,
                    )
                )
            )
            return {
                "summary": "confirmed partial synthesis",
                "findings": [
                    {
                        "text": "confirmed partial finding",
                        "evidence_refs": refs,
                    }
                ],
                "contradictions": [],
                "uncertainty": "partial by explicit cancellation",
            }
        if "map" in schema_id:
            return {
                "relevant": True,
                "summary": "map summary",
                "findings": ["supported source finding"],
                "contradictions": [],
                "uncertainty": "",
            }
        return {
            "summary": "source synthesis summary",
            "findings": ["supported source finding"],
            "contradictions": [],
            "uncertainty": "",
        }

    def stream_chat(self, *, model_id: str, messages):
        del model_id, messages
        yield "unused"


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start()
    app.source_analysis_service.provider = _CancelProvider()
    return app


def _capture(app: AthenaApplication, path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")
    app.sources.capture_file(path)


def _acquire_parent(app: AthenaApplication, job_id):
    current = app.jobs.get(job_id)
    if current.state is JobState.WAITING:
        app.jobs.wake(job_id)
    leased = app.jobs.acquire(
        job_id,
        worker_id="research-cancel-parent",
        lease_seconds=120,
    )
    assert leased.lease_token is not None
    return leased.lease_token


def _run_queued_children(app: AthenaApplication, job_id) -> None:
    scope = app.research.initialize(job_id)
    for work in app.research_repository.list_work_items(scope.scope_id):
        if work.source_processing_job_id is not None:
            child = app.jobs.get(work.source_processing_job_id)
            if child.state is JobState.QUEUED:
                assert app.source_processing.run_to_completion(
                    child.job_id,
                    worker_id="research-cancel-source-child",
                ).done
        refreshed = app.research_repository.get_work_item(work.work_item_id)
        if refreshed.source_analysis_job_id is not None:
            child = app.jobs.get(refreshed.source_analysis_job_id)
            if child.state is JobState.QUEUED:
                assert app.source_analysis.run_to_completion(
                    child.job_id,
                    worker_id="research-cancel-analysis-child",
                ).done


def _drive_to_synthesis(app: AthenaApplication, job_id) -> None:
    for _ in range(100):
        lease_token = _acquire_parent(app, job_id)
        for _ in range(50):
            result = app.research_worker.step(
                job_id,
                lease_token=lease_token,
                extend_seconds=120,
            )
            if result.waiting or result.done:
                break
        if result.completed_stage == "awaiting_synthesis":
            return
        _run_queued_children(app, job_id)
    raise AssertionError("Research did not reach synthesis.")


def test_cancel_during_reduce_preserves_confirmed_partial_without_complete_result(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        for index in range(4):
            _capture(
                app,
                tmp_path / f"cancel-source-{index}.txt",
                f"distinct cancel evidence {index}",
            )
        job = app.research.enqueue_local(query="Aggregate all cancel evidence.")
        _drive_to_synthesis(app, job.job_id)
        scope = app.research.initialize(job.job_id)
        lease_token = _acquire_parent(app, job.job_id)
        synthesis = ResearchSynthesisService(
            repository=app.research_repository,
            source_analysis=app.source_analysis_service,
        )

        planned_final = synthesis.plan_next_synthesis(
            scope,
            parent_job_id=job.job_id,
            lease_token=lease_token,
        )
        reduce_children = synthesis.split_synthesis_work(
            scope,
            planned_final,
            parent_job_id=job.job_id,
            lease_token=lease_token,
        )
        assert len(reduce_children) >= 2
        assert all(
            child.stage is ResearchSynthesisStage.REDUCE
            for child in reduce_children
        )

        first_reduce = reduce_children[0]
        partial_artifact = synthesis.execute_call(
            scope=scope,
            parent_job_id=job.job_id,
            lease_token=lease_token,
            prepared=synthesis.prepare_call(scope, first_reduce),
            extend_seconds=120,
        )
        persisted_before_cancel = (
            app.research_repository.synthesis_artifact_for_work_item(
                first_reduce.work_item_id
            )
        )
        assert persisted_before_cancel == partial_artifact
        assert (
            app.research_repository.get_synthesis_work_item(
                first_reduce.work_item_id
            ).state
            is ResearchSynthesisWorkState.COMPLETED
        )

        requested = app.jobs.request_cancel(job.job_id)
        assert requested.state is JobState.CANCEL_REQUESTED
        cancelled = app.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )

        assert cancelled.done is True
        assert cancelled.completed_stage == "cancel"
        assert cancelled.job.state is JobState.CANCELLED
        assert cancelled.scope is not None
        assert cancelled.scope.state is ResearchScopeState.PARTIAL
        assert (
            app.research_repository.synthesis_artifact_for_work_item(
                first_reduce.work_item_id
            )
            == partial_artifact
        )
        assert (
            app.research_repository.get_synthesis_work_item(
                first_reduce.work_item_id
            ).state
            is ResearchSynthesisWorkState.COMPLETED
        )
        assert not any(
            item.stage is ResearchSynthesisStage.FINAL
            and item.state is ResearchSynthesisWorkState.COMPLETED
            for item in app.research_repository.list_synthesis_work_items(
                scope.scope_id
            )
        )
        result_count = app.database.connection.execute(
            "SELECT COUNT(*) FROM research_results WHERE scope_id = ?",
            (scope.scope_id.bytes,),
        ).fetchone()[0]
        assert result_count == 0
    finally:
        app.stop()
