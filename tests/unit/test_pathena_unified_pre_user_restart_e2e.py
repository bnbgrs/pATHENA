from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.generation import ChatGenerationService
from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.chat.unified_resumable import UnifiedLocalChatService
from athena.chat.unified_send_plan import UnifiedSendPlanRepository
from athena.common.ids import new_uuid7
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
        yield "Recovered answer [MODEL-PRIOR]"


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


class _EmptyRetrieval:
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
    hybrid: _EmptyRetrieval,
    archive: _EmptyRetrieval,
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


def test_pre_user_crash_restarts_without_retrieval_or_duplicate_turns(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "athena.db"
    provider = _Provider()
    embedding = _EmbeddingProvider()
    hybrid = _EmptyRetrieval()
    archive = _EmptyRetrieval()
    operation_id = new_uuid7()
    content = "Recover the frozen pre-user operation."

    database = SQLiteDatabase(path)
    database.start()
    try:
        chat_id = ChatService(ChatRepository(database)).create_chat()
        service = _service(
            database,
            provider=provider,
            embedding=embedding,
            hybrid=hybrid,
            archive=archive,
        )

        def crash_before_user_operation(
            self: GroundedSendCoordinator,
            *args: object,
            **kwargs: object,
        ) -> object:
            del self, args, kwargs
            raise RuntimeError("synthetic crash before durable user operation")

        with monkeypatch.context() as scoped:
            scoped.setattr(
                GroundedSendCoordinator,
                "start",
                crash_before_user_operation,
            )
            with pytest.raises(
                RuntimeError,
                match="synthetic crash before durable user operation",
            ):
                _send(
                    service,
                    chat_id=chat_id,
                    operation_id=operation_id,
                    content=content,
                )

        plan = UnifiedSendPlanRepository(database).load(operation_id)
        assert plan is not None
        assert plan.operation_id == operation_id
        assert plan.chat_id == chat_id
        assert ChatRepository(database).load_chat(chat_id).messages == ()
        assert provider.calls == 0
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
        completed = _send(
            restarted,
            chat_id=chat_id,
            operation_id=operation_id,
            content=content,
        )

        assert provider.calls == 1
        assert (
            embedding.calls,
            hybrid.calls,
            hybrid.lexical_calls,
            archive.calls,
            archive.lexical_calls,
        ) == retrieval_counts
        messages = ChatRepository(database).load_chat(chat_id).messages
        assert len(messages) == 2
        assert messages[0].message_id == operation_id
        assert completed.processing_run.status == "succeeded"
        assert completed.context_package.request_id == operation_id
        reloaded_plan = UnifiedSendPlanRepository(database).load(operation_id)
        assert reloaded_plan == plan
    finally:
        database.stop()
