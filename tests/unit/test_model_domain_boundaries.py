from __future__ import annotations

import pytest

from athena.model.domain import (
    ModelChatMessage,
    ModelInfo,
    ProviderHealth,
    ProviderHealthStatus,
)


def _model(**overrides: object) -> ModelInfo:
    values: dict[str, object] = {
        "provider": "lmstudio",
        "backend_model_id": "local/model",
        "display_name": "Local Model",
        "model_type": "llm",
        "context_capacity": 8192,
        "quantization": "Q4",
        "loaded": True,
        "vision": False,
        "trained_for_tool_use": None,
        "loaded_context_length": 4096,
    }
    values.update(overrides)
    return ModelInfo(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("context_capacity", True),
        ("context_capacity", 1.5),
        ("context_capacity", 0),
        ("loaded_context_length", False),
        ("loaded_context_length", 1.5),
        ("loaded_context_length", 0),
    ],
)
def test_model_info_rejects_invalid_context_metadata(field: str, value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _model(**{field: value})


def test_model_info_rejects_loaded_context_above_capacity() -> None:
    with pytest.raises(ValueError, match="must not exceed"):
        _model(context_capacity=4096, loaded_context_length=8192)


@pytest.mark.parametrize("field", ["provider", "backend_model_id", "display_name", "model_type"])
def test_model_info_rejects_empty_identity_text(field: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        _model(**{field: "   "})


@pytest.mark.parametrize("field", ["vision", "trained_for_tool_use"])
def test_model_info_rejects_non_boolean_capability_flags(field: str) -> None:
    with pytest.raises(TypeError, match="bool or None"):
        _model(**{field: 1})


def test_model_info_rejects_non_boolean_loaded_flag() -> None:
    with pytest.raises(TypeError, match="loaded must be bool"):
        _model(loaded=1)


def test_provider_health_rejects_untyped_status() -> None:
    with pytest.raises(TypeError, match="ProviderHealthStatus"):
        ProviderHealth(status="ready")  # type: ignore[arg-type]


def test_provider_health_accepts_empty_detail_for_backend_diagnostics() -> None:
    health = ProviderHealth(status=ProviderHealthStatus.READY, detail="")
    assert health.detail == ""


def test_model_chat_message_requires_text_role_and_content() -> None:
    with pytest.raises(ValueError, match="role must not be empty"):
        ModelChatMessage(role=" ", content="hello")
    with pytest.raises(TypeError, match="content must be text"):
        ModelChatMessage(role="user", content=1)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "role",
    [" user", "user ", "tool", "developer", "system\nuser", "USER"],
)
def test_model_chat_message_rejects_noncanonical_or_unsupported_roles(role: str) -> None:
    with pytest.raises(ValueError, match="system, user, assistant"):
        ModelChatMessage(role=role, content="hello")


@pytest.mark.parametrize("role", ["system", "user", "assistant"])
def test_model_chat_message_accepts_supported_roles(role: str) -> None:
    message = ModelChatMessage(role=role, content="hello")
    assert message.role == role
