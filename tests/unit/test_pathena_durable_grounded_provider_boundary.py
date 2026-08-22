from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any, cast

import pytest

from athena.chat import durable_grounded_generation as durable_module
from athena.chat.durable_grounded_generation import DurableGroundedGenerationService
from athena.chat.grounded_recovery import GroundedRecoveryState
from athena.chat.grounded_send import GroundedProviderBoundaryError


class _Coordinator:
    def __init__(self) -> None:
        self.database = object()
        self.calls: list[tuple[uuid.UUID, uuid.UUID, object]] = []
        self.context_packages: list[tuple[uuid.UUID, uuid.UUID, object]] = []
        self.events: list[str] = []
        self.state = GroundedRecoveryState.RESUMABLE

    def recover(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: object,
    ) -> object:
        del chat_id, fingerprint
        return SimpleNamespace(operation_id=operation_id, state=self.state)

    def store_context_package(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        package: object,
    ) -> object:
        self.events.append("package")
        self.context_packages.append((operation_id, chat_id, package))
        return object()

    def begin_provider_attempt(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: object,
    ) -> object:
        self.events.append("guard")
        self.calls.append((operation_id, chat_id, fingerprint))
        self.state = GroundedRecoveryState.AMBIGUOUS
        return object()


class _DelegatedGeneration:
    def __init__(self, chat: object, provider: object, *, interactive_demand: object) -> None:
        del chat, provider, interactive_demand

    def send_context_package(self, **kwargs: Any) -> object:
        before_provider = kwargs["on_before_provider_call"]
        before_provider()
        return _RESULT


class _RetryingDelegatedGeneration(_DelegatedGeneration):
    def send_context_package(self, **kwargs: Any) -> object:
        before_provider = kwargs["on_before_provider_call"]
        before_provider()
        before_provider()
        return _RESULT


_RESULT = object()


def _service(monkeypatch, delegated_type: type[_DelegatedGeneration]):
    coordinator = _Coordinator()
    base_generation = SimpleNamespace(
        chat=SimpleNamespace(repository=object()),
        provider=object(),
        interactive_demand=None,
    )
    monkeypatch.setattr(durable_module, "ChatGenerationService", delegated_type)
    monkeypatch.setattr(
        durable_module,
        "validate_grounded_request_context_binding",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        durable_module,
        "validate_grounded_snapshot_current",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        durable_module,
        "bind_grounded_processing_run",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        durable_module,
        "complete_grounded_processing_run",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        durable_module,
        "fail_grounded_processing_run",
        lambda *args, **kwargs: None,
    )
    return (
        DurableGroundedGenerationService(
            cast(Any, base_generation),
            cast(Any, coordinator),
        ),
        coordinator,
    )


def _user_message(operation_id: uuid.UUID) -> object:
    return SimpleNamespace(
        message_id=operation_id,
        actor_id=uuid.uuid4(),
    )


def test_durable_generation_persists_exact_package_before_provider_guard(monkeypatch) -> None:
    operation_id = uuid.uuid4()
    chat_id = uuid.uuid4()
    fingerprint = object()
    context_package = object()
    service, coordinator = _service(monkeypatch, _DelegatedGeneration)
    result = service.send_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        user_message=cast(Any, _user_message(operation_id)),
        context_package=cast(Any, context_package),
        processing_run_id=uuid.uuid4(),
        fingerprint=cast(Any, fingerprint),
        receipt_payload_builder=lambda content, provider_id, model_id: "{}",
    )
    assert result is _RESULT
    assert coordinator.context_packages == [(operation_id, chat_id, context_package)]
    assert coordinator.calls == [(operation_id, chat_id, fingerprint)]
    assert coordinator.events == ["package", "guard"]


def test_external_provider_hook_precedes_irreversible_guard(monkeypatch) -> None:
    operation_id = uuid.uuid4()
    chat_id = uuid.uuid4()
    fingerprint = object()
    service, coordinator = _service(monkeypatch, _DelegatedGeneration)
    result = service.send_context_package(
        operation_id=operation_id,
        chat_id=chat_id,
        user_message=cast(Any, _user_message(operation_id)),
        context_package=cast(Any, object()),
        processing_run_id=uuid.uuid4(),
        fingerprint=cast(Any, fingerprint),
        receipt_payload_builder=lambda content, provider_id, model_id: "{}",
        on_before_provider_call=lambda: coordinator.events.append("hook"),
    )
    assert result is _RESULT
    assert coordinator.events == ["package", "hook", "guard"]


def test_internal_grounding_retry_is_fenced_before_second_hook(monkeypatch) -> None:
    operation_id = uuid.uuid4()
    chat_id = uuid.uuid4()
    fingerprint = object()
    service, coordinator = _service(monkeypatch, _RetryingDelegatedGeneration)
    with pytest.raises(GroundedProviderBoundaryError) as exc_info:
        service.send_context_package(
            operation_id=operation_id,
            chat_id=chat_id,
            user_message=cast(Any, _user_message(operation_id)),
            context_package=cast(Any, object()),
            processing_run_id=uuid.uuid4(),
            fingerprint=cast(Any, fingerprint),
            receipt_payload_builder=lambda content, provider_id, model_id: "{}",
            on_before_provider_call=lambda: coordinator.events.append("hook"),
        )
    assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS
    assert coordinator.calls == [(operation_id, chat_id, fingerprint)]
    assert coordinator.events == ["package", "hook", "guard"]
