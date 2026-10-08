from __future__ import annotations

import json
from collections.abc import Iterator, Sequence

import pytest

from athena.chat.direct import DirectChatService
from athena.chat.generation import ChatGenerationService
from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.model.domain import (
    ModelChatMessage,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context_package import ContextPackageService, ContextSnapshotDriftError
from athena.storage.database import SQLiteDatabase


class FakeProvider:
    provider_id = "lm_studio"

    def __init__(self, *, drift_on_discover_call: int | None = None, drift=None) -> None:
        self.discover_calls = 0
        self.stream_calls = 0
        self.requests: list[tuple[ModelChatMessage, ...]] = []
        self.drift_on_discover_call = drift_on_discover_call
        self.drift = drift

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        self.discover_calls += 1
        if (
            self.drift_on_discover_call is not None
            and self.discover_calls == self.drift_on_discover_call
            and self.drift is not None
        ):
            self.drift()
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
        self.stream_calls += 1
        self.requests.append(tuple(messages))
        yield "direct answer"


def _runtime(tmp_path, provider: FakeProvider):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    generation = ChatGenerationService(chat, provider)
    runs = ModelRunRepository(database)
    service = DirectChatService(
        chat_generation=generation,
        context_packages=ContextPackageService(database),
        model_runs=runs,
    )
    return database, chat, runs, service


def test_direct_chat_is_bounded_and_provider_receives_only_package(tmp_path) -> None:
    provider = FakeProvider()
    database, chat, runs, service = _runtime(tmp_path, provider)
    try:
        chat_id = chat.create_chat()
        chat.add_user_message(chat_id=chat_id, content="old user")
        chat.add_assistant_message(
            chat_id=chat_id,
            content="old assistant",
            provider_id="lm_studio",
            model_id="primary",
        )
        recent_user = chat.add_user_message(
            chat_id=chat_id,
            content="recent user [CTX-777]",
        )
        recent_assistant = chat.add_assistant_message(
            chat_id=chat_id,
            content=(
                "recent assistant [CTX-001], "
                "[SOURCE:CTX-002].\n\n"
                'ATHENA_PROVENANCE '
                '{"athena_provenance_version":3,"evidence":[]}'
            ),
            provider_id="lm_studio",
            model_id="primary",
        )

        result = service.send_message(
            chat_id=chat_id,
            content="current user",
            requested_model_id="primary",
            max_recent_conversation_turns=1,
            output_reserve=1000,
            safety_margin=100,
        )

        assert provider.stream_calls == 1
        sent = provider.requests[0]
        assert tuple((item.role, item.content) for item in sent) == (
            ("user", "recent user"),
            ("assistant", "recent assistant."),
            ("user", "current user"),
        )

        assert all(
            "CTX-" not in item.content
            for item in sent[:-1]
        )
        assert all(
            "ATHENA_PROVENANCE" not in item.content
            for item in sent[:-1]
        )

        persisted = chat.load_chat(chat_id).messages

        assert (
            persisted[2].content
            == "recent user [CTX-777]"
        )

        assert (
            persisted[3].content
            == (
                "recent assistant [CTX-001], "
                "[SOURCE:CTX-002].\n\n"
                'ATHENA_PROVENANCE '
                '{"athena_provenance_version":3,"evidence":[]}'
            )
        )
        assert tuple(
            (item.role, item.content)
            for item in result.context_package.model_messages()
        ) == tuple((item.role, item.content) for item in sent)

        snapshot = json.loads(result.processing_run.input_snapshot_json)
        assert snapshot["excluded_candidate_summary"]["conversation_candidate_count"] == 4
        assert snapshot["excluded_candidate_summary"]["conversation_included_count"] == 2
        assert snapshot["excluded_candidate_summary"]["conversation_excluded_count"] == 2
        refs = snapshot["included_refs"]
        assert any(
            item["entity_id"] == str(recent_user.message_id)
            and item["revision_id"] == str(recent_user.revision_id)
            for item in refs
        )
        assert any(
            item["entity_id"] == str(recent_assistant.message_id)
            and item["revision_id"] == str(recent_assistant.revision_id)
            for item in refs
        )
        assert result.processing_run.status == "succeeded"
        assert runs.load_signature(
            result.context_package.model_signature.model_signature_id
        ).model_identifier == "primary"
    finally:
        database.stop()


def test_direct_chat_pre_provider_drift_makes_zero_provider_calls(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        chat = ChatService(ChatRepository(database))
        target_chat = chat.create_chat()
        drift_chat = chat.create_chat()

        def drift() -> None:
            chat.add_user_message(chat_id=drift_chat, content="concurrent write")

        provider = FakeProvider(drift_on_discover_call=2, drift=drift)
        service = DirectChatService(
            chat_generation=ChatGenerationService(chat, provider),
            context_packages=ContextPackageService(database),
            model_runs=ModelRunRepository(database),
        )

        with pytest.raises(ContextSnapshotDriftError):
            service.send_message(
                chat_id=target_chat,
                content="current",
                requested_model_id="primary",
                output_reserve=1000,
                safety_margin=100,
            )

        assert provider.stream_calls == 0
        messages = chat.load_chat(target_chat).messages
        assert len(messages) == 1
        assert messages[0].content == "current"
        row = database.connection.execute(
            "SELECT status, error_detail FROM processing_runs"
        ).fetchone()
        assert row is not None
        assert str(row["status"]) == "failed"
        assert "ContextSnapshotDriftError" in str(row["error_detail"])
    finally:
        database.stop()



def test_direct_long_chat_recalls_archived_original_without_losing_output_reserve(
    tmp_path,
) -> None:
    provider = FakeProvider()
    database, chat, _, service = _runtime(tmp_path, provider)
    try:
        chat_id = chat.create_chat()
        original = chat.add_user_message(
            chat_id=chat_id,
            content="Unser geheimes Codewort ist Elefantenbruecke.",
        )
        chat.add_assistant_message(
            chat_id=chat_id,
            content="Ich habe Elefantenbruecke notiert.",
            provider_id="lm_studio",
            model_id="primary",
        )
        for index in range(12):
            chat.add_user_message(
                chat_id=chat_id,
                content=f"Fuellthema {index}: " + ("Banane " * 180),
            )
            chat.add_assistant_message(
                chat_id=chat_id,
                content="Verstanden. " * 100,
                provider_id="lm_studio",
                model_id="primary",
            )
        before = chat.load_chat(chat_id).messages

        result = service.send_message(
            chat_id=chat_id,
            content="Welches Codewort mit Elefantenbruecke war vereinbart?",
            output_reserve=1000,
            safety_margin=100,
        )

        sent = provider.requests[0]
        assert any(
            message.role == "user"
            and "Elefantenbruecke" in message.content
            and "Historical" in message.content
            for message in sent
        )
        assert result.context_package.budget.output_reserve == 1000
        assert result.context_package.token_estimates.estimated_total_tokens <= 4096
        original_refs = (
            ref
            for ref in result.context_package.included_refs
            if ref.entity_id == original.message_id
        )
        assert any(ref.revision_id == original.revision_id for ref in original_refs)
        summary = result.context_package.excluded_candidate_summary
        assert summary.conversation_included_count + summary.conversation_excluded_count == len(before)
        assert summary.conversation_excluded_count > 0
        after = chat.load_chat(chat_id).messages
        assert len(after) == len(before) + 2
        assert tuple(item.message_id for item in after[:len(before)]) == tuple(
            item.message_id for item in before
        )
        audit = json.loads(result.processing_run.input_snapshot_json)
        assert audit["excluded_candidate_summary"]["conversation_included_count"] == (
            summary.conversation_included_count
        )
    finally:
        database.stop()


def test_direct_unfittable_current_input_has_no_provider_call_or_persistence(
    tmp_path,
) -> None:
    from athena.retrieval.context import ContextBuilderError

    provider = FakeProvider()
    database, chat, _, service = _runtime(tmp_path, provider)
    try:
        chat_id = chat.create_chat()
        with pytest.raises(ContextBuilderError, match="Current user input"):
            service.send_message(
                chat_id=chat_id,
                content="Riesenwort " * 5000,
                output_reserve=1000,
                safety_margin=100,
            )
        assert provider.stream_calls == 0
        assert chat.load_chat(chat_id).messages == ()
    finally:
        database.stop()


def test_continuity_does_not_materialize_protected_archived_text(
    tmp_path,
) -> None:
    from dataclasses import replace

    from athena.chat.context_continuity import build_direct_continuity

    provider = FakeProvider()
    database, chat, _, _ = _runtime(tmp_path, provider)
    try:
        chat_id = chat.create_chat()
        archived = chat.add_user_message(
            chat_id=chat_id,
            content="Elefantenbruecke is confidential.",
        )
        protected = replace(archived, content=None)
        plan = build_direct_continuity(
            archive=(protected,),
            recent_candidates=(),
            query="Was war Elefantenbruecke?",
            context_limit=4096,
            requested_output_reserve=1000,
            safety_margin=100,
        )
        assert plan.recall_refs == ()
        assert plan.recall_sections == ()
    finally:
        database.stop()
