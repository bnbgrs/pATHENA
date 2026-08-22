from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run,
)
from athena.chat.repository import ChatRepository
from athena.common.ids import uuid_to_blob
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
        pipeline_version="metadata-corruption-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="metadata-corruption-test",
        prompt_template_version="1",
    )
    return user, package, run


def test_grounded_run_rejects_blank_persisted_pipeline_version(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        user, package, run = _fixture(database)
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE processing_runs SET pipeline_version = '' WHERE processing_run_id = ?",
                (uuid_to_blob(run.processing_run_id),),
            )
        with pytest.raises(
            GroundedProcessingRunError,
            match="invalid pipeline version",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=package,
                trigger_actor_id=user,
            )
    finally:
        database.stop()


def test_grounded_run_rejects_partial_prompt_template_provenance(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        user, package, run = _fixture(database)
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE processing_runs
                SET prompt_template_version = NULL
                WHERE processing_run_id = ?
                """,
                (uuid_to_blob(run.processing_run_id),),
            )
        with pytest.raises(
            GroundedProcessingRunError,
            match="prompt-template provenance is incomplete",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=package,
                trigger_actor_id=user,
            )
    finally:
        database.stop()
