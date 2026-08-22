from __future__ import annotations

import json
import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.durable_grounded_generation import (
    DurableGroundedGenerationError,
    DurableGroundedGenerationService,
)
from athena.chat.generation import ChatGenerationService
from athena.chat.grounded_recovery import (
    GroundedRecoveryConflictError,
    GroundedRecoveryState,
    GroundedSendRecovery,
)
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.model.domain import ModelChatMessage, ModelInfo, ProviderHealth, ProviderHealthStatus
from athena.model.provenance import ModelRunRepository
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

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (
            ModelInfo(
                provider=self.provider_id,
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
        )

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
    ) -> Iterator[str]:
        del messages
        assert model_id == "primary"
        assert max_output_tokens == 1000
        assert reasoning_mode == "off"
        self.calls += 1
        yield "durable answer"


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


def _package_and_run(
    database: SQLiteDatabase,
    user_message: ChatMessage,
) -> tuple[ContextPackage, uuid.UUID]:
    if user_message.actor_id is None:
        raise AssertionError("Test user message must have an actor.")
    model_runs = ModelRunRepository(database)
    signature = model_runs.get_or_create_signature(
        model=_Provider().discover_models()[0],
        generation_parameters={
            "max_output_tokens": 1000,
            "reasoning_mode": "off",
        },
        context_configuration={"context_package_version": 1},
    )
    context = ContextBuilderService().build_from_ranked(
        query=user_message.content or "request",
        results=(),
        max_estimated_tokens=300,
    )
    package = ContextPackageService.build(
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
        snapshot_commit_seq=_user_commit_seq(database, user_message),
        retrieval_candidate_count=0,
        memory_candidate_count=0,
    )
    run = model_runs.start_run(
        run_type="chat.unified_local_context_package",
        trigger_actor_id=user_message.actor_id,
        pipeline_version="grounded-restart-no-replay-v1",
        input_snapshot=package.run_snapshot(),
        configuration={"context_package_version": 1},
        model_signature_id=signature.model_signature_id,
        prompt_template_id="grounded-restart-no-replay",
        prompt_template_version="1",
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


def _receipt_payload(content: str, provider_id: str, model_id: str) -> str:
    return json.dumps(
        {
            "assistant_text": content,
            "provider_id": provider_id,
            "model_id": model_id,
        }
    )


def test_restart_normal_send_path_cannot_replay_recorded_provider_result(
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    provider = _Provider()
    operation_id = uuid.uuid4()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        fingerprint = _fingerprint(chat_id)
        coordinator = GroundedSendCoordinator(database)
        started = coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        package, processing_run_id = _package_and_run(database, started.user_message)
        generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(chats), provider),
            coordinator,
        )

        first = generation.send_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            user_message=started.user_message,
            context_package=package,
            processing_run_id=processing_run_id,
            fingerprint=fingerprint,
            receipt_payload_builder=_receipt_payload,
        )
        assert provider.calls == 1
        assert first.assistant_message.content == "durable answer"
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.FINALIZATION_REQUIRED
        assert len(chats.load_chat(chat_id).messages) == 2

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        restarted_chats = ChatRepository(database)
        restarted_coordinator = GroundedSendCoordinator(database)
        restarted_generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(restarted_chats), provider),
            restarted_coordinator,
        )
        persisted_chat = restarted_chats.load_chat(chat_id)
        persisted_user = next(
            message for message in persisted_chat.messages if message.message_id == operation_id
        )

        with pytest.raises(
            DurableGroundedGenerationError,
            match="not safely resumable",
        ):
            restarted_generation.send_context_package(
                operation_id=operation_id,
                chat_id=chat_id,
                user_message=persisted_user,
                context_package=package,
                processing_run_id=processing_run_id,
                fingerprint=fingerprint,
                receipt_payload_builder=_receipt_payload,
            )

        assert provider.calls == 1
        assert len(restarted_chats.load_chat(chat_id).messages) == 2
        pending = restarted_coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert pending.state is GroundedRecoveryState.FINALIZATION_REQUIRED
        assert pending.provider_result is not None
        assert pending.provider_result.operation_id == operation_id
        assert pending.provider_result.processing_run_id == processing_run_id

        recovery = GroundedSendRecovery(database)
        receipt = recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert receipt.operation_id == operation_id
        assert receipt.chat_id == chat_id
        assert receipt.processing_run_id == processing_run_id
        assert provider.calls == 1
        complete = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert complete.state is GroundedRecoveryState.COMPLETE
        assert complete.receipt == receipt
        assert len(restarted_chats.load_chat(chat_id).messages) == 2
        run = ModelRunRepository(database).load_run(processing_run_id)
        assert run.status == "succeeded"
    finally:
        database.stop()


def test_restart_inspect_rejects_corrupted_provider_processing_run(
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    provider = _Provider()
    operation_id = uuid.uuid4()
    try:
        chats = ChatRepository(database)
        user = chats.create_actor(actor_type="user")
        chat_id = chats.create_chat(actor_id=user)
        fingerprint = _fingerprint(chat_id)
        coordinator = GroundedSendCoordinator(database)
        started = coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=user,
            content="hello",
            fingerprint=fingerprint,
        )
        package, processing_run_id = _package_and_run(database, started.user_message)
        generation = DurableGroundedGenerationService(
            ChatGenerationService(ChatService(chats), provider),
            coordinator,
        )
        generation.send_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            user_message=started.user_message,
            context_package=package,
            processing_run_id=processing_run_id,
            fingerprint=fingerprint,
            receipt_payload_builder=_receipt_payload,
        )
        assert provider.calls == 1
        assert coordinator.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        ).state is GroundedRecoveryState.FINALIZATION_REQUIRED

        foreign_processing_run_id = uuid.uuid4()
        with database.write_transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE grounded_provider_results
                SET processing_run_id = ?
                WHERE operation_id = ?
                """,
                (
                    uuid_to_blob(foreign_processing_run_id),
                    uuid_to_blob(operation_id),
                ),
            )
            assert cursor.rowcount == 1

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        recovery = GroundedSendRecovery(database)
        status = recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        assert status.state is GroundedRecoveryState.CONFLICT
        with pytest.raises(
            GroundedRecoveryConflictError,
            match="cannot finalize from conflict",
        ):
            recovery.finalize_recorded_result(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
        assert provider.calls == 1
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
        run = ModelRunRepository(database).load_run(processing_run_id)
        assert run.status == "succeeded"
    finally:
        database.stop()
