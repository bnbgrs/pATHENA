from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    complete_grounded_processing_run,
)
from athena.chat.repository import ChatRepository
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _fixture(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=ModelInfo(
            provider="lm_studio",
            backend_model_id="primary",
            display_name="primary",
            model_type="llm",
            context_capacity=32768,
            quantization="Q4_K_M",
            loaded=True,
            vision=False,
            trained_for_tool_use=False,
            loaded_context_length=4096,
        ),
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    package = ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="current_user",
                role="user",
                content="hello",
                included_ref_ids=("CURRENT-USER",),
            ),
        ),
        included_refs=(
            ContextIncludedRef(
                ref_id="CURRENT-USER",
                entity_type="chat_message",
                entity_id=uuid.uuid4(),
                revision_id=uuid.uuid4(),
            ),
        ),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=0,
            conversation_included_count=0,
            conversation_excluded_count=0,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1210,
        ),
        snapshot_commit_seq=1,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="processing-run-completion-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="processing-run-completion-test",
        prompt_template_version="1",
    )
    return model_runs, user, package, run


def test_grounded_processing_run_completion_is_idempotent(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _model_runs, user, package, run = _fixture(database)
        first = complete_grounded_processing_run(
            database,
            processing_run_id=run.processing_run_id,
            package=package,
            trigger_actor_id=user,
        )
        second = complete_grounded_processing_run(
            database,
            processing_run_id=run.processing_run_id,
            package=package,
            trigger_actor_id=user,
        )
        assert first.status == "succeeded"
        assert first.finished_at_us is not None
        assert second == first
    finally:
        database.stop()


def test_grounded_processing_run_completion_rejects_failed_terminal_state(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        model_runs, user, package, run = _fixture(database)
        model_runs.finish_run(
            run.processing_run_id,
            status="failed",
            error_detail="ProviderError",
        )
        with pytest.raises(
            GroundedProcessingRunError,
            match="terminal state",
        ):
            complete_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=package,
                trigger_actor_id=user,
            )
    finally:
        database.stop()


def test_grounded_processing_run_completion_rejects_foreign_snapshot(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _model_runs, user, package, run = _fixture(database)
        foreign = ContextPackageService.build_from_sections(
            model_signature=ModelRunRepository(database).load_signature(
                package.model_signature.model_signature_id
            ),
            budget=package.budget,
            sections=package.sections,
            included_refs=package.included_refs,
            excluded_candidate_summary=package.excluded_candidate_summary,
            token_estimates=package.token_estimates,
            snapshot_commit_seq=package.snapshot_commit_seq + 1,
        )
        with pytest.raises(
            GroundedProcessingRunError,
            match="input snapshot conflicts",
        ):
            complete_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=foreign,
                trigger_actor_id=user,
            )
    finally:
        database.stop()
