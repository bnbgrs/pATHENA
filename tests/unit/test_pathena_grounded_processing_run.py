from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run,
)
from athena.chat.repository import ChatRepository
from athena.model.domain import ModelInfo
from athena.model.provenance import (
    ModelRunRepository,
    ModelSignature,
    ProcessingRun,
)
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _model(model_id: str = "primary") -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id=model_id,
        display_name=model_id,
        model_type="llm",
        context_capacity=32768,
        quantization="Q4_K_M",
        loaded=True,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=4096,
    )


def _package(
    signature: ModelSignature,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
) -> ContextPackage:
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="system",
                role="system",
                content="grounded",
                included_ref_ids=(),
            ),
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
                entity_id=operation_id,
                revision_id=revision_id,
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
            system_tokens=10,
            context_tokens=0,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=1,
    )


def _provenance(
    database: SQLiteDatabase,
    *,
    model_id: str = "primary",
) -> tuple[ModelRunRepository, ModelSignature, ProcessingRun, ContextPackage]:
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=_model(model_id),
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    package = _package(signature, uuid.uuid4(), uuid.uuid4())
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-test",
        prompt_template_version="1",
    )
    return model_runs, signature, run, package


def test_grounded_processing_run_accepts_matching_live_provenance(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, _, run, package = _provenance(database)
        validate_grounded_processing_run(
            database,
            processing_run_id=run.processing_run_id,
            package=package,
            trigger_actor_id=run.trigger_actor_id,
        )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_unknown_run(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, _, run, package = _provenance(database)
        with pytest.raises(
            GroundedProcessingRunError,
            match="persisted ProcessingRun",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=uuid.uuid4(),
                package=package,
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_finished_run(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        model_runs, _, run, package = _provenance(database)
        model_runs.finish_run(run.processing_run_id, status="succeeded")
        with pytest.raises(
            GroundedProcessingRunError,
            match="running ProcessingRun",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=package,
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_other_run_type(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        model_runs, signature, run, package = _provenance(database)
        foreign_run = model_runs.start_run(
            run_type="knowledge.extraction",
            trigger_actor_id=run.trigger_actor_id,
            pipeline_version="test-v1",
            input_snapshot=package.run_snapshot(),
            configuration={"context_package_version": 1},
            model_signature_id=signature.model_signature_id,
            prompt_template_id="grounded-test",
            prompt_template_version="1",
        )
        with pytest.raises(
            GroundedProcessingRunError,
            match="type conflicts",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=foreign_run.processing_run_id,
                package=package,
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_other_trigger_actor(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, _, run, package = _provenance(database)
        other_user = ChatRepository(database).create_actor(actor_type="user")
        assert other_user != run.trigger_actor_id
        with pytest.raises(
            GroundedProcessingRunError,
            match="trigger actor conflicts",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=package,
                trigger_actor_id=other_user,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_other_model_signature(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        model_runs, _, run, _ = _provenance(database)
        other_signature = model_runs.get_or_create_signature(
            model=_model("other"),
            generation_parameters={
                "max_output_tokens": 1000,
                "reasoning_mode": "off",
            },
            context_configuration={"context_package_version": 1},
        )
        with pytest.raises(
            GroundedProcessingRunError,
            match="ModelSignature conflicts",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=_package(other_signature, uuid.uuid4(), uuid.uuid4()),
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_other_context_snapshot(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, signature, run, _ = _provenance(database)
        other_package = _package(signature, uuid.uuid4(), uuid.uuid4())
        with pytest.raises(
            GroundedProcessingRunError,
            match="input snapshot conflicts",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=run.processing_run_id,
                package=other_package,
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()


def test_grounded_processing_run_rejects_other_configuration(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        model_runs, signature, run, package = _provenance(database)
        foreign_run = model_runs.start_run(
            run_type="chat.unified_local_context_package",
            trigger_actor_id=run.trigger_actor_id,
            pipeline_version="test-v1",
            input_snapshot=package.run_snapshot(),
            configuration={"context_package_version": 999},
            model_signature_id=signature.model_signature_id,
            prompt_template_id="grounded-test",
            prompt_template_version="1",
        )
        with pytest.raises(
            GroundedProcessingRunError,
            match="configuration conflicts",
        ):
            validate_grounded_processing_run(
                database,
                processing_run_id=foreign_run.processing_run_id,
                package=package,
                trigger_actor_id=run.trigger_actor_id,
            )
    finally:
        database.stop()
