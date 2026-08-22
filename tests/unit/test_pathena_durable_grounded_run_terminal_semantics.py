from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.durable_grounded_generation import (
    DurableGroundedGenerationError,
    DurableGroundedGenerationService,
)
from athena.chat.generation import ChatGenerationService
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


class _InterruptingProvider:
    provider_id = "lm_studio"

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
    ) -> Iterator[str]:
        del model_id, messages, max_output_tokens, reasoning_mode
        raise KeyboardInterrupt
        yield "unreachable"


class _AnswerProvider:
    provider_id = "lm_studio"

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
    ) -> Iterator[str]:
        del model_id, messages, max_output_tokens, reasoning_mode
        yield "durable answer"


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


def _fixture(database: SQLiteDatabase, provider):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    fingerprint = build_chat_request_fingerprint(
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
    coordinator = GroundedSendCoordinator(database)
    started = coordinator.start(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=fingerprint,
    )
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
        context_configuration={"context_package_version": 1},
    )
    package = ContextPackageService.build_from_sections(
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
                revision_id=started.user_message.revision_id,
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
        snapshot_commit_seq=_commit_seq(database, started.user_message.revision_id),
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user,
        pipeline_version="terminal-semantics-test-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="terminal-semantics-test",
        prompt_template_version="1",
    )
    service = DurableGroundedGenerationService(
        ChatGenerationService(ChatService(chats), provider),
        coordinator,
    )
    return (
        chats,
        chat_id,
        operation_id,
        fingerprint,
        coordinator,
        started.user_message,
        package,
        run.processing_run_id,
        service,
    )


def test_keyboard_interrupt_cancels_processing_run(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        (
            _chats,
            chat_id,
            operation_id,
            fingerprint,
            coordinator,
            user_message,
            package,
            run_id,
            service,
        ) = _fixture(database, _InterruptingProvider())
        with pytest.raises(KeyboardInterrupt):
            service.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=user_message,
                context_package=package,
                processing_run_id=run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=lambda content, provider_id, model_id: "{}",
            )
        run = ModelRunRepository(database).load_run(run_id)
        assert run.status == "cancelled"
        assert run.finished_at_us is not None
        assert run.error_detail == "KeyboardInterrupt"
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.AMBIGUOUS
        assert coordinator.provider_attempts.load_result(operation_id) is None
    finally:
        database.stop()


def test_journaled_answer_keeps_run_succeeded_when_receipt_builder_fails(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        (
            _chats,
            chat_id,
            operation_id,
            fingerprint,
            coordinator,
            user_message,
            package,
            run_id,
            service,
        ) = _fixture(database, _AnswerProvider())

        def broken_receipt_builder(
            content: str,
            provider_id: str,
            model_id: str,
        ) -> str:
            del content, provider_id, model_id
            raise ValueError("receipt builder failed")

        with pytest.raises(
            DurableGroundedGenerationError,
            match="answer was journaled for recovery",
        ):
            service.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=user_message,
                context_package=package,
                processing_run_id=run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=broken_receipt_builder,
            )
        run = ModelRunRepository(database).load_run(run_id)
        assert run.status == "succeeded"
        assert run.finished_at_us is not None
        assert run.error_detail is None
        recorded = coordinator.provider_attempts.load_result(operation_id)
        assert recorded is not None
        assert recorded.assistant_content == "durable answer"
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.RESULT_AVAILABLE
    finally:
        database.stop()
