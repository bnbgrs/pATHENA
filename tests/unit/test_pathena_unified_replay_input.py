from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.send_operation import ChatSendOperationRepository
from athena.chat.unified_replay import build_unified_replay_projection
from athena.chat.unified_replay_input import (
    UnifiedReplayInputConflictError,
    UnifiedReplayInputRepository,
    UnifiedReplayInputSchemaError,
)
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBuilderService
from athena.retrieval.context_package import (
    ContextPackageBudget,
    ContextPackageService,
    ContextTokenEstimates,
)
from athena.retrieval.evidence import MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBundle
from athena.storage.database import SQLiteDatabase


def _user_commit_seq(database: SQLiteDatabase, revision_id: uuid.UUID) -> int:
    row = database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.revision_id = ?
        """,
        (uuid_to_blob(revision_id),),
    ).fetchone()
    assert row is not None
    return int(row["commit_seq"])


def _fixture(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user_id = chats.create_actor(actor_type="user", display_name="Replay Test User")
    chat_id = chats.create_chat(actor_id=user_id)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="checkpoint request",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={"test": "unified-replay-input"},
    )
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user_id,
        content="checkpoint request",
        fingerprint=fingerprint,
    )

    primary_model = ModelInfo(
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
    )
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=primary_model,
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={
            "mode": "unified_local_chat",
            "embedding_model_id": None,
            "evidence_policy_id": "typed-provenance-v1",
            "allow_model_prior": True,
            "memory_context_budget": 300,
            "source_context_budget": 300,
        },
    )
    memory_context = ContextBuilderService().build_from_ranked(
        query="checkpoint request",
        results=(),
        max_estimated_tokens=300,
    )
    package = ContextPackageService.build(
        model_signature=signature,
        context=memory_context,
        system_text="UNIFIED TEST SYSTEM",
        prior_messages=(),
        current_user_message=started.user_message,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=600,
            output_reserve=1000,
            safety_margin=200,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=8,
            system_tokens=8,
            context_tokens=memory_context.estimated_tokens,
            estimated_input_tokens=16 + memory_context.estimated_tokens,
            estimated_total_tokens=1216 + memory_context.estimated_tokens,
        ),
        snapshot_commit_seq=_user_commit_seq(database, started.user_message.revision_id),
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user_id,
        pipeline_version="unified-replay-input-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"test": "unified-replay-input"},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="unified-local-chat",
        prompt_template_version="1",
    )
    ChatSendOperationRepository(database).bind_grounded_processing_run(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
    )
    GroundedContextPackageRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    source_context = SourceContextBundle(
        query="checkpoint request",
        mode="archive_hybrid",
        items=(),
        omitted_count=0,
        estimated_tokens=0,
        max_estimated_tokens=300,
        rendered_text="",
    )
    evidence = MemoryEvidenceSelection(
        policy_id="typed-provenance-v1",
        results=(),
        classifications=(),
    )
    projection = build_unified_replay_projection(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        context_package=package,
        primary_model=primary_model,
        embedding_model=None,
        memory_context=memory_context,
        source_context=source_context,
        evidence_selection=evidence,
    )
    return operation_id, chat_id, run.processing_run_id, package, projection


def test_unified_replay_checkpoint_is_idempotent_and_restart_safe(tmp_path: Path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    try:
        operation_id, chat_id, run_id, package, projection = _fixture(database)
        repository = UnifiedReplayInputRepository(database)
        first = repository.store(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            projection=projection,
        )
        second = repository.store(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            projection=projection,
        )
        assert second == first
        assert first.context_package_request_id == package.request_id

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        loaded = UnifiedReplayInputRepository(database).load(operation_id)
        assert loaded == first
        assert loaded is not None
        assert loaded.projection.primary_model.backend_model_id == "primary"
    finally:
        database.stop()


def test_unified_replay_checkpoint_rejects_drift_and_corruption(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, run_id, _package, projection = _fixture(database)
        repository = UnifiedReplayInputRepository(database)
        repository.store(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            projection=projection,
        )

        changed = json.loads(json.dumps(projection))
        changed["primary_model"]["display_name"] = "changed"
        with pytest.raises(UnifiedReplayInputConflictError):
            repository.store(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=run_id,
                projection=changed,
            )

        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE unified_grounded_replay_inputs
                SET payload_sha256 = ?
                WHERE operation_id = ?
                """,
                ("0" * 64, uuid_to_blob(operation_id)),
            )
        with pytest.raises(UnifiedReplayInputSchemaError):
            repository.load(operation_id)
    finally:
        database.stop()
