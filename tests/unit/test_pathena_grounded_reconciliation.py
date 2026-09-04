from __future__ import annotations

import json
import uuid

from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
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


def _fingerprint(chat_id: uuid.UUID, content: str = "hello"):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content=content,
        requested_model_id="model",
        requested_embedding_model_id="embed",
        effective_context_limit=4096,
        max_output_tokens=1024,
        temperature=0.3,
        reasoning_mode="off",
        retrieval_configuration={"max_items": 4},
    )


def _chat(database: SQLiteDatabase) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID]:
    chats = ChatRepository(database)
    actor = chats.create_actor(actor_type="user")
    model_actor = chats.create_actor(
        actor_type="primary_model",
        display_name="lm_studio:model",
    )
    return actor, model_actor, chats.create_chat(actor_id=actor)


def _model_info() -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="model",
        display_name="model",
        model_type="llm",
        context_capacity=32768,
        quantization=None,
        loaded=True,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=4096,
    )


def _context_package(
    signature: ModelSignature,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    *,
    snapshot_commit_seq: int,
) -> ContextPackage:
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2872,
            output_reserve=1024,
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
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1034,
        ),
        snapshot_commit_seq=snapshot_commit_seq,
    )


def _start(
    database: SQLiteDatabase,
    *,
    actor_id: uuid.UUID,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    fingerprint,
) -> tuple[GroundedSendCoordinator, uuid.UUID]:
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=actor_id,
        content="hello",
        fingerprint=fingerprint,
    )
    return coordinator, started.user_message.revision_id


def _bind_context_and_run(
    coordinator: GroundedSendCoordinator,
    *,
    actor_id: uuid.UUID,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
) -> uuid.UUID:
    commit_row = coordinator.database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.entity_id = ? AND r.revision_id = ?
        """,
        (uuid_to_blob(operation_id), uuid_to_blob(revision_id)),
    ).fetchone()
    assert commit_row is not None

    model_runs = ModelRunRepository(coordinator.database)
    context_configuration = {
        "mode": "grounded",
        "embedding_model_id": "embed",
    }
    signature = model_runs.get_or_create_signature(
        model=_model_info(),
        generation_parameters={
            "max_output_tokens": 1024,
            "reasoning_mode": "off",
            "temperature": 0.3,
        },
        context_configuration=context_configuration,
    )
    package = _context_package(
        signature,
        operation_id,
        revision_id,
        snapshot_commit_seq=int(commit_row["commit_seq"]),
    )
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=actor_id,
        pipeline_version="test-v1",
        input_snapshot=package.run_snapshot(),
        configuration=context_configuration,
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        coordinator.database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=actor_id,
    )
    return run.processing_run_id


def _journal_and_commit_assistant(
    coordinator: GroundedSendCoordinator,
    *,
    model_actor_id: uuid.UUID,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    fingerprint,
    processing_run_id: uuid.UUID,
    payload_json: str,
) -> None:
    payload = json.loads(payload_json)
    assistant_content = payload["assistant_text"]
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    coordinator.record_provider_result(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        processing_run_id=processing_run_id,
        assistant_content=assistant_content,
        receipt_payload_json=payload_json,
        provider_id="lm_studio",
        model_id="model",
    )
    coordinator.commit_assistant(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=model_actor_id,
        content=assistant_content,
    )


def test_reconciliation_projects_absent_incomplete_complete_and_conflict(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor, model_actor, chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    reconciler = GroundedSendReconciler(database)

    assert reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.ABSENT

    coordinator, revision_id = _start(
        database,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
    )
    assert reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    ).state is GroundedReconciliationState.INCOMPLETE

    conflict = reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=_fingerprint(chat_id, "different"),
    )
    assert conflict.state is GroundedReconciliationState.CONFLICT

    run_id = _bind_context_and_run(
        coordinator,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        revision_id=revision_id,
    )
    payload = '{"assistant_text":"answer","evidence":[]}'
    _journal_and_commit_assistant(
        coordinator,
        model_actor_id=model_actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        payload_json=payload,
    )
    completed = coordinator.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    status = reconciler.inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.COMPLETE
    assert status.receipt == completed
    database.stop()


def test_reconciliation_survives_restart_and_returns_exact_receipt(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    actor, model_actor, chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator, revision_id = _start(
        database,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
    )
    run_id = _bind_context_and_run(
        coordinator,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        revision_id=revision_id,
    )
    payload = '{"assistant_text":"replay","evidence":["CTX-001"]}'
    _journal_and_commit_assistant(
        coordinator,
        model_actor_id=model_actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        payload_json=payload,
    )
    coordinator.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    status = GroundedSendReconciler(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.COMPLETE
    assert status.receipt is not None
    assert status.receipt.payload_json == payload
    database.stop()


def test_reconciliation_fails_closed_when_complete_operation_loses_receipt(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor, model_actor, chat_id = _chat(database)
    operation_id = uuid.uuid4()
    fingerprint = _fingerprint(chat_id)
    coordinator, revision_id = _start(
        database,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
    )
    run_id = _bind_context_and_run(
        coordinator,
        actor_id=actor,
        chat_id=chat_id,
        operation_id=operation_id,
        revision_id=revision_id,
    )
    payload = '{"assistant_text":"answer"}'
    _journal_and_commit_assistant(
        coordinator,
        model_actor_id=model_actor,
        chat_id=chat_id,
        operation_id=operation_id,
        fingerprint=fingerprint,
        processing_run_id=run_id,
        payload_json=payload,
    )
    coordinator.complete(
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run_id,
        payload_json=payload,
    )
    database.connection.execute(
        "DELETE FROM grounded_send_receipts WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    )
    status = GroundedSendReconciler(database).inspect(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    assert status.state is GroundedReconciliationState.CONFLICT
    assert status.receipt is None
    database.stop()


def test_reconciliation_fails_closed_when_receipt_is_corrupted(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        actor, model_actor, chat_id = _chat(database)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        coordinator, revision_id = _start(
            database,
            actor_id=actor,
            chat_id=chat_id,
            operation_id=operation_id,
            fingerprint=fingerprint,
        )
        run_id = _bind_context_and_run(
            coordinator,
            actor_id=actor,
            chat_id=chat_id,
            operation_id=operation_id,
            revision_id=revision_id,
        )
        payload = '{"assistant_text":"answer"}'
        _journal_and_commit_assistant(
            coordinator,
            model_actor_id=model_actor,
            chat_id=chat_id,
            operation_id=operation_id,
            fingerprint=fingerprint,
            processing_run_id=run_id,
            payload_json=payload,
        )
        coordinator.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=run_id,
            payload_json=payload,
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE grounded_send_receipts SET payload_json = ? WHERE operation_id = ?",
                ('{"assistant_text":"tampered"}', uuid_to_blob(operation_id)),
            )

        status = GroundedSendReconciler(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedReconciliationState.CONFLICT
        assert status.receipt is None
    finally:
        database.stop()
