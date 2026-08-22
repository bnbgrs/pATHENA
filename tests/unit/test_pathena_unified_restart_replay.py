from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.generation import ChatGenerationService
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedSendRecovery
from athena.chat.models import ChatMessage
from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.chat.unified import (
    UnifiedGroundedRecoveryRequiredError,
    UnifiedLocalChatService,
)
from athena.chat.unified_durable import build_unified_grounded_fingerprint
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBuilderService
from athena.retrieval.context_package import ContextPackageService
from athena.retrieval.evidence import MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBuilderService
from athena.storage.database import SQLiteDatabase


class _Provider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.calls = 0
        self.model = ModelInfo(
            provider="lm_studio",
            backend_model_id="primary",
            display_name="primary",
            model_type="llm",
            context_capacity=32768,
            quantization="Q4_K_M",
            loaded=True,
            vision=False,
            trained_for_tool_use=False,
            loaded_context_length=8192,
        )

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (self.model,)

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        del messages, max_output_tokens, reasoning_mode, temperature
        assert model_id == "primary"
        self.calls += 1
        yield "Replay answer [MODEL-PRIOR]"


class _EmbeddingProvider:
    def __init__(self) -> None:
        self.calls = 0
        self.model = ModelInfo(
            provider="lm_studio",
            backend_model_id="embed",
            display_name="embed",
            model_type="embedding",
            context_capacity=2048,
            quantization=None,
            loaded=True,
            vision=False,
            trained_for_tool_use=False,
            loaded_context_length=2048,
        )

    def resolve_model(self, requested_model_id: str | None = None) -> ModelInfo:
        self.calls += 1
        assert requested_model_id == "embed"
        return self.model


class _EmptyHybridRetrieval:
    def __init__(self) -> None:
        self.calls = 0
        self.lexical_calls = 0

    def search(self, *args: object, **kwargs: object) -> tuple[()]:
        del args, kwargs
        self.calls += 1
        return ()

    def search_lexical(self, *args: object, **kwargs: object) -> tuple[()]:
        del args, kwargs
        self.lexical_calls += 1
        return ()


class _EmptyArchiveRetrieval:
    def __init__(self) -> None:
        self.calls = 0
        self.lexical_calls = 0

    def search(self, *args: object, **kwargs: object) -> tuple[()]:
        del args, kwargs
        self.calls += 1
        return ()

    def search_lexical(self, *args: object, **kwargs: object) -> tuple[()]:
        del args, kwargs
        self.lexical_calls += 1
        return ()


class _EmptyEvidencePolicy:
    def classify(self, results: tuple[object, ...]) -> MemoryEvidenceSelection:
        assert results == ()
        return MemoryEvidenceSelection(
            policy_id="typed-provenance-v1",
            results=(),
            classifications=(),
        )


class _EmptyPersonalMemory:
    def context_candidates(
        self,
        *,
        scope_kind: object = None,
        scope_entity_id: uuid.UUID | None = None,
        limit: int = 32,
    ) -> tuple[()]:
        del scope_kind, scope_entity_id, limit
        return ()


class _UnusedAnchors:
    def verify(self, anchor_id: uuid.UUID) -> None:
        raise AssertionError(f"unexpected SourceAnchor verify: {anchor_id}")

    def read_text(self, anchor_id: uuid.UUID) -> str:
        raise AssertionError(f"unexpected SourceAnchor read: {anchor_id}")

    def materialize_text_range(
        self,
        representation_id: uuid.UUID,
        *,
        start_offset: int,
        end_offset: int,
    ) -> None:
        raise AssertionError(
            "unexpected SourceAnchor materialization: "
            f"{representation_id}:{start_offset}:{end_offset}"
        )


def _service(
    database: SQLiteDatabase,
    *,
    provider: _Provider,
    embedding: _EmbeddingProvider,
    hybrid: _EmptyHybridRetrieval,
    archive: _EmptyArchiveRetrieval,
) -> UnifiedLocalChatService:
    chat = ChatService(ChatRepository(database))
    generation = ChatGenerationService(chat, provider)
    return UnifiedLocalChatService(
        chat_generation=generation,
        embedding_provider=embedding,  # type: ignore[arg-type]
        hybrid_retrieval=hybrid,  # type: ignore[arg-type]
        memory_context_builder=ContextBuilderService(),
        evidence_policy=_EmptyEvidencePolicy(),  # type: ignore[arg-type]
        personal_memory=_EmptyPersonalMemory(),  # type: ignore[arg-type]
        archive_retrieval=archive,  # type: ignore[arg-type]
        source_context_builder=SourceContextBuilderService(
            _UnusedAnchors()  # type: ignore[arg-type]
        ),
        context_packages=ContextPackageService(database),
        model_runs=ModelRunRepository(database),
    )


def _fingerprint(chat_id: uuid.UUID, content: str):
    return build_unified_grounded_fingerprint(
        chat_id=chat_id,
        content=content,
        retrieval_query_override=None,
        requested_model_id="primary",
        requested_embedding_model_id="embed",
        max_memory_context_tokens=1200,
        max_memory_context_items=8,
        max_memory_items=8,
        max_source_context_tokens=1200,
        max_source_context_items=8,
        max_recent_conversation_turns=8,
        memory_scope_kind=None,
        memory_scope_entity_id=None,
        effective_context_limit=None,
        output_reserve=2048,
        safety_margin=256,
        temperature=None,
        reasoning_mode="off",
        allow_model_prior=True,
    )


def _send(
    service: UnifiedLocalChatService,
    *,
    chat_id: uuid.UUID,
    operation_id: uuid.UUID,
    content: str,
):
    return service.send_message(
        chat_id=chat_id,
        content=content,
        requested_model_id="primary",
        requested_embedding_model_id="embed",
        operation_id=operation_id,
    )


def test_unified_complete_retry_replays_exact_result_without_live_retrieval(
    tmp_path: Path,
) -> None:
    path = tmp_path / "athena.db"
    provider = _Provider()
    embedding = _EmbeddingProvider()
    hybrid = _EmptyHybridRetrieval()
    archive = _EmptyArchiveRetrieval()
    operation_id = uuid.uuid4()
    content = "Give me the durable replay answer."

    database = SQLiteDatabase(path)
    database.start()
    try:
        chats = ChatService(ChatRepository(database))
        chat_id = chats.create_chat()
        service = _service(
            database,
            provider=provider,
            embedding=embedding,
            hybrid=hybrid,
            archive=archive,
        )
        initial = _send(
            service,
            chat_id=chat_id,
            operation_id=operation_id,
            content=content,
        )
        assert provider.calls == 1
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
        first_recovery = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=_fingerprint(chat_id, content),
        )
        assert first_recovery.state in {
            GroundedRecoveryState.FINALIZATION_REQUIRED,
            GroundedRecoveryState.COMPLETE,
        }
        retrieval_counts = (
            embedding.calls,
            hybrid.calls,
            hybrid.lexical_calls,
            archive.calls,
            archive.lexical_calls,
        )

        database.stop()
        database = SQLiteDatabase(path)
        database.start()
        restarted = _service(
            database,
            provider=provider,
            embedding=embedding,
            hybrid=hybrid,
            archive=archive,
        )
        replayed = _send(
            restarted,
            chat_id=chat_id,
            operation_id=operation_id,
            content=content,
        )

        assert replayed == initial
        assert provider.calls == 1
        assert (
            embedding.calls,
            hybrid.calls,
            hybrid.lexical_calls,
            archive.calls,
            archive.lexical_calls,
        ) == retrieval_counts
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
        complete = GroundedSendRecovery(database).inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=_fingerprint(chat_id, content),
        )
        assert complete.state is GroundedRecoveryState.COMPLETE
        assert complete.processing_run_id == initial.processing_run.processing_run_id
        assert complete.receipt is not None
        assert complete.provider_result is not None
        assert complete.provider_result.processing_run_id == (
            initial.processing_run.processing_run_id
        )
    finally:
        database.stop()


def test_unified_same_operation_with_different_content_fails_closed(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        provider = _Provider()
        embedding = _EmbeddingProvider()
        hybrid = _EmptyHybridRetrieval()
        archive = _EmptyArchiveRetrieval()
        chat_id = ChatService(ChatRepository(database)).create_chat()
        operation_id = uuid.uuid4()
        service = _service(
            database,
            provider=provider,
            embedding=embedding,
            hybrid=hybrid,
            archive=archive,
        )
        _send(
            service,
            chat_id=chat_id,
            operation_id=operation_id,
            content="original request",
        )
        calls_after_first_send = provider.calls

        with pytest.raises(UnifiedGroundedRecoveryRequiredError) as exc_info:
            _send(
                service,
                chat_id=chat_id,
                operation_id=operation_id,
                content="different request",
            )

        assert exc_info.value.status.state is GroundedRecoveryState.CONFLICT
        assert provider.calls == calls_after_first_send
        assert len(ChatRepository(database).load_chat(chat_id).messages) == 2
    finally:
        database.stop()
