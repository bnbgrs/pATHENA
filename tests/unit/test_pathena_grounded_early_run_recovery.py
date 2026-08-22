from __future__ import annotations

import uuid
from pathlib import Path

from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import (
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBuilderService
from athena.retrieval.context_package import (
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextTokenEstimates,
)
from athena.storage.database import SQLiteDatabase


def _model() -> ModelInfo:
    return ModelInfo(
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


def _user_commit_seq(database: SQLiteDatabase, user_message: ChatMessage) -> int:
    row = database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.revision_id = ?
        """,
        (uuid_to_blob(user_message.revision_id),),
    ).fetchone()
    assert row is not None
    return int(row["commit_seq"])


def _package_and_run(
    database: SQLiteDatabase,
    user_message: ChatMessage,
) -> tuple[ContextPackage, uuid.UUID]:
    assert user_message.actor_id is not None
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=_model(),
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    context = ContextBuilderService().build_from_ranked(
        query=user_message.content or "request",
        results=(),
        max_estimated_tokens=300,
    )
    package = ContextPackageService.build(
        model_signature=signature,
        context=context,
        system_text="PACKAGE SYSTEM",
        prior_messages=(),
        current_user_message=user_message,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=300,
            output_reserve=1000,
            safety_margin=200,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=10,
            context_tokens=context.estimated_tokens,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=_user_commit_seq(database, user_message),
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user_message.actor_id,
        pipeline_version="early-run-recovery-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="early-run-recovery-test",
        prompt_template_version="1",
    )
    return package, run.processing_run_id


def _fingerprint(chat_id: uuid.UUID) -> ChatRequestFingerprint:
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
    )


def _pin_run_before_context(
    database: SQLiteDatabase,
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, ChatRequestFingerprint]:
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
    package, run_id = _package_and_run(database, started.user_message)
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        package=package,
        trigger_actor_id=user,
    )
    assert coordinator.load_context_package(operation_id) is None
    return operation_id, chat_id, run_id, fingerprint


def test_restart_recovers_run_pinned_before_context_package(tmp_path: Path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    try:
        operation_id, chat_id, run_id, fingerprint = _pin_run_before_context(database)
        before = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert before.state is GroundedRecoveryState.RESUMABLE
        assert before.processing_run_id == run_id

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        restarted = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert restarted.state is GroundedRecoveryState.RESUMABLE
        assert restarted.processing_run_id == run_id
        run = ModelRunRepository(database).load_run(run_id)
        assert run.status == "running"
        assert run.finished_at_us is None
    finally:
        database.stop()


def test_early_pinned_run_missing_after_restart_is_conflict(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, run_id, fingerprint = _pin_run_before_context(database)
        database.connection.execute(
            "DELETE FROM processing_runs WHERE processing_run_id = ?",
            (uuid_to_blob(run_id),),
        )

        status = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.processing_run_id == run_id
    finally:
        database.stop()


def test_early_pinned_terminal_run_without_provider_attempt_is_conflict(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        operation_id, chat_id, run_id, fingerprint = _pin_run_before_context(database)
        ModelRunRepository(database).finish_run(
            run_id,
            status="failed",
            error_detail="SimulatedFailure",
        )

        status = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.processing_run_id == run_id
    finally:
        database.stop()