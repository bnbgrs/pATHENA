from __future__ import annotations

import uuid

import pytest

from athena.model.domain import (
    ModelCapabilities,
    ModelCapabilitySupport,
    ModelInfo,
)
from athena.model.registry import (
    ModelRegistry,
    ModelRegistryError,
    ModelResourceProfile,
    ModelRoleEligibility,
)


def _model(
    model_id: str,
    *,
    provider: str = "provider",
    model_type: str = "llm",
    chat: ModelCapabilitySupport = ModelCapabilitySupport.SUPPORTED,
    structured_output: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN,
) -> ModelInfo:
    return ModelInfo(
        provider=provider,
        backend_model_id=model_id,
        display_name=model_id,
        model_type=model_type,
        context_capacity=8192,
        quantization=None,
        loaded=False,
        vision=None,
        trained_for_tool_use=None,
        capabilities=ModelCapabilities(
            chat=chat,
            structured_output=structured_output,
        ),
    )


def test_registry_enforces_one_active_primary() -> None:
    registry = ModelRegistry()
    first = _model("first")
    second = _model("second")
    registry.refresh((first, second))

    registry.activate_primary(provider="provider", model_id="first")
    activated = registry.activate_primary(provider="provider", model_id="second")

    assert activated.active_primary is True
    assert registry.active_primary() == activated
    assert registry.get(provider="provider", model_id="first").active_primary is False
    assert sum(entry.active_primary for entry in registry.entries()) == 1


def test_registry_fails_closed_for_unknown_required_capability() -> None:
    registry = ModelRegistry()
    model = _model("unknown-chat", chat=ModelCapabilitySupport.UNKNOWN)

    (entry,) = registry.refresh((model,))

    assert entry.eligibility is ModelRoleEligibility.INELIGIBLE
    with pytest.raises(ModelRegistryError, match="not eligible"):
        registry.activate_primary(provider="provider", model_id="unknown-chat")


def test_registry_keeps_infrastructure_models_ineligible() -> None:
    registry = ModelRegistry()
    embedding = _model("embed", model_type="embedding")

    (entry,) = registry.refresh((embedding,))

    assert entry.eligibility is ModelRoleEligibility.INELIGIBLE


def test_registry_evaluates_active_workflow_requirements() -> None:
    registry = ModelRegistry()
    model = _model(
        "structured",
        structured_output=ModelCapabilitySupport.UNKNOWN,
    )

    (entry,) = registry.refresh(
        (model,),
        required_capabilities=("chat", "structured_output"),
    )

    assert entry.eligibility is ModelRoleEligibility.INELIGIBLE


def test_refresh_preserves_operator_metadata_for_same_identity() -> None:
    registry = ModelRegistry()
    original = _model("primary")
    registry.refresh((original,))
    registry.set_alias(provider="provider", model_id="primary", alias="Writer")
    resources = ModelResourceProfile(
        vram_peak_bytes=1234,
        ram_peak_bytes=5678,
        load_time_seconds=1.25,
        tokens_per_second=42.0,
    )
    registry.set_resource_profile(
        provider="provider",
        model_id="primary",
        resources=resources,
    )
    registry.activate_primary(provider="provider", model_id="primary")

    refreshed_model = ModelInfo(
        provider="provider",
        backend_model_id="primary",
        display_name="Primary v2",
        model_type="llm",
        context_capacity=16384,
        quantization="Q4",
        loaded=True,
        vision=None,
        trained_for_tool_use=None,
        capabilities=ModelCapabilities(chat=ModelCapabilitySupport.SUPPORTED),
    )
    (entry,) = registry.refresh((refreshed_model,))

    assert entry.model == refreshed_model
    assert entry.user_alias == "Writer"
    assert entry.resources == resources
    assert entry.active_primary is True


def test_refresh_clears_active_primary_when_model_disappears() -> None:
    registry = ModelRegistry()
    registry.refresh((_model("primary"),))
    registry.activate_primary(provider="provider", model_id="primary")

    assert registry.refresh(()) == ()
    assert registry.active_primary() is None


def test_refresh_rejects_duplicate_provider_model_identity() -> None:
    registry = ModelRegistry()
    duplicate = _model("same")

    with pytest.raises(ModelRegistryError, match="duplicate model identities"):
        registry.refresh((duplicate, duplicate))


def test_resource_profile_rejects_non_finite_measurements() -> None:
    with pytest.raises(ModelRegistryError, match="finite"):
        ModelResourceProfile(tokens_per_second=float("nan"))


def test_registry_identity_is_provider_scoped() -> None:
    registry = ModelRegistry()
    left = _model("same", provider="left")
    right = _model("same", provider="right")

    entries = registry.refresh((left, right))

    assert {entry.identity for entry in entries} == {
        ("left", "same"),
        ("right", "same"),
    }
    assert uuid.UUID(int=0).int == 0  # Keep this test module import-only deterministic.
