from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.direct import DirectChatService
from athena.chat.generation import ChatGenerationService, GenerationCancelledError
from athena.chat.models import MessageType
from athena.chat.repository import ChatRepository
from athena.chat.send_identity import (
    SendOperationState,
    SendOperationStateError,
    assistant_message_id_for_operation,
)
from athena.chat.service import ChatService
from athena.model.domain import (
    ModelChatMessage,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context_package import ContextPackageService
from athena.storage.database import SQLiteDatabase

_OPERATION_ID = uuid.UUID(
    "11111111-2222-4333-8444-555555555555"
)


class _Provider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.discover_calls = 0
        self.stream_calls = 0

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            ProviderHealthStatus.READY
        )

    def discover_models(
        self,
    ) -> tuple[ModelInfo, ...]:
        self.discover_calls += 1

        return (
            ModelInfo(
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
        )

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        del messages

        assert model_id == "primary"
        assert max_output_tokens == 1000
        assert reasoning_mode == "off"
        assert temperature is None

        self.stream_calls += 1

        yield "direct answer"


def _runtime(
    tmp_path: Path,
) -> tuple[
    SQLiteDatabase,
    ChatService,
    _Provider,
    DirectChatService,
]:
    database = SQLiteDatabase(
        tmp_path / "athena.db"
    )
    database.start()

    provider = _Provider()

    chat = ChatService(
        ChatRepository(database)
    )

    generation = ChatGenerationService(
        chat,
        provider,
    )

    service = DirectChatService(
        chat_generation=generation,
        context_packages=ContextPackageService(
            database
        ),
        model_runs=ModelRunRepository(
            database
        ),
    )

    return (
        database,
        chat,
        provider,
        service,
    )


def test_direct_send_operation_persists_stable_turn_ids_and_blocks_reexecution(
    tmp_path: Path,
) -> None:
    (
        database,
        chat,
        provider,
        service,
    ) = _runtime(tmp_path)

    try:
        chat_id = chat.create_chat()

        result = service.send_message(
            chat_id=chat_id,
            content="hello",
            requested_model_id="primary",
            operation_id=_OPERATION_ID,
            output_reserve=1000,
            safety_margin=100,
        )

        assert (
            result.generation.user_message.message_id
            == _OPERATION_ID
        )

        assert (
            result.generation.assistant_message.message_id
            == assistant_message_id_for_operation(
                _OPERATION_ID
            )
        )

        status = chat.inspect_send_operation(
            chat_id=chat_id,
            operation_id=_OPERATION_ID,
            content="hello",
        )

        assert (
            status.state
            is SendOperationState.COMPLETE
        )

        assert provider.stream_calls == 1

        with pytest.raises(
            SendOperationStateError
        ) as raised:
            service.send_message(
                chat_id=chat_id,
                content="hello",
                requested_model_id="primary",
                operation_id=_OPERATION_ID,
                output_reserve=1000,
                safety_margin=100,
            )

        assert (
            raised.value.status.state
            is SendOperationState.COMPLETE
        )

        assert provider.stream_calls == 1

        persisted = (
            chat.load_chat(
                chat_id
            ).messages
        )

        assert len(persisted) == 2

        assert [
            message.message_id
            for message in persisted
        ] == [
            _OPERATION_ID,
            assistant_message_id_for_operation(
                _OPERATION_ID
            ),
        ]

    finally:
        database.stop()


def test_explicit_cancel_between_chunks_marks_run_cancelled_and_keeps_user_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, chat, provider, service = _runtime(tmp_path)

    try:
        chat_id = chat.create_chat()
        provider.stream_chat = _two_chunk_stream(provider)  # type: ignore[method-assign]
        finished_statuses: list[str] = []
        original_finish = service.model_runs.finish_run

        def finish_run(
            processing_run_id: uuid.UUID,
            *,
            status: str,
            error_detail: str | None = None,
        ):
            finished_statuses.append(status)
            return original_finish(
                processing_run_id,
                status=status,
                error_detail=error_detail,
            )

        monkeypatch.setattr(service.model_runs, "finish_run", finish_run)
        checks = 0

        def cancel_requested() -> bool:
            nonlocal checks
            checks += 1
            return checks >= 5

        with pytest.raises(GenerationCancelledError):
            service.send_message(
                chat_id=chat_id,
                content="cancel after first chunk",
                requested_model_id="primary",
                operation_id=_OPERATION_ID,
                output_reserve=1000,
                safety_margin=100,
                cancel_requested=cancel_requested,
            )

        persisted = chat.load_chat(chat_id).messages
        assert [message.message_type for message in persisted] == [
            MessageType.USER,
        ]
        assert persisted[0].content == "cancel after first chunk"
        assert finished_statuses == ["cancelled"]
        assert provider.stream_calls == 1
    finally:
        database.stop()


def _two_chunk_stream(provider: _Provider):
    def stream_chat(
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        del messages
        assert model_id == "primary"
        assert max_output_tokens == 1000
        assert reasoning_mode == "off"
        assert temperature is None
        provider.stream_calls += 1
        yield "partial"
        yield " should not persist"

    return stream_chat


def test_direct_send_operation_incomplete_fails_closed_before_provider(
    tmp_path: Path,
) -> None:
    (
        database,
        chat,
        provider,
        service,
    ) = _runtime(tmp_path)

    try:
        chat_id = chat.create_chat()

        chat.add_user_message(
            chat_id=chat_id,
            content="hello",
            operation_id=_OPERATION_ID,
        )

        assert provider.discover_calls == 0
        assert provider.stream_calls == 0

        with pytest.raises(
            SendOperationStateError
        ) as raised:
            service.send_message(
                chat_id=chat_id,
                content="hello",
                requested_model_id="primary",
                operation_id=_OPERATION_ID,
                output_reserve=1000,
                safety_margin=100,
            )

        assert (
            raised.value.status.state
            is SendOperationState.INCOMPLETE
        )

        assert provider.discover_calls == 0
        assert provider.stream_calls == 0

        persisted = (
            chat.load_chat(
                chat_id
            ).messages
        )

        assert len(persisted) == 1
        assert (
            persisted[0].message_id
            == _OPERATION_ID
        )

    finally:
        database.stop()
