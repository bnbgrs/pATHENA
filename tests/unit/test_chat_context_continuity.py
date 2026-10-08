"""Regression coverage for issue #516: long chat continuity and bounded context."""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator, Sequence

import pytest

from athena.chat.continuity import budgeted_continuity
from athena.chat.direct import DirectChatService
from athena.chat.generation import ChatGenerationService
from athena.chat.models import ChatMessage, MessageType
from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.model.domain import (
    ModelChatMessage,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBuilderError
from athena.retrieval.context_package import ContextPackageService
from athena.storage.database import SQLiteDatabase


class _Provider:
    provider_id = "lm_studio"

    def __init__(self) -> None:
        self.calls: list[tuple[ModelChatMessage, ...]] = []

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
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
    ) -> Iterator[str]:
        assert model_id == "primary"
        assert max_output_tokens == 1000
        assert reasoning_mode == "off"
        self.calls.append(tuple(messages))
        yield "continuity reply"


def _runtime(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    provider = _Provider()
    chat = ChatService(ChatRepository(database))
    service = DirectChatService(
        chat_generation=ChatGenerationService(chat, provider),
        context_packages=ContextPackageService(database),
        model_runs=ModelRunRepository(database),
    )
    return database, provider, chat, service


def test_long_chat_fits_loaded_context_and_recalls_old_original(tmp_path) -> None:
    database, provider, chat, service = _runtime(tmp_path)
    try:
        chat_id = chat.create_chat()
        old = chat.add_user_message(
            chat_id=chat_id,
            content="The zeppelin blueprint is stored in the green folder.",
        )
        chat.add_assistant_message(
            chat_id=chat_id, content="Got it.",
            provider_id="lm_studio", model_id="primary",
        )
        for index in range(12):
            chat.add_user_message(
                chat_id=chat_id,
                content=f"unrelated conversation {index} " + "details " * 160,
            )
            chat.add_assistant_message(
                chat_id=chat_id,
                content=f"response {index} " + "discussion " * 150,
                provider_id="lm_studio",
                model_id="primary",
            )

        originals = chat.load_chat(chat_id).messages
        result = service.send_message(
            chat_id=chat_id,
            content="Where is the zeppelin blueprint?",
            requested_model_id="primary",
            output_reserve=1000,
            safety_margin=100,
        )
        assert len(provider.calls) == 1
        sent = provider.calls[0]
        assert "zeppelin blueprint" in sent[0].content.lower()
        assert "green folder" in sent[0].content.lower()
        assert sent[0].role == "user"
        assert sent[-1].content == "Where is the zeppelin blueprint?"
        assert len(sent) < len(originals)
        assert result.context_package.token_estimates.estimated_total_tokens <= 4096
        assert result.context_package.budget.output_reserve == 1000

        # The recap is a traceable projection of original USER messages.
        recap = result.context_package.sections[0]
        assert recap.name == "conversation_continuity"
        recall_refs = [
            item for item in result.context_package.included_refs
            if item.ref_id.startswith("CHAT-RECALL-")
        ]
        assert any(item.entity_id == old.message_id for item in recall_refs)
        assert all(
            item.entity_id in {
                message.message_id for message in originals
                if message.message_type is MessageType.USER
            }
            for item in recall_refs
        )
        persisted = chat.load_chat(chat_id).messages
        assert persisted[:len(originals)] == originals
        assert len(persisted) == len(originals) + 2

        snapshot = json.loads(result.processing_run.input_snapshot_json)
        counts = snapshot["excluded_candidate_summary"]
        assert counts["conversation_candidate_count"] == len(originals)
        assert (
            counts["conversation_included_count"]
            + counts["conversation_excluded_count"]
            == len(originals)
        )
        assert result.processing_run.status == "succeeded"
    finally:
        database.stop()


def test_single_oversized_prior_turn_is_omitted_without_erasure(tmp_path) -> None:
    database, provider, chat, service = _runtime(tmp_path)
    try:
        chat_id = chat.create_chat()
        chat.add_user_message(
            chat_id=chat_id, content="obsolete " * 5000,
        )
        chat.add_assistant_message(
            chat_id=chat_id, content="old assistant " * 2500,
            provider_id="lm_studio", model_id="primary",
        )
        before = chat.load_chat(chat_id).messages
        result = service.send_message(
            chat_id=chat_id,
            content="New topic",
            requested_model_id="primary",
            output_reserve=1000,
            safety_margin=100,
        )
        assert len(provider.calls) == 1
        assert len(provider.calls[0]) <= 2
        assert result.context_package.token_estimates.estimated_total_tokens <= 4096
        assert chat.load_chat(chat_id).messages[:len(before)] == before
    finally:
        database.stop()


def test_oversized_current_input_fails_before_persist_or_provider(tmp_path) -> None:
    database, provider, chat, service = _runtime(tmp_path)
    try:
        chat_id = chat.create_chat()
        with pytest.raises(ContextBuilderError, match="Current user input"):
            service.send_message(
                chat_id=chat_id,
                content="unbounded " * 5500,
                requested_model_id="primary",
                output_reserve=1000,
                safety_margin=100,
            )
        assert not provider.calls
        assert chat.load_chat(chat_id).messages == ()
    finally:
        database.stop()


def test_protected_older_message_is_never_projected_as_recapped_text() -> None:
    chat_id = uuid.uuid4()
    protected = ChatMessage(
        message_id=uuid.uuid4(),
        chat_id=chat_id,
        sequence_no=1,
        message_type=MessageType.USER,
        actor_id=None,
        created_at_us=1,
        revision_id=uuid.uuid4(),
        content=None,
        content_format=None,
    )
    projection = budgeted_continuity(
        all_messages=(protected,),
        initial_recent=(),
        current_query="What did I say earlier?",
        history_budget=512,
    )
    assert projection.recap_sections == ()
    assert projection.recap_refs == ()
    assert projection.included_count == 0
