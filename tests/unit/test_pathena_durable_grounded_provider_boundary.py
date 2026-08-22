from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any, cast

from athena.chat import durable_grounded_generation as durable_module
from athena.chat.durable_grounded_generation import DurableGroundedGenerationService


class _Coordinator:
    def __init__(self) -> None:
        self.calls: list[tuple[uuid.UUID, uuid.UUID, object]] = []
        self.events: list[str] = []

    def begin_provider_attempt(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: object,
    ) -> object:
        self.events.append("guard")
        self.calls.append((operation_id, chat_id, fingerprint))
        return object()


class _DelegatedGeneration:
    def __init__(self, chat: object, provider: object, *, interactive_demand: object) -> None:
        del chat, provider, interactive_demand

    def send_context_package(self, **kwargs: Any) -> object:
        before_provider = kwargs["on_before_provider_call"]
        before_provider()
        return _RESULT


_RESULT = object()


def test_durable_generation_uses_recovery_guard_before_provider(monkeypatch) -> None:
    operation_id = uuid.uuid4()
    chat_id = uuid.uuid4()
    fingerprint = object()
    coordinator = _Coordinator()
    base_generation = SimpleNamespace(
        chat=object(),
        provider=object(),
        interactive_demand=None,
    )
    monkeypatch.setattr(
        durable_module,
        "ChatGenerationService",
        _DelegatedGeneration,
    )
    service = DurableGroundedGenerationService(
        cast(Any, base_generation),
        cast(Any, coordinator),
    )

    result = service.send_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        user_message=cast(Any, SimpleNamespace(message_id=operation_id)),
        context_package=cast(Any, object()),
        processing_run_id=uuid.uuid4(),
        fingerprint=cast(Any, fingerprint),
        receipt_payload_builder=lambda content, provider_id, model_id: "{}",
    )

    assert result is _RESULT
    assert coordinator.calls == [(operation_id, chat_id, fingerprint)]


def test_recovery_guard_precedes_external_provider_hook(monkeypatch) -> None:
    operation_id = uuid.uuid4()
    chat_id = uuid.uuid4()
    fingerprint = object()
    coordinator = _Coordinator()
    base_generation = SimpleNamespace(
        chat=object(),
        provider=object(),
        interactive_demand=None,
    )
    monkeypatch.setattr(
        durable_module,
        "ChatGenerationService",
        _DelegatedGeneration,
    )
    service = DurableGroundedGenerationService(
        cast(Any, base_generation),
        cast(Any, coordinator),
    )

    result = service.send_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        user_message=cast(Any, SimpleNamespace(message_id=operation_id)),
        context_package=cast(Any, object()),
        processing_run_id=uuid.uuid4(),
        fingerprint=cast(Any, fingerprint),
        receipt_payload_builder=lambda content, provider_id, model_id: "{}",
        on_before_provider_call=lambda: coordinator.events.append("hook"),
    )

    assert result is _RESULT
    assert coordinator.events == ["guard", "hook"]
