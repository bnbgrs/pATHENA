from __future__ import annotations

import pytest

from athena.model.domain import (
    ModelCapabilities,
    ModelCapabilitySupport,
    ModelInfo,
)
from athena.model.registry import (
    ModelLoadOwnership,
    ModelRegistry,
    ModelRegistryError,
)


def _model(*, loaded: bool) -> ModelInfo:
    return ModelInfo(
        provider="provider",
        backend_model_id="model",
        display_name="Model",
        model_type="llm",
        context_capacity=8192,
        quantization=None,
        loaded=loaded,
        vision=None,
        trained_for_tool_use=None,
        capabilities=ModelCapabilities(chat=ModelCapabilitySupport.SUPPORTED),
    )


def test_unknown_load_ownership_fails_closed_for_automatic_unload() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=True),))

    assert registry.automatic_unload_allowed(provider="provider", model_id="model") is False


def test_externally_loaded_model_cannot_be_automatically_unloaded() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=True),))
    registry.record_load_ownership(
        provider="provider",
        model_id="model",
        ownership=ModelLoadOwnership.LOADED_EXTERNALLY,
    )

    assert registry.automatic_unload_allowed(provider="provider", model_id="model") is False


def test_only_athena_owned_load_allows_automatic_unload() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=True),))
    registry.record_load_ownership(
        provider="provider",
        model_id="model",
        ownership=ModelLoadOwnership.LOADED_BY_ATHENA,
    )

    assert registry.automatic_unload_allowed(provider="provider", model_id="model") is True


def test_unloaded_model_cannot_be_marked_as_owned_load() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=False),))

    with pytest.raises(ModelRegistryError, match="only be assigned to a loaded model"):
        registry.record_load_ownership(
            provider="provider",
            model_id="model",
            ownership=ModelLoadOwnership.LOADED_BY_ATHENA,
        )


def test_refresh_clears_ownership_after_model_becomes_unloaded() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=True),))
    registry.record_load_ownership(
        provider="provider",
        model_id="model",
        ownership=ModelLoadOwnership.LOADED_BY_ATHENA,
    )

    (entry,) = registry.refresh((_model(loaded=False),))

    assert entry.load_ownership is ModelLoadOwnership.UNKNOWN
    assert entry.automatic_unload_allowed is False


def test_refresh_preserves_known_ownership_while_instance_stays_loaded() -> None:
    registry = ModelRegistry()
    registry.refresh((_model(loaded=True),))
    registry.record_load_ownership(
        provider="provider",
        model_id="model",
        ownership=ModelLoadOwnership.LOADED_EXTERNALLY,
    )

    (entry,) = registry.refresh((_model(loaded=True),))

    assert entry.load_ownership is ModelLoadOwnership.LOADED_EXTERNALLY
