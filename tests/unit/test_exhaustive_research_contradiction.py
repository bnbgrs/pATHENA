from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_exhaustive_research_synthesis_service import (
    _acquire_parent,
    _app,
    _capture,
    _drive_to_synthesis_wait,
)

from athena.research.synthesis_service import ResearchSynthesisService


def test_opposing_sources_remain_visible_in_final_research_contradiction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, provider = _app(tmp_path / "runtime")
    original_generate_structured = provider.generate_structured

    def generate_structured(
        *,
        model_id: str,
        messages,
        schema_id: str,
        json_schema,
        max_output_tokens: int | None = None,
    ):
        text = "\n".join(message.content for message in messages)
        if schema_id.startswith("athena_research_synthesis_"):
            return original_generate_structured(
                model_id=model_id,
                messages=messages,
                schema_id=schema_id,
                json_schema=json_schema,
                max_output_tokens=max_output_tokens,
            )
        if "launch succeeded" in text:
            finding = "The launch succeeded."
        elif "launch failed" in text:
            finding = "The launch failed."
        else:
            return original_generate_structured(
                model_id=model_id,
                messages=messages,
                schema_id=schema_id,
                json_schema=json_schema,
                max_output_tokens=max_output_tokens,
            )
        if "map" in schema_id:
            return {
                "relevant": True,
                "summary": finding,
                "findings": [finding],
                "contradictions": [],
                "uncertainty": "",
            }
        return {
            "summary": finding,
            "findings": [finding],
            "contradictions": [],
            "uncertainty": "",
        }

    monkeypatch.setattr(provider, "generate_structured", generate_structured)

    _capture(
        app,
        tmp_path / "successful-launch.txt",
        "The launch succeeded according to the primary operational record.",
    )
    _capture(
        app,
        tmp_path / "failed-launch.txt",
        "The launch failed according to the independent incident record.",
    )

    job = app.research.enqueue_local(query="Did the launch succeed or fail?")
    waiting = _drive_to_synthesis_wait(app, job.job_id)
    assert waiting.completed_stage == "awaiting_synthesis"

    scope = app.research.initialize(job.job_id)
    source_artifacts = set(
        app.research_repository.successful_source_analysis_final_artifact_ids(
            scope.scope_id
        )
    )
    assert len(source_artifacts) == 2

    lease_token = _acquire_parent(app, job.job_id)
    service = ResearchSynthesisService(
        repository=app.research_repository,
        source_analysis=app.source_analysis_service,
    )
    work = service.plan_next_synthesis(
        scope,
        parent_job_id=job.job_id,
        lease_token=lease_token,
    )
    prepared = service.prepare_call(scope, work)
    prepared_text = "\n".join(message.content for message in prepared.messages)
    assert "The launch succeeded." in prepared_text
    assert "The launch failed." in prepared_text

    artifact = service.execute_call_with_coverage_repair(
        scope=scope,
        parent_job_id=job.job_id,
        lease_token=lease_token,
        prepared=prepared,
        extend_seconds=120,
    )

    content = json.loads(artifact.content_json)
    assert content["contradictions"] == ["preserved disagreement"]
    precise_sources = set(
        app.research_repository.precise_source_analysis_artifact_ids_for_synthesis_output(
            artifact.artifact_id,
            output_kind="contradiction",
            output_ordinal=0,
        )
    )
    assert precise_sources == source_artifacts

    app.jobs.yield_job(job.job_id, lease_token=lease_token)
    app.stop()
