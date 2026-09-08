from __future__ import annotations

from pathlib import Path

import pytest
from test_exhaustive_research_synthesis_service import _prepare_research

from athena.research.models import ResearchSynthesisStage
from athena.research.synthesis_service import ResearchSynthesisInputTooLargeError


def test_large_archive_synthesis_splits_until_every_model_call_fits_pinned_context(
    tmp_path: Path,
) -> None:
    app, provider, job, scope, lease_token, service = _prepare_research(
        tmp_path,
        source_count=40,
        context_capacity=2_048,
    )

    assert scope.effective_context_limit == 2_048
    assert scope.output_reserve > 0
    assert scope.safety_margin > 0

    source_artifacts = set(
        app.research_repository.successful_source_analysis_final_artifact_ids(
            scope.scope_id
        )
    )
    assert len(source_artifacts) == 40

    first_final = service.plan_next_synthesis(
        scope,
        parent_job_id=job.job_id,
        lease_token=lease_token,
    )
    assert first_final.stage is ResearchSynthesisStage.FINAL

    with pytest.raises(
        ResearchSynthesisInputTooLargeError,
        match="exceeds pinned input budget",
    ):
        service.prepare_call(scope, first_final)

    synthesis_call_start = len(provider.calls)
    prepared_input_tokens: list[int] = []
    final_artifact = None

    def execute_or_split(work) -> None:
        nonlocal final_artifact
        try:
            prepared = service.prepare_call(scope, work)
        except ResearchSynthesisInputTooLargeError:
            children = service.split_synthesis_work(
                scope,
                work,
                parent_job_id=job.job_id,
                lease_token=lease_token,
            )
            assert children
            for child in children:
                execute_or_split(child)
            return

        prepared_input_tokens.append(prepared.estimated_input_tokens)
        artifact = service.execute_call_with_coverage_repair(
            scope=scope,
            parent_job_id=job.job_id,
            lease_token=lease_token,
            prepared=prepared,
            extend_seconds=120,
        )
        if work.stage is ResearchSynthesisStage.FINAL:
            final_artifact = artifact

    for _ in range(16):
        work = service.plan_next_synthesis(
            scope,
            parent_job_id=job.job_id,
            lease_token=lease_token,
        )
        execute_or_split(work)
        if final_artifact is not None:
            break
    else:
        raise AssertionError("Large-archive synthesis did not converge to a final artifact.")

    synthesis_output_limits = [
        output_limit
        for (schema_id, _messages), output_limit in zip(
            provider.calls[synthesis_call_start:],
            provider.max_output_limits[synthesis_call_start:],
            strict=True,
        )
        if schema_id.startswith("athena_research_synthesis_")
    ]
    assert len(synthesis_output_limits) == len(prepared_input_tokens)
    assert len(synthesis_output_limits) > 1

    for request_tokens, output_limit in zip(
        prepared_input_tokens,
        synthesis_output_limits,
        strict=True,
    ):
        assert output_limit is not None
        assert (
            request_tokens + output_limit + scope.safety_margin
            <= scope.effective_context_limit
        )

    assert final_artifact is not None
    precise_sources = set(
        app.research_repository.precise_source_analysis_artifact_ids_for_synthesis_output(
            final_artifact.artifact_id,
            output_kind="finding",
            output_ordinal=0,
        )
    )
    assert precise_sources == source_artifacts

    app.jobs.yield_job(job.job_id, lease_token=lease_token)
    app.stop()
