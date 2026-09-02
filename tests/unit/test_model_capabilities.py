from __future__ import annotations

import pytest

from athena.model.domain import (
    ModelCapabilities,
    ModelCapabilitySupport,
    ModelInfo,
)


def _model_info(**overrides: object) -> ModelInfo:
    values: dict[str, object] = {
        "provider": "provider",
        "backend_model_id": "model",
        "display_name": "Model",
        "model_type": "llm",
        "context_capacity": None,
        "quantization": None,
        "loaded": False,
        "vision": None,
        "trained_for_tool_use": None,
    }
    values.update(overrides)
    return ModelInfo(**values)  # type: ignore[arg-type]


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
    assert _model_info().capabilities == ModelCapabilities()


def test_model_info_normalizes_observed_discovery_capabilities() -> None:
    info = _model_info(
        context_capacity=8192,
        vision=False,
        trained_for_tool_use=True,
    )

    assert info.capabilities.context_length is ModelCapabilitySupport.SUPPORTED
    assert info.capabilities.vision is ModelCapabilitySupport.UNSUPPORTED
    assert info.capabilities.tool_calls is ModelCapabilitySupport.SUPPORTED
    assert info.capabilities.audio is ModelCapabilitySupport.UNKNOWN


def test_model_info_preserves_unrelated_explicit_capabilities() -> None:
    info = _model_info(
        capabilities=ModelCapabilities(
            chat=ModelCapabilitySupport.SUPPORTED,
            streaming=ModelCapabilitySupport.SUPPORTED,
            audio=ModelCapabilitySupport.UNSUPPORTED,
        )
    )

    assert info.capabilities.chat is ModelCapabilitySupport.SUPPORTED
    assert info.capabilities.streaming is ModelCapabilitySupport.SUPPORTED
    assert info.capabilities.audio is ModelCapabilitySupport.UNSUPPORTED
    assert info.capabilities.vision is ModelCapabilitySupport.UNKNOWN


def test_model_info_rejects_capability_that_contradicts_provider_metadata() -> None:
    with pytest.raises(ValueError, match="vision capability contradicts"):
        _model_info(
            vision=False,
            capabilities=ModelCapabilities(
                vision=ModelCapabilitySupport.SUPPORTED,
            ),
        )


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
