from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.grounded_snapshot import (
    GroundedSnapshotBindingError,
    validate_grounded_snapshot_current,
    validate_grounded_snapshot_identity,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
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


def _signature(database: SQLiteDatabase) -> ModelSignature:
    return ModelRunRepository(database).get_or_create_signature(
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


def _user_commit_seq(
    database: SQLiteDatabase,
    revision_id: uuid.UUID,
) -> int:
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
    *,
    signature: ModelSignature,
    operation_id: uuid.UUID,
    revision_id: uuid.UUID,
    snapshot_commit_seq: int,
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
        snapshot_commit_seq=snapshot_commit_seq,
    )


def _started(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    snapshot_commit_seq = _user_commit_seq(
        database,
        started.user_message.revision_id,
    )
    package = _package(
        signature=_signature(database),
        operation_id=operation_id,
        revision_id=started.user_message.revision_id,
        snapshot_commit_seq=snapshot_commit_seq,
    )
    return chats, user, chat_id, operation_id, package


def test_snapshot_identity_matches_current_user_commit(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, _user, _chat_id, operation_id, package = _started(database)
        validate_grounded_snapshot_identity(
            database,
            package=package,
            operation_id=operation_id,
        )
        validate_grounded_snapshot_current(
            database,
            package=package,
            operation_id=operation_id,
        )
    finally:
        database.stop()


def test_snapshot_identity_rejects_declared_sequence_drift(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _chats, _user, _chat_id, operation_id, package = _started(database)
        revision_id = package.current_user_ref().revision_id
        assert revision_id is not None
        wrong = _package(
            signature=_signature(database),
            operation_id=operation_id,
            revision_id=revision_id,
            snapshot_commit_seq=package.snapshot_commit_seq + 1,
        )
        with pytest.raises(
            GroundedSnapshotBindingError,
            match="snapshot sequence conflicts",
        ):
            validate_grounded_snapshot_identity(
                database,
                package=wrong,
                operation_id=operation_id,
            )
    finally:
        database.stop()


def test_snapshot_current_rejects_later_canonical_commit_without_corrupting_identity(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats, user, _chat_id, operation_id, package = _started(database)
        other_chat_id = chats.create_chat(actor_id=user)
        ChatService(chats).add_user_message(
            chat_id=other_chat_id,
            content="later canonical change",
        )

        validate_grounded_snapshot_identity(
            database,
            package=package,
            operation_id=operation_id,
        )
        with pytest.raises(
            GroundedSnapshotBindingError,
            match="Canonical state changed",
        ):
            validate_grounded_snapshot_current(
                database,
                package=package,
                operation_id=operation_id,
            )
    finally:
        database.stop()
