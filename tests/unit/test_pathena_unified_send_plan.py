from __future__ import annotations

from pathlib import Path

import pytest

from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.unified_send_plan import (
    UnifiedSendPlanConflictError,
    UnifiedSendPlanRepository,
    UnifiedSendPlanSchemaError,
)
from athena.common.ids import new_uuid7, uuid_to_blob
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBundle
from athena.retrieval.evidence import MEMORY_EVIDENCE_POLICY_ID, MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBundle
from athena.storage.database import SQLiteDatabase


def _primary_model() -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="primary",
        display_name="Primary",
        model_type="llm",
        context_capacity=32768,
        quantization="Q4_K_M",
        loaded=True,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=4096,
    )


def _fingerprint(chat_id):
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
        retrieval_configuration={"memory_limit": 8, "source_limit": 8},
    )


def _memory_context() -> ContextBundle:
    return ContextBundle(
        query="hello",
        mode="lexical",
        memory_items=(),
        items=(),
        omitted_memory_count=0,
        omitted_count=0,
        estimated_tokens=1,
        max_estimated_tokens=300,
        rendered_text="NO MEMORY EVIDENCE",
    )


def _source_context() -> SourceContextBundle:
    return SourceContextBundle(
        query="hello",
        mode="archive_hybrid",
        items=(),
        omitted_count=0,
        estimated_tokens=1,
        max_estimated_tokens=300,
        rendered_text="NO SOURCE EVIDENCE",
    )


def _evidence() -> MemoryEvidenceSelection:
    return MemoryEvidenceSelection(
        policy_id=MEMORY_EVIDENCE_POLICY_ID,
        results=(),
        classifications=(),
    )


def _fixture(database: SQLiteDatabase):
    chats = ChatRepository(database)
    actor_id = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor_id)
    model = _primary_model()
    signature = ModelRunRepository(database).get_or_create_signature(
        model=model,
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={
            "embedding_model_id": None,
            "evidence_policy_id": MEMORY_EVIDENCE_POLICY_ID,
        },
    )
    return chats, actor_id, chat_id, model, signature.model_signature_id


def _store(
    repository: UnifiedSendPlanRepository,
    *,
    operation_id,
    chat_id,
    fingerprint,
    actor_id,
    model,
    model_signature_id,
    retrieval_query_override=None,
):
    return repository.store(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        user_actor_id=actor_id,
        retrieval_snapshot_commit_seq=0,
        model_signature_id=model_signature_id,
        retrieval_query_override=retrieval_query_override,
        primary_model=model,
        embedding_model=None,
        memory_context=_memory_context(),
        source_context=_source_context(),
        evidence_selection=_evidence(),
    )


def test_unified_send_plan_survives_restart_and_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    try:
        _, actor_id, chat_id, model, signature_id = _fixture(database)
        operation_id = new_uuid7()
        fingerprint = _fingerprint(chat_id)
        repository = UnifiedSendPlanRepository(database)

        first = _store(
            repository,
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            actor_id=actor_id,
            model=model,
            model_signature_id=signature_id,
        )
        second = _store(
            repository,
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            actor_id=actor_id,
            model=model,
            model_signature_id=signature_id,
        )
        assert second == first

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        restarted = UnifiedSendPlanRepository(database).load(
            operation_id,
            fingerprint=fingerprint,
        )
        assert restarted == first
        assert restarted is not None
        assert restarted.operation_id == operation_id
        assert restarted.chat_id == chat_id
        assert restarted.user_actor_id == actor_id
        assert restarted.projection.primary_model.backend_model_id == "primary"
    finally:
        database.stop()


def test_unified_send_plan_rejects_conflicting_operation_reuse(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, actor_id, chat_id, model, signature_id = _fixture(database)
        operation_id = new_uuid7()
        fingerprint = _fingerprint(chat_id)
        repository = UnifiedSendPlanRepository(database)
        _store(
            repository,
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            actor_id=actor_id,
            model=model,
            model_signature_id=signature_id,
        )

        with pytest.raises(
            UnifiedSendPlanConflictError,
            match="different pre-user send plan",
        ):
            _store(
                repository,
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                actor_id=actor_id,
                model=model,
                model_signature_id=signature_id,
                retrieval_query_override="different-query",
            )

        different_request = build_chat_request_fingerprint(
            mode=ChatSendMode.GROUNDED,
            chat_id=chat_id,
            content="different",
            requested_model_id="primary",
            requested_embedding_model_id=None,
            effective_context_limit=4096,
            max_output_tokens=1000,
            temperature=None,
            reasoning_mode="off",
            retrieval_configuration={"memory_limit": 8, "source_limit": 8},
        )
        with pytest.raises(UnifiedSendPlanConflictError, match="retry request conflicts"):
            repository.load(operation_id, fingerprint=different_request)
    finally:
        database.stop()


def test_unified_send_plan_detects_payload_corruption(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, actor_id, chat_id, model, signature_id = _fixture(database)
        operation_id = new_uuid7()
        fingerprint = _fingerprint(chat_id)
        repository = UnifiedSendPlanRepository(database)
        _store(
            repository,
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            actor_id=actor_id,
            model=model,
            model_signature_id=signature_id,
        )
        with database.write_transaction() as connection:
            connection.execute(
                "UPDATE unified_grounded_send_plans SET payload_json = ? WHERE operation_id = ?",
                ("{}", uuid_to_blob(operation_id)),
            )

        with pytest.raises(UnifiedSendPlanSchemaError, match="payload hash"):
            repository.load(operation_id, fingerprint=fingerprint)
    finally:
        database.stop()


def test_unified_send_plan_cannot_be_created_after_user_operation(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, actor_id, chat_id, model, signature_id = _fixture(database)
        operation_id = new_uuid7()
        fingerprint = _fingerprint(chat_id)
        GroundedSendCoordinator(database).start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content="hello",
            fingerprint=fingerprint,
        )

        with pytest.raises(UnifiedSendPlanConflictError, match="before the user operation"):
            _store(
                UnifiedSendPlanRepository(database),
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
                actor_id=actor_id,
                model=model,
                model_signature_id=signature_id,
            )
    finally:
        database.stop()
