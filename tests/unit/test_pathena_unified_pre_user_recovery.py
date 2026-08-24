from __future__ import annotations

from pathlib import Path

from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_send_plan import UnifiedSendPlanRepository
from athena.common.ids import new_uuid7
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBundle
from athena.retrieval.context_package import ContextPackageService
from athena.retrieval.evidence import MEMORY_EVIDENCE_POLICY_ID, MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBundle
from athena.storage.database import SQLiteDatabase


def _model() -> ModelInfo:
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


def _fingerprint(chat_id, content: str = "hello"):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content=content,
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


def _store_plan(database: SQLiteDatabase):
    chats = ChatRepository(database)
    actor_id = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor_id)
    model = _model()
    signature = ModelRunRepository(database).get_or_create_signature(
        model=model,
        generation_parameters={"max_output_tokens": 1000, "reasoning_mode": "off"},
        context_configuration={
            "embedding_model_id": None,
            "evidence_policy_id": MEMORY_EVIDENCE_POLICY_ID,
        },
    )
    operation_id = new_uuid7()
    fingerprint = _fingerprint(chat_id)
    plan = UnifiedSendPlanRepository(database).store(
        operation_id=operation_id,
        chat_id=chat_id,
        fingerprint=fingerprint,
        user_actor_id=actor_id,
        retrieval_snapshot_commit_seq=ContextPackageService(database).current_commit_seq(),
        model_signature_id=signature.model_signature_id,
        retrieval_query_override=None,
        primary_model=model,
        embedding_model=None,
        memory_context=_memory_context(),
        source_context=_source_context(),
        evidence_selection=MemoryEvidenceSelection(
            policy_id=MEMORY_EVIDENCE_POLICY_ID,
            results=(),
            classifications=(),
        ),
    )
    return actor_id, chat_id, operation_id, fingerprint, plan


def test_pre_user_recovery_reports_absent_without_plan(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        actor_id = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=actor_id)
        operation_id = new_uuid7()
        status = UnifiedPreUserRecoveryInspector(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=_fingerprint(chat_id),
        )
        assert status.state is UnifiedPreUserRecoveryState.ABSENT
        assert status.plan is None
    finally:
        database.stop()


def test_pre_user_recovery_reports_ready_for_frozen_plan(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        _, chat_id, operation_id, fingerprint, plan = _store_plan(database)
        status = UnifiedPreUserRecoveryInspector(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is UnifiedPreUserRecoveryState.READY
        assert status.plan == plan
    finally:
        database.stop()


def test_pre_user_recovery_reports_consumed_after_user_operation(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        actor_id, chat_id, operation_id, fingerprint, plan = _store_plan(database)
        GroundedSendCoordinator(database).start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content="hello",
            fingerprint=fingerprint,
        )
        status = UnifiedPreUserRecoveryInspector(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is UnifiedPreUserRecoveryState.CONSUMED
        assert status.plan == plan
    finally:
        database.stop()


def test_pre_user_recovery_rejects_snapshot_drift(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        actor_id, chat_id, operation_id, fingerprint, plan = _store_plan(database)
        GroundedSendCoordinator(database).start(
            operation_id=new_uuid7(),
            chat_id=chat_id,
            actor_id=actor_id,
            content="intervening commit",
            fingerprint=_fingerprint(chat_id, "intervening commit"),
        )
        status = UnifiedPreUserRecoveryInspector(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is UnifiedPreUserRecoveryState.CONFLICT
        assert status.plan == plan
        assert status.reason is not None
        assert "Canonical state changed" in status.reason
    finally:
        database.stop()
