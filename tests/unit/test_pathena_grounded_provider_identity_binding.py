from __future__ import annotations

import uuid

import pytest

from athena.chat.grounded_provider_attempt import GroundedProviderAttemptConflictError
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import (
    GroundedProviderIdentityError,
    GroundedSendCoordinator,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


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


def _package(operation_id: uuid.UUID, revision_id: uuid.UUID):
    signature = ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization="Q4_K_M",
        generation_parameters_json='{"max_output_tokens":1000,"reasoning_mode":"off"}',
        context_configuration_json='{"context_package_version":1}',
        signature_hash=b"s" * 32,
        created_at_us=1,
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
        snapshot_commit_seq=1,
    )


def _started_coordinator(database: SQLiteDatabase):
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
    coordinator.store_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        package=_package(operation_id, started.user_message.revision_id),
    )
    coordinator.begin_provider_attempt(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
    )
    return coordinator, chat_id, operation_id, fingerprint


def test_provider_result_identity_must_match_pinned_context_model(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, chat_id, operation_id, fingerprint = _started_coordinator(database)

        with pytest.raises(
            GroundedProviderIdentityError,
            match="pinned ContextPackage model",
        ):
            coordinator.record_provider_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                processing_run_id=uuid.uuid4(),
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer"}',
                provider_id="other_provider",
                model_id="other_model",
            )

        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.provider_attempts.load_result_identity(operation_id) is None
    finally:
        database.stop()


def test_low_level_provider_result_cannot_bypass_pinned_context_model(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, chat_id, operation_id, _ = _started_coordinator(database)

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="pinned ContextPackage model",
        ):
            coordinator.provider_attempts.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=uuid.uuid4(),
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer"}',
                provider_id="other_provider",
                model_id="other_model",
            )

        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.provider_attempts.load_result_identity(operation_id) is None
    finally:
        database.stop()


def test_low_level_provider_result_requires_identity_when_context_pins_model(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, chat_id, operation_id, _ = _started_coordinator(database)

        with pytest.raises(
            GroundedProviderAttemptConflictError,
            match="identity is required",
        ):
            coordinator.provider_attempts.store_result(
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=uuid.uuid4(),
                assistant_content="answer",
                receipt_payload_json='{"assistant_text":"answer"}',
            )

        assert coordinator.provider_attempts.load_result(operation_id) is None
        assert coordinator.provider_attempts.load_result_identity(operation_id) is None
    finally:
        database.stop()


def test_recovery_rejects_provider_identity_tampered_after_persistence(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        coordinator, chat_id, operation_id, fingerprint = _started_coordinator(database)
        coordinator.record_provider_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            processing_run_id=uuid.uuid4(),
            assistant_content="answer",
            receipt_payload_json='{"assistant_text":"answer"}',
            provider_id="lm_studio",
            model_id="primary",
        )
        with database.write_transaction() as connection:
            connection.execute(
                """
                UPDATE grounded_provider_result_identities
                SET provider_id = ?
                WHERE operation_id = ?
                """,
                ("tampered_provider", uuid_to_blob(operation_id)),
            )

        status = coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        assert status.provider_result is None
        assert status.provider_identity is None
    finally:
        database.stop()
