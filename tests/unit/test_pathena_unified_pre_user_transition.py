from __future__ import annotations

from pathlib import Path

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_pre_user_transition import (
    UnifiedPreUserTransitionError,
    UnifiedPreUserTransitionService,
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


def _fingerprint(chat_id, content: str):
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


def _freeze_plan(database: SQLiteDatabase, *, content: str = "hello"):
    chats = ChatRepository(database)
    actor_id = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=actor_id)
    model = ModelInfo(
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
    signature = ModelRunRepository(database).get_or_create_signature(
        model=model,
        generation_parameters={"max_output_tokens": 1000, "reasoning_mode": "off"},
        context_configuration={
            "embedding_model_id": None,
            "evidence_policy_id": MEMORY_EVIDENCE_POLICY_ID,
        },
    )
    operation_id = new_uuid7()
    fingerprint = _fingerprint(chat_id, content)
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
        memory_context=ContextBundle(
            query=content,
            mode="lexical",
            memory_items=(),
            items=(),
            omitted_memory_count=0,
            omitted_count=0,
            estimated_tokens=1,
            max_estimated_tokens=300,
            rendered_text="NO MEMORY EVIDENCE",
        ),
        source_context=SourceContextBundle(
            query=content,
            mode="archive_hybrid",
            items=(),
            omitted_count=0,
            estimated_tokens=1,
            max_estimated_tokens=300,
            rendered_text="NO SOURCE EVIDENCE",
        ),
        evidence_selection=MemoryEvidenceSelection(
            policy_id=MEMORY_EVIDENCE_POLICY_ID,
            results=(),
            classifications=(),
        ),
    )
    return actor_id, chat_id, operation_id, fingerprint, plan


def test_transition_consumes_ready_plan_with_exact_user_identity(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        actor_id, chat_id, operation_id, fingerprint, plan = _freeze_plan(database)
        transition = UnifiedPreUserTransitionService(database).start(
            operation_id=operation_id,
            chat_id=chat_id,
            content="hello",
            fingerprint=fingerprint,
        )
        assert transition.plan == plan
        assert transition.user_message.message_id == operation_id
        assert transition.user_message.actor_id == actor_id
        assert transition.package_snapshot_commit_seq == plan.retrieval_snapshot_commit_seq + 1

        status = UnifiedPreUserRecoveryInspector(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is UnifiedPreUserRecoveryState.CONSUMED
    finally:
        database.stop()


def test_transition_refuses_plan_after_snapshot_drift(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        actor_id, chat_id, operation_id, fingerprint, _ = _freeze_plan(database)
        chats = ChatRepository(database)
        other_chat_id = chats.create_chat(actor_id=actor_id)
        assert other_chat_id != chat_id

        with pytest.raises(UnifiedPreUserTransitionError, match="state=conflict"):
            UnifiedPreUserTransitionService(database).start(
                operation_id=operation_id,
                chat_id=chat_id,
                content="hello",
                fingerprint=fingerprint,
            )
        assert chats.load_chat(chat_id).messages == ()
    finally:
        database.stop()
