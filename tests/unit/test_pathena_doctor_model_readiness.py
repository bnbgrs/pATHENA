from __future__ import annotations

from athena.config.settings import AthenaSettings
from athena.doctor import _check_model
from athena.model.domain import ModelInfo, ProviderHealth, ProviderHealthStatus


class _Provider:
    def __init__(self, models: tuple[ModelInfo, ...]) -> None:
        self.base_url = "http://127.0.0.1:1234"
        self._models = models

    def health(self) -> ProviderHealth:
        return ProviderHealth(ProviderHealthStatus.READY)

    def discover_models(self) -> tuple[ModelInfo, ...]:
        return self._models


def _model(*, model_type: str, loaded: bool, model_id: str) -> ModelInfo:
    return ModelInfo(
        provider="lm_studio",
        backend_model_id=model_id,
        display_name=model_id,
        model_type=model_type,
        context_capacity=32768,
        quantization=None,
        loaded=loaded,
        vision=False,
        trained_for_tool_use=False,
        loaded_context_length=32768 if loaded else None,
    )


def _settings() -> AthenaSettings:
    return AthenaSettings(local_root=__import__("pathlib").Path.cwd().resolve())


def test_doctor_warns_when_server_has_no_loaded_llm(monkeypatch) -> None:
    provider = _Provider(
        (
            _model(model_type="llm", loaded=False, model_id="available-llm"),
            _model(model_type="embedding", loaded=True, model_id="loaded-embedding"),
        )
    )
    monkeypatch.setattr(
        "athena.doctor.LMStudioProvider",
        lambda **_kwargs: provider,
    )

    result = _check_model(_settings())

    assert result.status == "WARN"
    assert "loaded_llms=0" in result.detail


def test_doctor_passes_only_with_loaded_llm(monkeypatch) -> None:
    provider = _Provider(
        (_model(model_type="llm", loaded=True, model_id="local-chat"),)
    )
    monkeypatch.setattr(
        "athena.doctor.LMStudioProvider",
        lambda **_kwargs: provider,
    )

    result = _check_model(_settings())

    assert result.status == "PASS"
    assert "local-chat" in result.detail
