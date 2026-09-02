from __future__ import annotations

from pathlib import Path

from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.unified_pre_user_resume import UnifiedPreUserResumeMaterializer
from athena.chat.unified_send_plan import UnifiedSendPlanRepository
from athena.common.ids import new_uuid7
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBundle
from athena.retrieval.context_package import ContextPackageService
from athena.retrieval.evidence import MEMORY_EVIDENCE_POLICY_ID, MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBundle
from athena.storage.database import SQLiteDatabase


def test_pre_user_resume_materializes_pinned_package_without_retrieval(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chats = ChatRepository(database)
        actor_id = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=actor_id)
        content = "hello"
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
                "context_package_version": 1,
                "mode": "unified_local_chat",
                "effective_context_limit": 4096,
                "memory_context_budget": 300,
                "source_context_budget": 300,
                "max_recent_conversation_turns": 8,
                "safety_margin": 256,
                "embedding_model_id": None,
                "evidence_policy_id": MEMORY_EVIDENCE_POLICY_ID,
                "epistemic_grounding_version": 1,
                "response_language_policy_version": 1,
                "allow_model_prior": True,
            },
        )
        operation_id = new_uuid7()
        fingerprint = build_chat_request_fingerprint(
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
        snapshot_seq = ContextPackageService(database).current_commit_seq()
        plan = UnifiedSendPlanRepository(database).store(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            user_actor_id=actor_id,
            retrieval_snapshot_commit_seq=snapshot_seq,
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

        materialized = UnifiedPreUserResumeMaterializer(database).materialize(
            operation_id=operation_id,
            chat_id=chat_id,
            content=content,
            fingerprint=fingerprint,
        )

        assert materialized.plan == plan
        assert materialized.user_message.message_id == operation_id
        assert materialized.user_message.actor_id == actor_id
        assert materialized.package.model_signature.model_signature_id == signature.model_signature_id
        assert materialized.package.snapshot_commit_seq == snapshot_seq + 1
        assert materialized.package.current_user_ref().entity_id == operation_id
        assert materialized.package.budget.effective_context_limit == 4096
        assert materialized.package.budget.context_budget == 600
        assert materialized.package.budget.output_reserve == 1000
        assert materialized.package.budget.safety_margin == 256
        assert materialized.package.sections[-1].name == "current_user"
        assert materialized.package.sections[-1].content == content
        assert len(chats.load_chat(chat_id).messages) == 1
    finally:
        database.stop()
