from __future__ import annotations

import threading
import uuid

import pytest
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
from athena.api.search_contracts import SearchProtectionResponse, SearchResultResponse
from athena.chat.send_identity import assistant_message_id_for_operation, chat_id_for_operation
from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
from athena.desktop.app import create_application
from athena.retrieval.universal import UniversalSearchEntityType


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


class _BlockingCancelableGateway(_Gateway):
    def __init__(self, *, cancel_accepted: bool) -> None:
        super().__init__()
        self.cancel_accepted = cancel_accepted
        self.send_entered = threading.Event()
        self.cancel_called = threading.Event()
        self.release_send = threading.Event()
        self.sent_operation_id: str | None = None
        self.sent_content: str | None = None
        self.sent_chat_id: str | None = None
        self.send_thread_id: int | None = None
        self.cancel_thread_id: int | None = None

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> ChatThreadResponse:
        del (
            model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        self.send_thread_id = threading.get_ident()
        self.sent_chat_id = chat_id
        self.sent_operation_id = operation_id
        self.sent_content = content
        self.send_entered.set()

        if self.cancel_accepted:
            assert self.cancel_called.wait(2.0)
            raise CoreApiClientError(
                "Chat generation was cancelled.",
                status=409,
                code="generation_cancelled",
                retryable=False,
            )

        assert self.release_send.wait(2.0)
        return self._thread(include_assistant=True)

    def cancel_chat_operation(self, operation_id: str) -> bool:
        self.cancel_thread_id = threading.get_ident()
        assert operation_id == self.sent_operation_id
        self.cancel_called.set()
        return self.cancel_accepted

    def load_chat(self, chat_id: str) -> ChatThreadResponse:
        assert chat_id == self.sent_chat_id
        return self._thread(include_assistant=False)

    def _thread(self, *, include_assistant: bool) -> ChatThreadResponse:
        assert self.sent_chat_id is not None
        assert self.sent_operation_id is not None
        assert self.sent_content is not None
        parsed_operation_id = uuid.UUID(self.sent_operation_id)
        user = ChatMessageResponse(
            message_id=self.sent_operation_id,
            chat_id=self.sent_chat_id,
            sequence_no=1,
            message_type="user",
            actor_id=str(uuid.uuid4()),
            created_at_us=1,
            revision_id=str(uuid.uuid4()),
            content=self.sent_content,
            content_format="text/plain",
        )
        messages: tuple[ChatMessageResponse, ...] = (user,)
        if include_assistant:
            assistant = ChatMessageResponse(
                message_id=str(
                    assistant_message_id_for_operation(parsed_operation_id)
                ),
                chat_id=self.sent_chat_id,
                sequence_no=2,
                message_type="assistant",
                actor_id=str(uuid.uuid4()),
                created_at_us=2,
                revision_id=str(uuid.uuid4()),
                content="answer",
                content_format="text/plain",
            )
            messages = (user, assistant)
        return ChatThreadResponse(
            chat_id=self.sent_chat_id,
            started_at_us=1,
            ended_at_us=None,
            archive_mode="standard",
            lifecycle_state="active",
            messages=messages,
        )


class _BlockingGroundedCancelableGateway(_BlockingCancelableGateway):
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
        self.send_thread_id = threading.get_ident()
        self.sent_chat_id = chat_id
        self.sent_operation_id = operation_id
        self.sent_content = content
        self.send_entered.set()
        assert self.cancel_called.wait(2.0)
        raise CoreApiClientError(
            "Grounded chat generation was cancelled.",
            status=409,
            code="generation_cancelled",
            retryable=False,
        )


def test_controller_stop_bypasses_blocked_grounded_send_pool() -> None:
    app = _app()
    gateway = _BlockingGroundedCancelableGateway(cancel_accepted=True)
    send_pool = _pool()
    control_pool = _pool()
    controller = DesktopApiController(
        gateway,
        thread_pool=send_pool,
        control_thread_pool=control_pool,
    )
    cancelled = QSignalSpy(controller.chat_cancelled)
    loaded = QSignalSpy(controller.chat_loaded)
    chat_id = str(uuid.uuid4())

    controller.send_grounded_message(
        chat_id=chat_id,
        content="stop grounded",
    )

    assert gateway.send_entered.wait(1.0)
    assert controller.chat_busy is True
    assert controller.can_cancel_active_chat is True
    assert controller.cancel_active_chat_operation() is True

    assert control_pool.waitForDone(2_000)
    assert send_pool.waitForDone(2_000)
    app.processEvents()
    app.processEvents()

    assert gateway.cancel_called.is_set()
    assert cancelled.count() == 1
    assert cancelled.at(0)[0] == gateway.sent_operation_id
    assert loaded.count() == 1
    thread = loaded.at(0)[0]
    assert isinstance(thread, ChatThreadResponse)
    assert len(thread.messages) == 1
    assert thread.messages[0].message_type == "user"
    assert controller.chat_busy is False
    assert controller.can_cancel_active_chat is False


def test_controller_stop_bypasses_blocked_single_thread_send_pool() -> None:
    app = _app()
    gateway = _BlockingCancelableGateway(cancel_accepted=True)
    send_pool = _pool()
    control_pool = _pool()
    controller = DesktopApiController(
        gateway,
        thread_pool=send_pool,
        control_thread_pool=control_pool,
    )
    cancelled = QSignalSpy(controller.chat_cancelled)
    loaded = QSignalSpy(controller.chat_loaded)
    states = QSignalSpy(controller.chat_cancel_state_changed)
    main_thread = threading.get_ident()
    chat_id = str(uuid.uuid4())

    controller.send_message(chat_id=chat_id, content="stop me")

    assert gateway.send_entered.wait(1.0)
    assert controller.chat_busy is True
    assert controller.can_cancel_active_chat is True
    assert controller.chat_cancel_pending is False
    assert controller.cancel_active_chat_operation() is True
    assert controller.chat_cancel_pending is True

    assert control_pool.waitForDone(2_000)
    assert send_pool.waitForDone(2_000)
    app.processEvents()
    app.processEvents()

    assert gateway.cancel_called.is_set()
    assert gateway.send_thread_id is not None
    assert gateway.cancel_thread_id is not None
    assert gateway.send_thread_id != main_thread
    assert gateway.cancel_thread_id != main_thread
    assert gateway.cancel_thread_id != gateway.send_thread_id
    assert cancelled.count() == 1
    assert cancelled.at(0)[0] == gateway.sent_operation_id
    assert loaded.count() == 1
    thread = loaded.at(0)[0]
    assert isinstance(thread, ChatThreadResponse)
    assert len(thread.messages) == 1
    assert thread.messages[0].message_type == "user"
    assert states.count() >= 1
    assert states.at(0)[0] == "requesting"
    assert controller.chat_busy is False
    assert controller.can_cancel_active_chat is False
    assert controller.chat_cancel_pending is False


def test_controller_rejected_stop_keeps_send_running_and_allows_retry() -> None:
    app = _app()
    gateway = _BlockingCancelableGateway(cancel_accepted=False)
    send_pool = _pool()
    control_pool = _pool()
    controller = DesktopApiController(
        gateway,
        thread_pool=send_pool,
        control_thread_pool=control_pool,
    )
    states = QSignalSpy(controller.chat_cancel_state_changed)
    sent = QSignalSpy(controller.chat_sent)
    cancelled = QSignalSpy(controller.chat_cancelled)
    chat_id = str(uuid.uuid4())

    controller.send_message(chat_id=chat_id, content="finish normally")

    assert gateway.send_entered.wait(1.0)
    assert controller.cancel_active_chat_operation() is True
    assert control_pool.waitForDone(2_000)
    app.processEvents()

    assert controller.chat_busy is True
    assert controller.can_cancel_active_chat is True
    assert controller.chat_cancel_pending is False
    assert controller.chat_cancel_state == "expired"
    assert states.count() >= 2
    assert states.at(0)[0] == "requesting"
    assert states.at(states.count() - 1)[0] == "expired"
    assert controller.cancel_active_chat_operation() is True
    assert control_pool.waitForDone(2_000)
    app.processEvents()
    assert controller.chat_cancel_state == "expired"

    gateway.release_send.set()
    assert send_pool.waitForDone(2_000)
    app.processEvents()

    assert sent.count() == 1
    assert cancelled.count() == 0
    assert controller.chat_busy is False
    assert controller.can_cancel_active_chat is False


class _LateCancelGateway(_BlockingCancelableGateway):
    def __init__(self) -> None:
        super().__init__(cancel_accepted=True)

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> ChatThreadResponse:
        del (
            model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        self.send_thread_id = threading.get_ident()
        self.sent_chat_id = chat_id
        self.sent_operation_id = operation_id
        self.sent_content = content
        self.send_entered.set()
        assert self.cancel_called.wait(2.0)
        return self._thread(include_assistant=True)


def test_controller_reports_accepted_but_late_stop_as_completed() -> None:
    app = _app()
    gateway = _LateCancelGateway()
    send_pool = _pool()
    control_pool = _pool()
    controller = DesktopApiController(
        gateway,
        thread_pool=send_pool,
        control_thread_pool=control_pool,
    )
    states = QSignalSpy(controller.chat_cancel_state_changed)
    sent = QSignalSpy(controller.chat_sent)
    cancelled = QSignalSpy(controller.chat_cancelled)

    controller.send_message(
        chat_id=str(uuid.uuid4()),
        content="too late to stop",
    )

    assert gateway.send_entered.wait(1.0)
    assert controller.cancel_active_chat_operation() is True
    assert control_pool.waitForDone(2_000)
    assert send_pool.waitForDone(2_000)
    app.processEvents()
    app.processEvents()

    observed_states = [states.at(index)[0] for index in range(states.count())]
    assert observed_states[0] == "requesting"
    assert "expired" in observed_states
    assert sent.count() == 1
    assert cancelled.count() == 0
    assert controller.chat_busy is False


class _SearchGateway(_Gateway):
    def __init__(self, *, fail: bool = False) -> None:
        super().__init__()
        self.fail = fail
        self.search_calls: list[tuple[str, int]] = []

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]:
        self._record()
        assert entity_types is None
        self.search_calls.append((query, limit))
        if self.fail:
            raise CoreApiClientError("Universal search unavailable.")
        return (
            SearchResultResponse(
                result_ref=(
                    "knowledge:"
                    "11111111-1111-1111-1111-111111111111"
                ),
                title="Alpha project",
                preview="Alpha durable knowledge.",
                entity_type="knowledge",
                revision_id="22222222-2222-2222-2222-222222222222",
                rank=1,
                retrieval_methods=("lexical",),
                source_anchor=None,
                protection=SearchProtectionResponse(
                    state="unprotected",
                    protection_scope_id=None,
                ),
            ),
        )


def test_controller_search_runs_off_ui_thread_and_emits_stable_request_id() -> None:
    app = _app()
    gateway = _SearchGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    ready = QSignalSpy(controller.search_ready)
    states = QSignalSpy(controller.search_state_changed)
    main_thread = threading.get_ident()

    request_id = controller.search("  alpha   project  ", limit=7)

    assert request_id == 1
    assert pool.waitForDone(2_000)
    app.processEvents()

    assert ready.count() == 1
    assert ready.at(0)[0] == request_id
    assert ready.at(0)[1] == "alpha project"
    results = ready.at(0)[2]
    assert len(results) == 1
    assert results[0].result_ref == (
        "knowledge:11111111-1111-1111-1111-111111111111"
    )
    assert gateway.search_calls == [("alpha project", 7)]
    assert gateway.thread_ids
    assert all(thread_id != main_thread for thread_id in gateway.thread_ids)
    assert [states.at(index)[0] for index in range(states.count())] == [
        True,
        False,
    ]


def test_controller_search_reports_core_failure_without_fake_results() -> None:
    app = _app()
    gateway = _SearchGateway(fail=True)
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    ready = QSignalSpy(controller.search_ready)
    failed = QSignalSpy(controller.search_failed)

    request_id = controller.search("alpha")

    assert pool.waitForDone(2_000)
    app.processEvents()

    assert ready.count() == 0
    assert failed.count() == 1
    assert failed.at(0) == [
        request_id,
        "alpha",
        "Universal search unavailable.",
    ]


def test_controller_search_rejects_invalid_request_before_thread_start() -> None:
    gateway = _SearchGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)

    with pytest.raises(ValueError, match="must not be empty"):
        controller.search("   ")

    with pytest.raises(ValueError, match="between 1 and 100"):
        controller.search("alpha", limit=0)

    assert gateway.search_calls == []



def test_controller_search_busy_state_spans_multiple_inflight_requests() -> None:
    app = _app()
    gateway = _SearchGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    ready = QSignalSpy(controller.search_ready)
    states = QSignalSpy(controller.search_state_changed)

    first = controller.search("alpha")
    second = controller.search("beta")

    assert (first, second) == (1, 2)
    assert controller.search_busy is True
    assert pool.waitForDone(2_000)
    app.processEvents()

    assert ready.count() == 2
    assert {ready.at(index)[0] for index in range(ready.count())} == {1, 2}
    assert gateway.search_calls == [("alpha", 30), ("beta", 30)]
    assert controller.search_busy is False
    assert [states.at(index)[0] for index in range(states.count())] == [
        True,
        False,
    ]


class _EditForkGateway(_Gateway):
    def __init__(self) -> None:
        super().__init__()
        self.edit_calls: list[tuple[str, str, str, str]] = []
        self.fork_calls: list[tuple[str, str, str]] = []

    @staticmethod
    def _thread(
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
        content: str,
    ) -> ChatThreadResponse:
        return ChatThreadResponse(
            chat_id=chat_id,
            started_at_us=1,
            ended_at_us=None,
            archive_mode="standard",
            lifecycle_state="active",
            messages=(
                ChatMessageResponse(
                    message_id=message_id,
                    chat_id=chat_id,
                    sequence_no=1,
                    message_type="user",
                    actor_id=str(uuid.uuid4()),
                    created_at_us=1,
                    revision_id=revision_id,
                    content=content,
                    content_format="text/plain",
                ),
            ),
        )

    def edit_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        expected_revision_id: str,
        content: str,
    ) -> ChatThreadResponse:
        self._record()
        self.edit_calls.append(
            (chat_id, message_id, expected_revision_id, content)
        )
        return self._thread(
            chat_id=chat_id,
            message_id=message_id,
            revision_id=str(uuid.uuid4()),
            content=content,
        )

    def fork_chat_from_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> ChatThreadResponse:
        self._record()
        self.fork_calls.append((chat_id, message_id, revision_id))
        return self._thread(
            chat_id=str(uuid.uuid4()),
            message_id=message_id,
            revision_id=revision_id,
            content="source",
        )


def test_controller_edit_message_runs_off_ui_thread_and_returns_canonical_thread() -> None:
    app = _app()
    gateway = _EditForkGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    loaded = QSignalSpy(controller.chat_loaded)
    main_thread = threading.get_ident()
    chat_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    revision_id = str(uuid.uuid4())

    controller.edit_message(
        chat_id=chat_id,
        message_id=message_id,
        revision_id=revision_id,
        content="revised",
    )

    assert pool.waitForDone(2_000)
    app.processEvents()

    assert gateway.edit_calls == [
        (chat_id, message_id, revision_id, "revised")
    ]
    assert gateway.thread_ids
    assert all(thread_id != main_thread for thread_id in gateway.thread_ids)
    assert loaded.count() == 1
    thread = loaded.at(0)[0]
    assert isinstance(thread, ChatThreadResponse)
    assert thread.chat_id == chat_id
    assert thread.messages[0].content == "revised"
    assert controller.chat_busy is False


def test_controller_fork_chat_runs_off_ui_thread_and_switches_to_returned_thread() -> None:
    app = _app()
    gateway = _EditForkGateway()
    pool = _pool()
    controller = DesktopApiController(gateway, thread_pool=pool)
    loaded = QSignalSpy(controller.chat_loaded)
    main_thread = threading.get_ident()
    chat_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    revision_id = str(uuid.uuid4())

    controller.fork_chat_from_message(
        chat_id=chat_id,
        message_id=message_id,
        revision_id=revision_id,
    )

    assert pool.waitForDone(2_000)
    app.processEvents()

    assert gateway.fork_calls == [(chat_id, message_id, revision_id)]
    assert gateway.thread_ids
    assert all(thread_id != main_thread for thread_id in gateway.thread_ids)
    assert loaded.count() == 1
    thread = loaded.at(0)[0]
    assert isinstance(thread, ChatThreadResponse)
    assert thread.chat_id != chat_id
    assert controller.chat_busy is False
