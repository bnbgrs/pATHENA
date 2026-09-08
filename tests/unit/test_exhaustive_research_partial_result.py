from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.models import JobState
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.research.models import ResearchScopeState, ResearchSynthesisStage
from athena.research.partial_result_service import ResearchPartialResultService
from athena.research.synthesis_service import ResearchSynthesisService


@dataclass
class _Provider:
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
                        r"INPUT-\d{3}-(?:FINDING|CONTRADICTION)-\d{3}", text
                    )
                    + re.findall(
                        r"(INPUT-\d{3}) kind=source_analysis_artifact", text
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
    app.source_analysis_service.provider = _Provider()
    return app


def _acquire_parent(app: AthenaApplication, job_id):
    current = app.jobs.get(job_id)
    if current.state is JobState.WAITING:
        app.jobs.wake(job_id)
    leased = app.jobs.acquire(
        job_id,
        worker_id="research-partial-parent",
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
                    worker_id="research-partial-source-child",
                ).done
        refreshed = app.research_repository.get_work_item(work.work_item_id)
        if refreshed.source_analysis_job_id is not None:
            child = app.jobs.get(refreshed.source_analysis_job_id)
            if child.state is JobState.QUEUED:
                assert app.source_analysis.run_to_completion(
                    child.job_id,
                    worker_id="research-partial-analysis-child",
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


def test_cancelled_research_can_explicitly_persist_partial_report(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime")
    try:
        for index in range(4):
            path = tmp_path / f"partial-source-{index}.txt"
            path.write_text(f"distinct partial evidence {index}", encoding="utf-8")
            app.sources.capture_file(path)

        job = app.research.enqueue_local(query="Aggregate partial evidence.")
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
        assert reduce_children
        assert reduce_children[0].stage is ResearchSynthesisStage.REDUCE
        confirmed = synthesis.execute_call(
            scope=scope,
            parent_job_id=job.job_id,
            lease_token=lease_token,
            prepared=synthesis.prepare_call(scope, reduce_children[0]),
            extend_seconds=120,
        )

        app.jobs.request_cancel(job.job_id)
        cancelled = app.research_worker.step(
            job.job_id,
            lease_token=lease_token,
            extend_seconds=120,
        )
        assert cancelled.job.state is JobState.CANCELLED
        assert cancelled.scope is not None
        assert cancelled.scope.state is ResearchScopeState.PARTIAL
        assert app.research_repository.get_result_for_scope(scope.scope_id) is None

        partials = ResearchPartialResultService(
            repository=app.research_repository,
            jobs=app.jobs,
        )
        result = partials.create(job.job_id)
        payload = json.loads(result.content_json)

        assert result.final_artifact_id is None
        assert payload["partial"] is True
        assert payload["result_status"] == "partial"
        assert payload["completion_reason"] == "cancelled"
        assert payload["confirmed_intermediates"]
        confirmed_ids = {
            item["artifact_id"] for item in payload["confirmed_intermediates"]
        }
        assert str(confirmed.artifact_id) in confirmed_ids
        confirmed_payload = next(
            item
            for item in payload["confirmed_intermediates"]
            if item["artifact_id"] == str(confirmed.artifact_id)
        )
        assert confirmed_payload["content_hash"] == confirmed.content_hash.hex()
        assert confirmed_payload["source_analysis_artifact_ids"]
        assert payload["coverage"]["processed_count"] == scope.processed_count
        assert app.research_repository.get_scope(scope.scope_id).state is ResearchScopeState.PARTIAL
        assert app.jobs.get(job.job_id).state is JobState.CANCELLED
        assert partials.create(job.job_id) == result
        assert not any(
            item.stage is ResearchSynthesisStage.FINAL
            and app.research_repository.synthesis_artifact_for_work_item(
                item.work_item_id
            )
            is not None
            for item in app.research_repository.list_synthesis_work_items(scope.scope_id)
        )
    finally:
        app.stop()
