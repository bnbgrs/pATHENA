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
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.model.provenance import ModelRunRepository, ModelSignature
from athena.retrieval.context import ContextBuilderService
from athena.retrieval.context_package import (
    ContextPackage,
    ContextPackageBudget,
    ContextPackageService,
    ContextTokenEstimates,
)
from athena.storage.database import SQLiteDatabase


class _Provider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.calls = 0

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
    ) -> Iterator[str]:
        del model_id, messages, max_output_tokens, reasoning_mode
        self.calls += 1
        yield "must not execute"


def _model() -> ModelInfo:
    return ModelInfo(
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
    )


def _signature(database: SQLiteDatabase) -> ModelSignature:
    return ModelRunRepository(database).get_or_create_signature(
        model=_model(),
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )


def _user_commit_seq(database: SQLiteDatabase, user_message: ChatMessage) -> int:
    row = database.connection.execute(
        """
        SELECT c.commit_seq
        FROM revisions AS r
        JOIN commit_records AS c ON c.commit_id = r.commit_id
        WHERE r.revision_id = ?
        """,
        (uuid_to_blob(user_message.revision_id),),
    ).fetchone()
    assert row is not None
    return int(row["commit_seq"])


def _package(
    *,
    signature: ModelSignature,
    user_message: ChatMessage,
    snapshot_commit_seq: int,
) -> ContextPackage:
    context = ContextBuilderService().build_from_ranked(
        query=user_message.content or "request",
        results=(),
        max_estimated_tokens=300,
    )
    return ContextPackageService.build(
        model_signature=signature,
        context=context,
        system_text="PACKAGE SYSTEM",
        prior_messages=(),
        current_user_message=user_message,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=300,
            output_reserve=1000,
            safety_margin=200,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=10,
            context_tokens=context.estimated_tokens,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=snapshot_commit_seq,
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )


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


def test_foreign_processing_run_snapshot_is_fenced_before_provider(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
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

        signature = _signature(database)
        snapshot_commit_seq = _user_commit_seq(database, started.user_message)
        package = _package(
            signature=signature,
            user_message=started.user_message,
            snapshot_commit_seq=snapshot_commit_seq,
        )
        foreign_package = _package(
            signature=signature,
            user_message=started.user_message,
            snapshot_commit_seq=snapshot_commit_seq,
        )
        assert foreign_package.model_signature == package.model_signature
        assert foreign_package.run_snapshot() != package.run_snapshot()

        run = ModelRunRepository(database).start_run(
            run_type="chat.unified_local_context_package",
            trigger_actor_id=user,
            pipeline_version="durable-grounded-test-v1",
            input_snapshot=foreign_package.run_snapshot(),
            configuration={"context_package_version": 1},
            model_signature_id=signature.model_signature_id,
            prompt_template_id="durable-grounded-test",
            prompt_template_version="1",
        )
        provider = _Provider()
        generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(chats), provider),
            coordinator,
        )

        with pytest.raises(
            DurableGroundedGenerationError,
            match="ProcessingRun provenance",
        ):
            generation.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=started.user_message,
                context_package=package,
                processing_run_id=run.processing_run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=lambda content, provider_id, model_id: (
                    '{"assistant_text":"' + content + '"}'
                ),
            )

        assert provider.calls == 0
        assert coordinator.load_context_package(operation_id) is None
        assert coordinator.provider_attempts.load(operation_id) is None
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.RESUMABLE
        assert ModelRunRepository(database).load_run(run.processing_run_id).status == "running"
    finally:
        database.stop()
