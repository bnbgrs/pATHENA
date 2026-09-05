from __future__ import annotations

import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from athena.chat.direct import DirectChatService
from athena.chat.generation import ChatGenerationService
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

    def __init__(
        self,
        *,
        loaded_context_length: int = 4096,
        expected_output_tokens: int = 1000,
    ) -> None:
        self.discover_calls = 0
        self.stream_calls = 0
        self.loaded_context_length = loaded_context_length
        self.expected_output_tokens = expected_output_tokens
        self.requests: list[tuple[ModelChatMessage, ...]] = []

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
                loaded_context_length=self.loaded_context_length,
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
        assert model_id == "primary"
        assert max_output_tokens == self.expected_output_tokens
        assert reasoning_mode == "off"
        assert temperature is None

        self.stream_calls += 1
        self.requests.append(tuple(messages))

        yield "direct answer"


def _runtime(
    tmp_path: Path,
    *,
    loaded_context_length: int = 4096,
    expected_output_tokens: int = 1000,
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

    provider = _Provider(
        loaded_context_length=loaded_context_length,
        expected_output_tokens=expected_output_tokens,
    )

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


def test_default_direct_chat_adapts_output_reserve_to_2048_loaded_context(
    tmp_path: Path,
) -> None:
    database, chat, provider, service = _runtime(
        tmp_path,
        loaded_context_length=2048,
        expected_output_tokens=896,
    )

    try:
        chat_id = chat.create_chat()

        result = service.send_message(
            chat_id=chat_id,
            content="test",
            requested_model_id="primary",
        )

        assert result.context_package.budget.effective_context_limit == 2048
        assert result.context_package.budget.output_reserve == 896
        assert result.context_package.budget.safety_margin == 256
        assert result.context_package.token_estimates.estimated_total_tokens <= 2048
        assert result.generation.assistant_message.content == "direct answer"
        assert provider.stream_calls == 1
    finally:
        database.stop()


def test_default_direct_chat_trims_old_history_but_keeps_it_persisted(
    tmp_path: Path,
) -> None:
    database, chat, provider, service = _runtime(
        tmp_path,
        loaded_context_length=2048,
        expected_output_tokens=896,
    )

    try:
        chat_id = chat.create_chat()
        old_payload = "OLD-HISTORY " * 500

        for index in range(3):
            chat.add_user_message(
                chat_id=chat_id,
                content=f"old-user-{index} {old_payload}",
            )
            chat.add_assistant_message(
                chat_id=chat_id,
                content=f"old-assistant-{index} {old_payload}",
                provider_id="lm_studio",
                model_id="history-model",
            )

        result = service.send_message(
            chat_id=chat_id,
            content="test",
            requested_model_id="primary",
        )

        summary = result.context_package.excluded_candidate_summary
        assert summary.conversation_candidate_count == 6
        assert summary.conversation_included_count < 6
        assert summary.conversation_excluded_count > 0
        assert result.context_package.token_estimates.estimated_total_tokens <= 2048
        assert provider.stream_calls == 1

        sent_text = "\n".join(
            message.content
            for message in provider.requests[-1]
        )
        assert "test" in sent_text
        assert "old-user-0" not in sent_text

        persisted = chat.load_chat(chat_id).messages
        assert len(persisted) == 8
        assert persisted[0].content is not None
        assert "old-user-0" in persisted[0].content
        assert persisted[-1].content == "direct answer"
    finally:
        database.stop()
