"""Core-owned runtime registry for primary-model selection."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import Enum

from athena.model.domain import ModelCapabilitySupport, ModelInfo

_INFRASTRUCTURE_MODEL_TYPES = frozenset(
    {
        "embedding",
        "embeddings",
        "ocr",
        "reranker",
        "speech_to_text",
        "stt",
        "text_to_speech",
        "tts",
    }
)
_CAPABILITY_NAMES = frozenset(
    {
        "chat",
        "structured_output",
        "tool_calls",
        "vision",
        "audio",
        "context_length",
        "streaming",
        "model_load_control",
    }
)


class ModelRegistryError(ValueError):
    """Raised when registry state would violate a primary-model invariant."""


class ModelRoleEligibility(str, Enum):
    PRIMARY = "primary"
    INELIGIBLE = "ineligible"


class ModelLoadOwnership(str, Enum):
    """Who owns one currently loaded model instance."""

    LOADED_BY_ATHENA = "loaded_by_athena"
    LOADED_EXTERNALLY = "loaded_externally"
    UNKNOWN = "unknown"


def _optional_nonnegative_int(value: object, label: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ModelRegistryError(f"{label} must be a non-negative integer or None.")


def _optional_nonnegative_float(value: object, label: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModelRegistryError(f"{label} must be a non-negative number or None.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ModelRegistryError(f"{label} must be finite and non-negative.") from exc
    if not math.isfinite(normalized) or normalized < 0.0:
        raise ModelRegistryError(f"{label} must be finite and non-negative.")


@dataclass(frozen=True, slots=True)
class ModelResourceProfile:
    """Measured performance metadata; absent values remain unknown."""

    vram_peak_bytes: int | None = None
    ram_peak_bytes: int | None = None
    load_time_seconds: float | None = None
    tokens_per_second: float | None = None

    def __post_init__(self) -> None:
        _optional_nonnegative_int(self.vram_peak_bytes, "vram_peak_bytes")
        _optional_nonnegative_int(self.ram_peak_bytes, "ram_peak_bytes")
        _optional_nonnegative_float(self.load_time_seconds, "load_time_seconds")
        _optional_nonnegative_float(self.tokens_per_second, "tokens_per_second")


@dataclass(frozen=True, slots=True)
class ModelRegistryEntry:
    model: ModelInfo
    eligibility: ModelRoleEligibility
    user_alias: str | None = None
    active_primary: bool = False
    resources: ModelResourceProfile = ModelResourceProfile()
    load_ownership: ModelLoadOwnership = ModelLoadOwnership.UNKNOWN

    def __post_init__(self) -> None:
        if not isinstance(self.model, ModelInfo):
            raise TypeError("Registry model must be ModelInfo.")
        if not isinstance(self.eligibility, ModelRoleEligibility):
            raise TypeError("Registry eligibility must be ModelRoleEligibility.")
        if self.user_alias is not None:
            if not isinstance(self.user_alias, str):
                raise TypeError("Registry alias must be text or None.")
            if not self.user_alias.strip() or self.user_alias != self.user_alias.strip():
                raise ModelRegistryError("Registry alias must be canonical non-empty text.")
        if not isinstance(self.active_primary, bool):
            raise TypeError("Registry active_primary must be bool.")
        if not isinstance(self.resources, ModelResourceProfile):
            raise TypeError("Registry resources must be ModelResourceProfile.")
        if not isinstance(self.load_ownership, ModelLoadOwnership):
            raise TypeError("Registry load_ownership must be ModelLoadOwnership.")
        if self.active_primary and self.eligibility is not ModelRoleEligibility.PRIMARY:
            raise ModelRegistryError("An ineligible model cannot be the active primary model.")
        if not self.model.loaded and self.load_ownership is not ModelLoadOwnership.UNKNOWN:
            raise ModelRegistryError("An unloaded model cannot retain load ownership.")

    @property
    def identity(self) -> tuple[str, str]:
        return self.model.provider, self.model.backend_model_id

    @property
    def automatic_unload_allowed(self) -> bool:
        return self.load_ownership is ModelLoadOwnership.LOADED_BY_ATHENA


class ModelRegistry:
    """In-memory Configuration/Runtime registry for Primary Model candidates.

    Discovery refreshes technical model facts while preserving operator-owned
    alias/resource metadata. Infrastructure model types are never primary
    candidates. Unknown capability support fails closed for required workflow
    capabilities rather than being treated as supported. Load ownership is also
    fail-closed: only a model explicitly recorded as loaded by ATHENA may be
    automatically unloaded. A generic discovery refresh clears ownership because
    discovery does not prove that a loaded backend instance is the same instance
    ATHENA previously created.
    """

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], ModelRegistryEntry] = {}
        self._active_identity: tuple[str, str] | None = None

    def entries(self) -> tuple[ModelRegistryEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    def get(self, *, provider: str, model_id: str) -> ModelRegistryEntry:
        key = _identity(provider, model_id)
        try:
            return self._entries[key]
        except KeyError as exc:
            raise ModelRegistryError("Model is not present in the primary-model registry.") from exc

    def refresh(
        self,
        models: tuple[ModelInfo, ...],
        *,
        required_capabilities: tuple[str, ...] = ("chat",),
    ) -> tuple[ModelRegistryEntry, ...]:
        if not isinstance(models, tuple) or not all(isinstance(item, ModelInfo) for item in models):
            raise TypeError("Registry refresh models must be a tuple of ModelInfo values.")
        required = _required_capabilities(required_capabilities)
        identities = [(item.provider, item.backend_model_id) for item in models]
        if len(set(identities)) != len(identities):
            raise ModelRegistryError("Registry refresh contains duplicate model identities.")

        refreshed: dict[tuple[str, str], ModelRegistryEntry] = {}
        for model in models:
            key = (model.provider, model.backend_model_id)
            prior = self._entries.get(key)
            eligibility = _eligibility(model, required)
            active = key == self._active_identity and eligibility is ModelRoleEligibility.PRIMARY
            refreshed[key] = ModelRegistryEntry(
                model=model,
                eligibility=eligibility,
                user_alias=None if prior is None else prior.user_alias,
                active_primary=active,
                resources=ModelResourceProfile() if prior is None else prior.resources,
                load_ownership=ModelLoadOwnership.UNKNOWN,
            )

        self._entries = refreshed
        active_identity = self._active_identity
        if active_identity is None:
            return self.entries()
        active_entry = refreshed.get(active_identity)
        if active_entry is None or not active_entry.active_primary:
            self._active_identity = None
        return self.entries()

    def set_alias(self, *, provider: str, model_id: str, alias: str | None) -> ModelRegistryEntry:
        key = _identity(provider, model_id)
        current = self.get(provider=provider, model_id=model_id)
        normalized: str | None
        if alias is None:
            normalized = None
        elif not isinstance(alias, str):
            raise TypeError("Registry alias must be text or None.")
        else:
            normalized = alias.strip()
            if not normalized:
                raise ModelRegistryError("Registry alias must not be empty.")
        updated = replace(current, user_alias=normalized)
        self._entries[key] = updated
        return updated

    def set_resource_profile(
        self,
        *,
        provider: str,
        model_id: str,
        resources: ModelResourceProfile,
    ) -> ModelRegistryEntry:
        if not isinstance(resources, ModelResourceProfile):
            raise TypeError("resources must be a ModelResourceProfile.")
        key = _identity(provider, model_id)
        updated = replace(self.get(provider=provider, model_id=model_id), resources=resources)
        self._entries[key] = updated
        return updated

    def record_load_ownership(
        self,
        *,
        provider: str,
        model_id: str,
        ownership: ModelLoadOwnership,
    ) -> ModelRegistryEntry:
        if not isinstance(ownership, ModelLoadOwnership):
            raise TypeError("ownership must be ModelLoadOwnership.")
        key = _identity(provider, model_id)
        current = self.get(provider=provider, model_id=model_id)
        if not current.model.loaded and ownership is not ModelLoadOwnership.UNKNOWN:
            raise ModelRegistryError("Load ownership can only be assigned to a loaded model.")
        updated = replace(current, load_ownership=ownership)
        self._entries[key] = updated
        return updated

    def automatic_unload_allowed(self, *, provider: str, model_id: str) -> bool:
        return self.get(provider=provider, model_id=model_id).automatic_unload_allowed

    def activate_primary(self, *, provider: str, model_id: str) -> ModelRegistryEntry:
        key = _identity(provider, model_id)
        requested = self.get(provider=provider, model_id=model_id)
        if requested.eligibility is not ModelRoleEligibility.PRIMARY:
            raise ModelRegistryError("Model is not eligible for the active primary role.")

        active_identity = self._active_identity
        if active_identity is not None and active_identity in self._entries:
            prior = self._entries[active_identity]
            self._entries[active_identity] = replace(prior, active_primary=False)
        activated = replace(requested, active_primary=True)
        self._entries[key] = activated
        self._active_identity = key
        return activated

    def deactivate_primary(self) -> None:
        active_identity = self._active_identity
        if active_identity is not None and active_identity in self._entries:
            current = self._entries[active_identity]
            self._entries[active_identity] = replace(current, active_primary=False)
        self._active_identity = None

    def active_primary(self) -> ModelRegistryEntry | None:
        active_identity = self._active_identity
        if active_identity is None:
            return None
        return self._entries.get(active_identity)


def _identity(provider: object, model_id: object) -> tuple[str, str]:
    if not isinstance(provider, str) or not provider.strip() or provider != provider.strip():
        raise ModelRegistryError("Registry provider must be canonical non-empty text.")
    if not isinstance(model_id, str) or not model_id.strip() or model_id != model_id.strip():
        raise ModelRegistryError("Registry model_id must be canonical non-empty text.")
    return provider, model_id


def _required_capabilities(value: object) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError("required_capabilities must be a tuple of capability names.")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or item not in _CAPABILITY_NAMES:
            raise ModelRegistryError("required_capabilities contains an unknown capability name.")
        if item in normalized:
            raise ModelRegistryError("required_capabilities must not contain duplicates.")
        normalized.append(item)
    return tuple(normalized)


def _eligibility(
    model: ModelInfo,
    required_capabilities: tuple[str, ...],
) -> ModelRoleEligibility:
    if model.model_type.strip().casefold() in _INFRASTRUCTURE_MODEL_TYPES:
        return ModelRoleEligibility.INELIGIBLE
    for name in required_capabilities:
        if getattr(model.capabilities, name) is not ModelCapabilitySupport.SUPPORTED:
            return ModelRoleEligibility.INELIGIBLE
    return ModelRoleEligibility.PRIMARY
