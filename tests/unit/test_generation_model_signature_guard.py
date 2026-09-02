from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import cast

import pytest

from athena.chat.generation import ChatGenerationService, ModelSelectionError
from athena.chat.models import MessageType
from athena.model.domain import ModelChatMessage, ModelInfo
from athena.model.signature_guard import ModelSignatureDriftError


class _Provider:
    def __init__(self, model: ModelInfo) -> None:
        self.model = model
        self.stream_calls = 0

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return (self.model,)

    def stream_chat(self, **_kwargs: object) -> tuple[str, ...]:
        self.stream_calls += 1
        return ("ok",)


class _Chat:
    def add_assistant_message(self, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(**kwargs)


class _Package:
    def __init__(self, *, revision: str | None) -> None:
        self.model_signature = SimpleNamespace(
            provider="lm_studio",
            model_identifier="primary",
            model_revision=revision,
            quantization="Q4_K_M",
        )
        self.budget = SimpleNamespace(effective_context_limit=4096)

    def current_user_ref(self) -> SimpleNamespace:
        return SimpleNamespace(
            entity_id=_USER_ID,
            revision_id=_REVISION_ID,
        )

    def model_messages(self) -> tuple[ModelChatMessage, ...]:
        return (ModelChatMessage(role="user", content="hello"),)

    def generation_controls(self) -> tuple[None, None]:
        return (None, None)

    def generation_temperature(self) -> None:
        return None


_CHAT_ID = uuid.uuid4()
_USER_ID = uuid.uuid4()
_REVISION_ID = uuid.uuid4()
_USER = SimpleNamespace(
    chat_id=_CHAT_ID,
    message_type=MessageType.USER,
    content="hello",
    message_id=_USER_ID,
    revision_id=_REVISION_ID,
)


def _model(*, revision: str | None) -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id="primary",
        display_name="Primary",
        model_type="llm",
        context_capacity=8192,
        quantization="Q4_K_M",
        loaded=True,
        vision=False,
        trained_for_tool_use=False,
        model_revision=revision,
    )


def test_generation_rejects_pinned_revision_drift_before_provider_call() -> None:
    provider = _Provider(_model(revision="rev-2"))
    service = ChatGenerationService(
        chat=cast(object, _Chat()),  # type: ignore[arg-type]
        provider=cast(object, provider),  # type: ignore[arg-type]
    )

    with pytest.raises(ModelSelectionError, match="ModelSignature") as exc_info:
        service.send_context_package(
            chat_id=_CHAT_ID,
            user_message=cast(object, _USER),  # type: ignore[arg-type]
            context_package=cast(object, _Package(revision="rev-1")),  # type: ignore[arg-type]
        )

    assert isinstance(exc_info.value.__cause__, ModelSignatureDriftError)
    assert provider.stream_calls == 0


def test_generation_preserves_legacy_unknown_revision_compatibility() -> None:
    provider = _Provider(_model(revision="later-observed"))
    service = ChatGenerationService(
        chat=cast(object, _Chat()),  # type: ignore[arg-type]
        provider=cast(object, provider),  # type: ignore[arg-type]
    )

    result = service.send_context_package(
        chat_id=_CHAT_ID,
        user_message=cast(object, _USER),  # type: ignore[arg-type]
        context_package=cast(object, _Package(revision=None)),  # type: ignore[arg-type]
    )

    assert result.model.model_revision == "later-observed"
    assert provider.stream_calls == 1
