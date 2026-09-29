from __future__ import annotations

import pytest

from athena.api.service import CoreApiFacade
from athena.model.domain import ModelInfo


def _model(
    model_id: str,
    *,
    loaded: bool,
    context: int | None = None,
) -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id=model_id,
        display_name=model_id,
        model_type="llm",
        context_capacity=32768,
        quantization="Q4",
        loaded=loaded,
        vision=False,
        trained_for_tool_use=True,
        loaded_context_length=context if loaded else None,
    )


class _ManagedProvider:
    provider_id = "lm_studio"

    def __init__(self, *, fail_target: str | None = None) -> None:
        self.fail_target = fail_target
        self.models = {
            "old/model": _model("old/model", loaded=True, context=8192),
            "new/model": _model("new/model", loaded=False),
        }
        self.events: list[tuple[str, str, int | None]] = []

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return tuple(self.models.values())

    def load_model(
        self,
        model_id: str,
        *,
        context_length: int | None = None,
    ) -> ModelInfo:
        self.events.append(("load", model_id, context_length))
        if model_id == self.fail_target:
            raise RuntimeError("synthetic load failure")
        current = self.models[model_id]
        loaded = _model(
            model_id,
            loaded=True,
            context=context_length or current.loaded_context_length or 8192,
        )
        self.models[model_id] = loaded
        return loaded

    def unload_model(self, model_id: str) -> None:
        self.events.append(("unload", model_id, None))
        self.models[model_id] = _model(model_id, loaded=False)


def _facade(provider: _ManagedProvider) -> CoreApiFacade:
    return CoreApiFacade(
        health=None,  # type: ignore[arg-type]
        chat=None,  # type: ignore[arg-type]
        model_provider=provider,  # type: ignore[arg-type]
    )


def test_model_switch_frees_old_vram_before_loading_new_model() -> None:
    provider = _ManagedProvider()
    result = _facade(provider).activate_model(
        "new/model",
        context_length=12288,
        unload_others=True,
    )

    assert result.backend_model_id == "new/model"
    assert result.loaded is True
    assert provider.events[:2] == [
        ("unload", "old/model", None),
        ("load", "new/model", 12288),
    ]
    assert provider.models["old/model"].loaded is False
    assert provider.models["new/model"].loaded is True


def test_failed_model_switch_restores_previous_loaded_model() -> None:
    provider = _ManagedProvider(fail_target="new/model")

    with pytest.raises(RuntimeError, match="synthetic load failure"):
        _facade(provider).activate_model(
            "new/model",
            context_length=12288,
            unload_others=True,
        )

    assert provider.events == [
        ("unload", "old/model", None),
        ("load", "new/model", 12288),
        ("load", "old/model", 8192),
    ]
    assert provider.models["old/model"].loaded is True
    assert provider.models["old/model"].loaded_context_length == 8192


def test_already_loaded_target_is_kept_while_other_models_are_released() -> None:
    provider = _ManagedProvider()
    provider.models["new/model"] = _model(
        "new/model",
        loaded=True,
        context=16384,
    )

    result = _facade(provider).activate_model(
        "new/model",
        context_length=12288,
        unload_others=True,
    )

    assert result.backend_model_id == "new/model"
    assert provider.events[0] == ("load", "new/model", 12288)
    assert provider.events[1] == ("unload", "old/model", None)
