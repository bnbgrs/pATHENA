from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import (
    GroundedProviderBoundaryError,
    GroundedProviderContextError,
    GroundedSendCoordinator,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
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


def _fingerprint(
    chat_id: uuid.UUID,
    *,
    temperature: float | None = None,
):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=temperature,
        reasoning_mode="off",
        retrieval_configuration={},
    )


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


def _package(
    database: SQLiteDatabase,
    *,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    temperature: float | None = None,
):
    generation_parameters: dict[str, object] = {
        "max_output_tokens": 1000,
        "reasoning_mode": "off",
    }
    if temperature is not None:
        generation_parameters["temperature"] = temperature
    signature = ModelRunRepository(database).get_or_create_signature(
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
        generation_parameters=generation_parameters,
        context_configuration={"context_package_version": 1},
    )
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
            estimated_total_tokens=1210,
        ),
        snapshot_commit_seq=_user_commit_seq(database, revision_id),
    )


def _bind_processing_run(
    database: SQLiteDatabase,
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    trigger_actor_id: uuid.UUID,
    package: ContextPackage,
) -> None:
    run = ModelRunRepository(database).start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=trigger_actor_id,
        pipeline_version="coordinator-context-fence-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=package.model_signature.model_signature_id,
        prompt_template_id="coordinator-context-fence-test",
        prompt_template_version="1",
    )
    bind_grounded_processing_run(
        database,
        operation_id=operation_id,
        chat_id=chat_id,
        processing_run_id=run.processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )


def _started(database: SQLiteDatabase):
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
    return chats, user, chat_id, operation_id, fingerprint, coordinator, started


def test_coordinator_rejects_stale_snapshot_before_attempt(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats, user, chat_id, operation_id, fingerprint, coordinator, started = _started(
            database
        )
        package = _package(
            database,
            operation_id=operation_id,
            revision_id=started.user_message.revision_id,
        )
        coordinator.store_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
        )
        _bind_processing_run(
            database,
            operation_id=operation_id,
            chat_id=chat_id,
            trigger_actor_id=user,
            package=package,
        )
        other_chat_id = chats.create_chat(actor_id=user)
        ChatService(chats).add_user_message(
            chat_id=other_chat_id,
            content="later canonical commit",
        )

        with pytest.raises(
            GroundedProviderContextError,
            match="durable ContextPackage",
        ):
            coordinator.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        assert coordinator.provider_attempts.load(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.RESUMABLE
    finally:
        database.stop()


def test_coordinator_rejects_none_temperature_drift_before_attempt(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, user, chat_id, operation_id, fingerprint, coordinator, started = _started(
            database
        )
        package = _package(
            database,
            operation_id=operation_id,
            revision_id=started.user_message.revision_id,
            temperature=0.7,
        )
        coordinator.store_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
        )
        _bind_processing_run(
            database,
            operation_id=operation_id,
            chat_id=chat_id,
            trigger_actor_id=user,
            package=package,
        )

        with pytest.raises(
            GroundedProviderBoundaryError,
            match="conflict; only resumable operations may begin a provider attempt",
        ):
            coordinator.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        assert coordinator.provider_attempts.load(operation_id) is None
    finally:
        database.stop()
