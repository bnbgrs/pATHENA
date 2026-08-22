from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_completion import (
    GroundedSendCompletionConflictError,
    GroundedSendCompletionCorruptionError,
    GroundedSendCompletionRepository,
)
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
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


def _package_and_run(
    database: SQLiteDatabase,
    user_message: ChatMessage,
) -> tuple[ContextPackage, uuid.UUID]:
    if user_message.actor_id is None:
        raise AssertionError("Test user message must have an actor.")
    runs = ModelRunRepository(database)
    signature = runs.get_or_create_signature(
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
    run = runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user_message.actor_id,
        pipeline_version="grounded-completion-run-fence-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-completion-run-fence",
        prompt_template_version="1",
    )
    return package, run.processing_run_id


def _fingerprint(chat_id: uuid.UUID):
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


def _receipt_payload() -> str:
    return json.dumps(
        {
            "assistant_text": "durable answer",
            "provider_id": "lm_studio",
            "model_id": "primary",
        }
    )


def _prepare_assistant_committed(
    database: SQLiteDatabase,
) -> tuple[
    GroundedSendCoordinator,
    uuid.UUID,
    uuid.UUID,
    uuid.UUID,
    str,
]:
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
    package, processing_run_id = _package_and_run(database, started.user_message)
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    payload = _receipt_payload()
    result = coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=processing_run_id,
        assistant_content="durable answer",
        receipt_payload_json=payload,
        provider_id="lm_studio",
        model_id="primary",
    )
    model_actor = ChatService(chats).ensure_primary_model(
        provider_id="lm_studio",
        model_id="primary",
    )
    coordinator.commit_assistant(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model_actor,
        content=result.assistant_content,
    )
    return coordinator, operation_id, chat_id, processing_run_id, payload


def test_low_level_completion_refuses_running_pinned_processing_run(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, operation_id, chat_id, processing_run_id, payload = (
            _prepare_assistant_committed(database)
        )
        runs = ModelRunRepository(database)
        before = runs.load_run(processing_run_id)
        assert before.status == "running"
        assert before.finished_at_us is None

        completions = GroundedSendCompletionRepository(database)
        with pytest.raises(
            GroundedSendCompletionConflictError,
            match="requires a succeeded ProcessingRun",
        ):
            completions.complete(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=processing_run_id,
                payload_json=payload,
            )
        assert completions.load(operation_id) is None
        still_running = runs.load_run(processing_run_id)
        assert still_running.status == "running"
        assert still_running.finished_at_us is None

        receipt = coordinator.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            payload_json=payload,
        )
        succeeded = runs.load_run(processing_run_id)
        assert succeeded.status == "succeeded"
        assert succeeded.finished_at_us is not None
        assert completions.load(operation_id) == receipt
    finally:
        database.stop()


def test_low_level_receipt_load_rejects_nonterminal_pinned_processing_run(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, operation_id, chat_id, processing_run_id, payload = (
            _prepare_assistant_committed(database)
        )
        receipt = coordinator.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            payload_json=payload,
        )
        completions = GroundedSendCompletionRepository(database)
        assert completions.load(operation_id) == receipt

        with database.write_transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE processing_runs
                SET status = 'running', finished_at_us = NULL, error_detail = NULL
                WHERE processing_run_id = ?
                """,
                (uuid_to_blob(processing_run_id),),
            )
            assert cursor.rowcount == 1

        with pytest.raises(
            GroundedSendCompletionCorruptionError,
            match="requires a succeeded ProcessingRun",
        ):
            completions.load(operation_id)
    finally:
        database.stop()
