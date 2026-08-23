from __future__ import annotations

import pytest

from athena.model.domain import (
    ModelCapabilities,
    ModelCapabilitySupport,
    ModelInfo,
)


def test_model_capabilities_default_to_unknown_without_provider_evidence() -> None:
    capabilities = ModelCapabilities()

    assert {
        capabilities.chat,
        capabilities.structured_output,
        capabilities.tool_calls,
        capabilities.vision,
        capabilities.audio,
        capabilities.context_length,
        capabilities.streaming,
        capabilities.model_load_control,
    } == {ModelCapabilitySupport.UNKNOWN}


def test_model_capabilities_preserve_supported_unsupported_and_unknown() -> None:
    capabilities = ModelCapabilities(
        chat=ModelCapabilitySupport.SUPPORTED,
        tool_calls=ModelCapabilitySupport.UNSUPPORTED,
        audio=ModelCapabilitySupport.UNKNOWN,
    )

    assert capabilities.chat is ModelCapabilitySupport.SUPPORTED
    assert capabilities.tool_calls is ModelCapabilitySupport.UNSUPPORTED
    assert capabilities.audio is ModelCapabilitySupport.UNKNOWN


def test_model_info_defaults_to_unknown_capabilities_for_legacy_callers() -> None:
    info = ModelInfo(
        provider="provider",
        backend_model_id="model",
        display_name="Model",
        model_type="llm",
        context_capacity=None,
        quantization=None,
        loaded=False,
        vision=None,
        trained_for_tool_use=None,
    )

    assert info.capabilities == ModelCapabilities()


@pytest.mark.parametrize(
    "field",
    [
        "chat",
        "structured_output",
        "tool_calls",
        "vision",
        "audio",
        "context_length",
        "streaming",
        "model_load_control",
    ],
)
def test_model_capabilities_reject_non_enum_values(field: str) -> None:
    with pytest.raises(TypeError, match=field):
        ModelCapabilities(**{field: "supported"})  # type: ignore[arg-type]
