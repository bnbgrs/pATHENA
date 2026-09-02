from __future__ import annotations

import threading
import uuid

from PySide6.QtCore import QThreadPool
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from athena.api.client import CoreApiClientError
from athena.api.contracts import (
    ChatMessageResponse,
    ChatSummaryResponse,
    ChatThreadResponse,
    GroundedChatResponse,
    GroundingResponse,
    HealthResponse,
    ModelResponse,
    ProviderHealthResponse,
)
from athena.chat.send_identity import assistant_message_id_for_operation, chat_id_for_operation
from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.app import create_application


class _Gateway:
    def __init__(
        self,
        *,
        core_fail: bool = False,
        chat_fail: bool = False,
        model_fail: bool = False,
    ) -> None:
        self.core_fail = core_fail
        self.chat_fail = chat_fail
        self.model_fail = model_fail
        self.thread_ids: list[int] = []

    def _record(self) -> None:
        self.thread_ids.append(threading.get_ident())

    def health(self) -> HealthResponse:
        self._record()
        if self.core_fail:
            raise CoreApiClientError("ATHENA Core is unavailable.")
        return HealthResponse(api_version="v1", core_status="ok", detail=None)

    def provider_health(self) -> ProviderHealthResponse:
        self._record()
        if self.model_fail:
            raise CoreApiClientError("LM Studio is unavailable.")
        return ProviderHealthResponse(provider="lm_studio", status="ready", detail=None)

    def list_models(self) -> tuple[ModelResponse, ...]:
        self._record()
        return (
            ModelResponse(
                provider="lm_studio",
                backend_model_id="qwen-test",
                display_name="Qwen Test",
                model_type="llm",
                context_capacity=128_000,
                quantization="Q4",
                loaded=True,
                vision=False,
                trained_for_tool_use=True,
                loaded_context_length=48_000,
            ),
        )

    def list_chats(self, *, limit: int = 50) -> tuple[ChatSummaryResponse, ...]:
        self._record()
        if self.chat_fail:
            raise CoreApiClientError("Chat status is unavailable.")
        assert limit == 50
        return (
            ChatSummaryResponse(
                chat_id="chat-1",
                started_at_us=1,
                ended_at_us=None,
                archive_mode="standard",
                lifecycle_state="active",
                message_count=2,
            ),
        )


def _app() -> QApplication:
    return create_application(["athena-desktop-controller-test"])


def _pool() -> QThreadPool:
    pool = QThreadPool()
    pool.setMaxThreadCount(1)
    return pool


def test_controller_refresh_runs_gateway_off_ui_thread() -> None:
    app = _app()
    gateway = _Gateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    spy = QSignalSpy(controller.snapshot_ready)
    main_thread = threading.get_ident()

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    snapshot = spy.at(0)[0]
    assert isinstance(snapshot, DesktopApiSnapshot)
    assert snapshot.health.core_status == "ok"
    assert snapshot.loaded_model is not None
    assert snapshot.loaded_model.display_name == "Qwen Test"
    assert gateway.thread_ids
    assert all(thread_id != main_thread for thread_id in gateway.thread_ids)
    assert pool.waitForDone(2_000)


def test_controller_reports_safe_core_failure() -> None:
    app = _app()
    gateway = _Gateway(core_fail=True)
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    spy = QSignalSpy(controller.connection_failed)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    assert spy.at(0)[0] == "ATHENA Core is unavailable."


def test_controller_keeps_core_connected_when_optional_status_fails() -> None:
    app = _app()
    gateway = _Gateway(chat_fail=True, model_fail=True)
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    spy = QSignalSpy(controller.snapshot_ready)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    snapshot = spy.at(0)[0]
    assert isinstance(snapshot, DesktopApiSnapshot)
    assert snapshot.health.core_status == "ok"
    assert snapshot.provider is None
    assert snapshot.models == ()
    assert snapshot.chats == ()
    assert snapshot.chat_error == "Chat status is unavailable."
    assert snapshot.model_error == "LM Studio is unavailable."
    assert pool.waitForDone(2_000)


def _chat_summary(index: int) -> ChatSummaryResponse:
    return ChatSummaryResponse(
        chat_id=f"chat-{index:03d}",
        started_at_us=10_000 - index,
        ended_at_us=None,
        archive_mode="standard",
        lifecycle_state="active",
        message_count=index,
    )


class _PagedGateway(_Gateway):
    def __init__(self) -> None:
        super().__init__()
        self.chats = tuple(_chat_summary(index) for index in range(125))
        self.chat_page_calls: list[tuple[int, int]] = []

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        self._record()
        self.chat_page_calls.append((limit, offset))
        return self.chats[offset : offset + limit]


class _DuplicatePageGateway(_Gateway):
    def __init__(self) -> None:
        super().__init__()
        self.chat_page_calls: list[tuple[int, int]] = []

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        self._record()
        self.chat_page_calls.append((limit, offset))
        return tuple(_chat_summary(index) for index in range(limit))


def test_controller_paginates_all_chat_summaries() -> None:
    app = _app()
    gateway = _PagedGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool, chat_limit=50)
    spy = QSignalSpy(controller.snapshot_ready)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    snapshot = spy.at(0)[0]
    assert isinstance(snapshot, DesktopApiSnapshot)
    assert snapshot.chat_error is None
    assert len(snapshot.chats) == 125
    assert len({chat.chat_id for chat in snapshot.chats}) == 125
    assert gateway.chat_page_calls == [(50, 0), (50, 50), (50, 100)]
    assert pool.waitForDone(2_000)


def test_controller_rejects_duplicate_chat_page() -> None:
    app = _app()
    gateway = _DuplicatePageGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool, chat_limit=50)
    spy = QSignalSpy(controller.snapshot_ready)

    controller.refresh()

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    snapshot = spy.at(0)[0]
    assert isinstance(snapshot, DesktopApiSnapshot)
    assert snapshot.chats == ()
    assert snapshot.chat_error == (
        "ATHENA chat pagination returned a duplicate chat identity."
    )
    assert gateway.chat_page_calls == [(50, 0), (50, 50)]
    assert pool.waitForDone(2_000)


class _GroundedGateway(_Gateway):
    def __init__(self) -> None:
        super().__init__()
        self.created_chat_id: str | None = None
        self.sent_chat_id: str | None = None
        self.sent_operation_id: str | None = None

    def create_chat(self, chat_id: str | None = None) -> ChatThreadResponse:
        assert chat_id is not None
        self.created_chat_id = chat_id
        return ChatThreadResponse(
            chat_id=chat_id,
            started_at_us=1,
            ended_at_us=None,
            archive_mode="archive",
            lifecycle_state="active",
            messages=(),
        )

    def send_unified_local_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        model_id: str | None = None,
        embedding_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> GroundedChatResponse:
        del (
            model_id,
            embedding_model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        parsed_operation_id = uuid.UUID(operation_id)
        self.sent_chat_id = chat_id
        self.sent_operation_id = operation_id
        user = ChatMessageResponse(
            message_id=operation_id,
            chat_id=chat_id,
            sequence_no=1,
            message_type="user",
            actor_id=str(uuid.uuid4()),
            created_at_us=1,
            revision_id=str(uuid.uuid4()),
            content=content,
            content_format="text/plain",
        )
        assistant = ChatMessageResponse(
            message_id=str(assistant_message_id_for_operation(parsed_operation_id)),
            chat_id=chat_id,
            sequence_no=2,
            message_type="assistant",
            actor_id=str(uuid.uuid4()),
            created_at_us=2,
            revision_id=str(uuid.uuid4()),
            content="answer",
            content_format="text/plain",
        )
        thread = ChatThreadResponse(
            chat_id=chat_id,
            started_at_us=1,
            ended_at_us=None,
            archive_mode="archive",
            lifecycle_state="active",
            messages=(user, assistant),
        )
        return GroundedChatResponse(
            thread=thread,
            assistant_text="answer",
            evidence=(),
            personal_memory=(),
            grounding=GroundingResponse(
                cited_context_ids=(),
                canonical_context_ids=(),
                user_statement_context_ids=(),
                conversation_context_ids=(),
                source_context_ids=(),
                research_context_ids=(),
                news_context_ids=(),
                invalid_context_ids=(),
                uses_inference=False,
                uses_model_prior=True,
                uses_unknown=False,
                has_provenance_marker=True,
            ),
            processing_run_id=str(uuid.uuid4()),
            model_id="primary",
            embedding_model_id=None,
        )


def test_controller_grounded_send_keeps_operation_and_new_chat_identity_stable() -> None:
    app = _app()
    gateway = _GroundedGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    spy = QSignalSpy(controller.grounded_chat_sent)

    controller.send_grounded_message(
        chat_id=None,
        content="hello grounded",
        model_id="primary",
    )

    assert pool.waitForDone(2_000)
    app.processEvents()
    assert spy.count() == 1
    assert gateway.sent_operation_id is not None
    operation_id = uuid.UUID(gateway.sent_operation_id)
    assert operation_id.version == 7
    expected_chat_id = str(chat_id_for_operation(operation_id))
    assert gateway.created_chat_id == expected_chat_id
    assert gateway.sent_chat_id == expected_chat_id
    grounded = spy.at(0)[0]
    assert isinstance(grounded, GroundedChatResponse)
    assert grounded.thread.messages[0].message_id == str(operation_id)
    assert grounded.thread.messages[1].message_id == str(
        assistant_message_id_for_operation(operation_id)
    )
