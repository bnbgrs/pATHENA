from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_context_package import (
    GroundedContextPackageConflictError,
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_processing_run import bind_grounded_processing_run
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.grounded_send import GroundedProviderBoundaryError, GroundedSendCoordinator
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _commit_seq(database: SQLiteDatabase, revision_id: uuid.UUID) -> int:
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


def _current_commit_seq(database: SQLiteDatabase) -> int:
    row = database.connection.execute(
        "SELECT COALESCE(MAX(commit_seq), 0) AS commit_seq FROM commit_records"
    ).fetchone()
    assert row is not None
    return int(row["commit_seq"])


def _package(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    *,
    snapshot_commit_seq: int | None = None,
    model_signature: ModelSignature | None = None,
):
    signature = model_signature or ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization="Q4_K_M",
        generation_parameters_json='{"max_output_tokens":1000,"reasoning_mode":"off"}',
        context_configuration_json='{"mode":"unified_local_chat"}',
        signature_hash=b"s" * 32,
        created_at_us=1,
    )
    resolved_snapshot_commit_seq = (
        _commit_seq(database, revision_id)
        if snapshot_commit_seq is None
        else snapshot_commit_seq
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
                name="system",
                role="system",
                content="exact durable evidence",
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
            context_tokens=10,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=resolved_snapshot_commit_seq,
    )


def _package_and_run(
    database: SQLiteDatabase,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    actor_id: uuid.UUID,
):
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
        context_configuration={"mode": "unified_local_chat"},
    )
    package = _package(
        database,
        operation_id,
        revision_id,
        model_signature=signature,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=actor_id,
        pipeline_version="grounded-context-package-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"mode": "unified_local_chat"},
        model_signature_id=signature.model_signature_id,
        prompt_template_id=None,
        prompt_template_version=None,
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


def test_exact_grounded_context_package_survives_restart(tmp_path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    package = _package(database, operation_id, message.revision_id)
    repository = GroundedContextPackageRepository(database)
    stored = repository.store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    )
    assert repository.store(
        operation_id=operation_id,
        chat_id=chat_id,
        package=package,
    ) == stored
    database.stop()

    database = SQLiteDatabase(path)
    database.start()
    recovered = GroundedContextPackageRepository(database).load(operation_id)
    assert recovered is not None
    assert recovered.payload_sha256 == stored.payload_sha256
    assert recovered.package == package
    assert recovered.package.model_messages() == package.model_messages()
    database.stop()


def test_grounded_context_package_rejects_other_current_user(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    with pytest.raises(GroundedContextPackageConflictError):
        GroundedContextPackageRepository(database).store(
            operation_id=operation_id,
            chat_id=chat_id,
            package=_package(
                database,
                uuid.uuid4(),
                uuid.uuid4(),
                snapshot_commit_seq=_current_commit_seq(database),
            ),
        )
    database.stop()


def test_context_package_rejects_wrong_current_user_revision(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=_fingerprint(chat_id),
        )

        with pytest.raises(
            GroundedContextPackageConflictError,
            match="model-input contract",
        ):
            GroundedContextPackageRepository(database).store(
                operation_id=operation_id,
                chat_id=chat_id,
                package=_package(
                    database,
                    operation_id,
                    uuid.uuid4(),
                    snapshot_commit_seq=_current_commit_seq(database),
                ),
            )
    finally:
        database.stop()


def test_context_package_load_rejects_tampered_user_content(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        message = GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=_fingerprint(chat_id),
        )
        repository = GroundedContextPackageRepository(database)
        repository.store(
            operation_id=operation_id,
            chat_id=chat_id,
            package=_package(database, operation_id, message.revision_id),
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE chat_message_revisions SET content = ? WHERE revision_id = ?",
                ("tampered", uuid_to_blob(message.revision_id)),
            )

        with pytest.raises(
            GroundedContextPackageSchemaError,
            match="model-input contract",
        ):
            repository.load(operation_id)
    finally:
        database.stop()


def test_context_package_cannot_be_backfilled_after_provider_start(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        message = GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=_fingerprint(chat_id),
        )
        GroundedProviderAttemptRepository(database).mark_started(
            operation_id=operation_id,
            chat_id=chat_id,
        )
        repository = GroundedContextPackageRepository(database)

        with pytest.raises(
            GroundedContextPackageConflictError,
            match="before provider execution begins",
        ):
            repository.store(
                operation_id=operation_id,
                chat_id=chat_id,
                package=_package(database, operation_id, message.revision_id),
            )

        assert repository.load(operation_id) is None
    finally:
        database.stop()


def test_recovery_rejects_result_missing_identity_when_context_is_pinned(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        fingerprint = _fingerprint(chat_id)
        message = GroundedUserTurnRepository(database).commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        package, processing_run_id = _package_and_run(
            database,
            operation_id,
            message.revision_id,
            user,
        )
        GroundedContextPackageRepository(database).store(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
        )
        bind_grounded_processing_run(
            database,
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            package=package,
            trigger_actor_id=user,
        )
        provider = GroundedProviderAttemptRepository(database)
        provider.mark_started(operation_id=operation_id, chat_id=chat_id)
        provider.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="primary",
        )
        with database.write_transaction() as connection:
            connection.execute(
                "DELETE FROM grounded_provider_result_identities WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            )

        status = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.provider_result is None
        assert status.provider_identity is None
    finally:
        database.stop()


def test_provider_boundary_rejects_context_model_mismatch_with_request(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        operation_id = uuid.uuid4()
        fingerprint = build_chat_request_fingerprint(
            mode=ChatSendMode.GROUNDED,
            chat_id=chat_id,
            content="hello",
            requested_model_id="other-model",
            requested_embedding_model_id=None,
            effective_context_limit=4096,
            max_output_tokens=1000,
            temperature=None,
            reasoning_mode="off",
            retrieval_configuration={},
        )
        coordinator = GroundedSendCoordinator(database)
        started = coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        coordinator.store_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            package=_package(database, operation_id, started.user_message.revision_id),
        )

        with pytest.raises(GroundedProviderBoundaryError) as exc_info:
            coordinator.begin_provider_attempt(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )

        assert exc_info.value.status.state is GroundedRecoveryState.CONFLICT
        assert coordinator.provider_attempts.load(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.CONFLICT
    finally:
        database.stop()
