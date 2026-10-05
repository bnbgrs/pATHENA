from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any

from athena.api.client import CoreApiClient, CoreApiClientError
from athena.api.executor import SerializedCoreApiSurface
from athena.api.server import CoreApiServer
from athena.api.service import CoreApiFacade
from athena.chat.cancellation import (
    ChatCancellationRegistry,
    ChatCancellationReservation,
)
from athena.chat.generation import GenerationCancelledError
from athena.model.domain import (
    ModelChatMessage,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)

_OPERATION_ID = "11111111-2222-4333-8444-555555555555"
_CHAT_ID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"


class _GateExecutor:
    def __init__(self) -> None:
        self.calls = 0
        self.queued = threading.Event()
        self.allow_owner = threading.Event()

    def call(self, callback: Callable[[], Any]) -> Any:
        self.calls += 1
        self.queued.set()
        assert self.allow_owner.wait(2.0)
        return callback()


class _CancellationSurface:
    def __init__(self) -> None:
        self.registry = ChatCancellationRegistry()
        self.send_started = threading.Event()
        self.send_observed_cancel = threading.Event()

    def reserve_chat_operation(
        self,
        operation_id: str,
    ) -> ChatCancellationReservation | None:
        return self.registry.reserve(uuid.UUID(operation_id))

    def release_chat_operation(
        self,
        reservation: ChatCancellationReservation,
    ) -> None:
        self.registry.release(reservation)

    def cancel_chat_operation(self, operation_id: str) -> bool:
        return self.registry.cancel(uuid.UUID(operation_id))

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> object:
        del (
            chat_id,
            content,
            requested_model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        reservation = self.registry.get_or_reserve(uuid.UUID(operation_id))
        self.send_started.set()
        if reservation.cancel_requested():
            self.send_observed_cancel.set()
            raise GenerationCancelledError("cancelled before provider")
        raise AssertionError("owner callback started without observing cancellation")


    def send_unified_local_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        requested_embedding_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> object:
        del (
            chat_id,
            content,
            requested_model_id,
            requested_embedding_model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        reservation = self.registry.get_or_reserve(uuid.UUID(operation_id))
        self.send_started.set()
        if reservation.cancel_requested():
            self.send_observed_cancel.set()
            raise GenerationCancelledError("grounded cancelled before provider")
        raise AssertionError("grounded owner callback started without cancellation")


def test_cancel_bypasses_owner_queue_and_closes_pre_dispatch_race() -> None:
    surface = _CancellationSurface()
    executor = _GateExecutor()
    serialized = SerializedCoreApiSurface(
        surface,  # type: ignore[arg-type]
        executor,  # type: ignore[arg-type]
    )
    raised: list[Exception] = []

    def run_send() -> None:
        try:
            serialized.send_chat_message(
                _CHAT_ID,
                content="cancel immediately",
                operation_id=_OPERATION_ID,
            )
        except Exception as exc:
            raised.append(exc)

    thread = threading.Thread(target=run_send)
    thread.start()

    assert executor.queued.wait(2.0)
    assert executor.calls == 1

    # The operation was reserved before owner-thread dispatch. Cancellation must
    # therefore succeed even though the queued send callback has not started.
    assert serialized.cancel_chat_operation(_OPERATION_ID) is True
    assert executor.calls == 1

    executor.allow_owner.set()
    thread.join(2.0)

    assert thread.is_alive() is False
    assert surface.send_started.is_set()
    assert surface.send_observed_cancel.is_set()
    assert len(raised) == 1
    assert isinstance(raised[0], GenerationCancelledError)
    assert surface.registry.is_active(uuid.UUID(_OPERATION_ID)) is False


def test_grounded_cancel_bypasses_owner_queue_and_closes_pre_dispatch_race() -> None:
    surface = _CancellationSurface()
    executor = _GateExecutor()
    serialized = SerializedCoreApiSurface(
        surface,  # type: ignore[arg-type]
        executor,  # type: ignore[arg-type]
    )
    raised: list[Exception] = []

    def run_send() -> None:
        try:
            serialized.send_unified_local_chat_message(
                _CHAT_ID,
                content="cancel grounded immediately",
                operation_id=_OPERATION_ID,
            )
        except Exception as exc:
            raised.append(exc)

    thread = threading.Thread(target=run_send)
    thread.start()

    assert executor.queued.wait(2.0)
    assert executor.calls == 1
    assert serialized.cancel_chat_operation(_OPERATION_ID) is True
    assert executor.calls == 1

    executor.allow_owner.set()
    thread.join(2.0)

    assert thread.is_alive() is False
    assert surface.send_observed_cancel.is_set()
    assert len(raised) == 1
    assert isinstance(raised[0], GenerationCancelledError)
    assert surface.registry.is_active(uuid.UUID(_OPERATION_ID)) is False


def test_unknown_cancel_does_not_enter_owner_executor() -> None:
    surface = _CancellationSurface()
    executor = _GateExecutor()
    serialized = SerializedCoreApiSurface(
        surface,  # type: ignore[arg-type]
        executor,  # type: ignore[arg-type]
    )

    assert serialized.cancel_chat_operation(_OPERATION_ID) is False
    assert executor.calls == 0


class _BlockingHttpSurface:
    def __init__(self) -> None:
        self.registry = ChatCancellationRegistry()
        self.send_started = threading.Event()

    def reserve_chat_operation(
        self,
        operation_id: str,
    ) -> ChatCancellationReservation | None:
        return self.registry.reserve(uuid.UUID(operation_id))

    def release_chat_operation(
        self,
        reservation: ChatCancellationReservation,
    ) -> None:
        self.registry.release(reservation)

    def cancel_chat_operation(self, operation_id: str) -> bool:
        return self.registry.cancel(uuid.UUID(operation_id))

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> object:
        del (
            chat_id,
            content,
            requested_model_id,
            effective_context_limit,
            max_output_tokens,
            temperature,
            thinking_enabled,
        )
        assert operation_id is not None
        reservation = self.registry.get_or_reserve(uuid.UUID(operation_id))
        self.send_started.set()
        deadline = time.monotonic() + 2.0
        try:
            while not reservation.cancel_requested():
                if time.monotonic() >= deadline:
                    raise AssertionError(
                        "HTTP cancellation did not reach the active send."
                    )
                time.sleep(0.01)
            raise GenerationCancelledError("cancelled through HTTP control plane")
        finally:
            self.registry.release(reservation)


def test_threaded_local_http_server_accepts_cancel_while_send_is_blocked(
    tmp_path,
) -> None:
    surface = _BlockingHttpSurface()
    runtime_root = tmp_path / "api"
    server = CoreApiServer(
        facade=surface,  # type: ignore[arg-type]
        runtime_root=runtime_root,
    )
    errors: list[CoreApiClientError] = []

    server.start()
    try:
        client = CoreApiClient(
            runtime_root,
            timeout_seconds=2.0,
            generation_timeout_seconds=3.0,
        )

        def send_message() -> None:
            try:
                client.send_chat_message(
                    _CHAT_ID,
                    content="block until cancelled",
                    operation_id=_OPERATION_ID,
                )
            except CoreApiClientError as exc:
                errors.append(exc)

        thread = threading.Thread(target=send_message)
        thread.start()

        assert surface.send_started.wait(2.0)
        assert client.cancel_chat_operation(_OPERATION_ID) is True

        thread.join(3.0)
        assert thread.is_alive() is False
        assert len(errors) == 1
        assert errors[0].status == 409
        assert errors[0].code == "generation_cancelled"
        assert surface.registry.is_active(uuid.UUID(_OPERATION_ID)) is False
    finally:
        server.stop()


class _ProviderCancelProbe:
    provider_id = "probe"

    def __init__(self) -> None:
        self.cancelled: list[str] = []

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return ()

    def stream_chat(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
    ) -> Iterator[str]:
        del (
            model_id,
            messages,
            max_output_tokens,
            reasoning_mode,
            temperature,
        )
        if False:
            yield ""

    def stream_chat_cancellable(
        self,
        *,
        request_id: str,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        max_output_tokens: int | None = None,
        reasoning_mode: str | None = None,
        temperature: float | None = None,
        cancel_requested: Callable[[], bool] | None = None,
    ) -> Iterator[str]:
        del (
            request_id,
            model_id,
            messages,
            max_output_tokens,
            reasoning_mode,
            temperature,
            cancel_requested,
        )
        if False:
            yield ""

    def generate_structured(
        self,
        *,
        model_id: str,
        messages: Sequence[ModelChatMessage],
        schema_id: str,
        json_schema: Mapping[str, Any],
        max_output_tokens: int | None = None,
    ) -> Mapping[str, Any]:
        del model_id, messages, schema_id, json_schema, max_output_tokens
        return {}

    def cancel_generation(self, request_id: str) -> None:
        self.cancelled.append(request_id)


def test_core_cancel_aborts_provider_only_for_reserved_operation() -> None:
    provider = _ProviderCancelProbe()
    facade = CoreApiFacade(
        health=object(),  # type: ignore[arg-type]
        chat=object(),  # type: ignore[arg-type]
        model_provider=provider,
    )

    reservation = facade.reserve_chat_operation(_OPERATION_ID)
    assert reservation is not None

    assert facade.cancel_chat_operation(_OPERATION_ID) is True
    assert provider.cancelled == [_OPERATION_ID]

    facade.release_chat_operation(reservation)

    assert facade.cancel_chat_operation(_OPERATION_ID) is False
    assert provider.cancelled == [_OPERATION_ID]
