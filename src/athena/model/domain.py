"""Stable model-provider domain types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

_MODEL_CHAT_ROLES = frozenset({"system", "user", "assistant"})


class ProviderHealthStatus(str, Enum):
    """Normalized provider health states used by the Core."""

    UNAVAILABLE = "unavailable"
    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    DEGRADED = "degraded"
    ERROR = "error"


class ModelCapabilitySupport(str, Enum):
    """Observed support state for one model/provider capability.

    UNKNOWN is intentionally distinct from UNSUPPORTED: provider metadata may
    omit a capability without proving that the model cannot perform it.
    """

    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


def _require_text(value: object, label: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{label} must not be empty.")


def _require_canonical_text(value: object, label: str) -> None:
    _require_text(value, label)
    assert isinstance(value, str)
    if value != value.strip():
        raise ValueError(f"{label} must use canonical trimmed text.")


def _require_optional_canonical_text(value: object, label: str) -> None:
    if value is None:
        return
    _require_canonical_text(value, label)


def _require_optional_positive_int(value: object, label: str) -> None:
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer or None.")
    if value < 1:
        raise ValueError(f"{label} must be >= 1.")


def _require_optional_bool(value: object, label: str) -> None:
    if value is not None and not isinstance(value, bool):
        raise TypeError(f"{label} must be bool or None.")


def _support_from_optional_bool(value: bool | None) -> ModelCapabilitySupport:
    if value is True:
        return ModelCapabilitySupport.SUPPORTED
    if value is False:
        return ModelCapabilitySupport.UNSUPPORTED
    return ModelCapabilitySupport.UNKNOWN


def _merge_observed_capability(
    *,
    declared: ModelCapabilitySupport,
    observed: ModelCapabilitySupport,
    label: str,
) -> ModelCapabilitySupport:
    if observed is ModelCapabilitySupport.UNKNOWN:
        return declared
    if declared is ModelCapabilitySupport.UNKNOWN:
        return observed
    if declared is not observed:
        raise ValueError(
            f"ModelInfo {label} capability contradicts normalized provider metadata."
        )
    return declared


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Health snapshot without backend-specific exception leakage."""

    status: ProviderHealthStatus
    detail: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, ProviderHealthStatus):
            raise TypeError("ProviderHealth status must be a ProviderHealthStatus.")
        if self.detail is not None and not isinstance(self.detail, str):
            raise TypeError("ProviderHealth detail must be text or None.")


@dataclass(frozen=True, slots=True)
class ModelCapabilities:
    """Normalized, evidence-preserving model/provider capabilities."""

    chat: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    structured_output: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    tool_calls: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    vision: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    audio: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    context_length: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    streaming: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN
    model_load_control: ModelCapabilitySupport = ModelCapabilitySupport.UNKNOWN

    def __post_init__(self) -> None:
        for name, value in (
            ("chat", self.chat),
            ("structured_output", self.structured_output),
            ("tool_calls", self.tool_calls),
            ("vision", self.vision),
            ("audio", self.audio),
            ("context_length", self.context_length),
            ("streaming", self.streaming),
            ("model_load_control", self.model_load_control),
        ):
            if not isinstance(value, ModelCapabilitySupport):
                raise TypeError(
                    f"ModelCapabilities {name} must be a ModelCapabilitySupport."
                )


@dataclass(frozen=True, slots=True)
class ModelInfo:
    """Backend model metadata normalized for ATHENA."""

    provider: str
    backend_model_id: str
    display_name: str
    model_type: str
    context_capacity: int | None
    quantization: str | None
    loaded: bool
    vision: bool | None
    trained_for_tool_use: bool | None
    loaded_context_length: int | None = None
    capabilities: ModelCapabilities = field(default_factory=ModelCapabilities)
    model_revision: str | None = None

    def __post_init__(self) -> None:
        _require_canonical_text(self.provider, "ModelInfo provider")
        _require_canonical_text(self.backend_model_id, "ModelInfo backend_model_id")
        _require_text(self.display_name, "ModelInfo display_name")
        _require_canonical_text(self.model_type, "ModelInfo model_type")
        _require_optional_positive_int(self.context_capacity, "ModelInfo context_capacity")
        if self.quantization is not None and not isinstance(self.quantization, str):
            raise TypeError("ModelInfo quantization must be text or None.")
        if not isinstance(self.loaded, bool):
            raise TypeError("ModelInfo loaded must be bool.")
        _require_optional_bool(self.vision, "ModelInfo vision")
        _require_optional_bool(self.trained_for_tool_use, "ModelInfo trained_for_tool_use")
        _require_optional_positive_int(
            self.loaded_context_length,
            "ModelInfo loaded_context_length",
        )
        if not isinstance(self.capabilities, ModelCapabilities):
            raise TypeError("ModelInfo capabilities must be a ModelCapabilities value.")
        _require_optional_canonical_text(
            self.model_revision,
            "ModelInfo model_revision",
        )
        if (
            self.context_capacity is not None
            and self.loaded_context_length is not None
            and self.loaded_context_length > self.context_capacity
        ):
            raise ValueError(
                "ModelInfo loaded_context_length must not exceed context_capacity."
            )

        normalized_capabilities = ModelCapabilities(
            chat=self.capabilities.chat,
            structured_output=self.capabilities.structured_output,
            tool_calls=_merge_observed_capability(
                declared=self.capabilities.tool_calls,
                observed=_support_from_optional_bool(self.trained_for_tool_use),
                label="tool_calls",
            ),
            vision=_merge_observed_capability(
                declared=self.capabilities.vision,
                observed=_support_from_optional_bool(self.vision),
                label="vision",
            ),
            audio=self.capabilities.audio,
            context_length=_merge_observed_capability(
                declared=self.capabilities.context_length,
                observed=(
                    ModelCapabilitySupport.SUPPORTED
                    if self.context_capacity is not None
                    else ModelCapabilitySupport.UNKNOWN
                ),
                label="context_length",
            ),
            streaming=self.capabilities.streaming,
            model_load_control=self.capabilities.model_load_control,
        )
        object.__setattr__(self, "capabilities", normalized_capabilities)


@dataclass(frozen=True, slots=True)
class ModelChatMessage:
    """One stateless chat-history item passed to a model provider."""

    role: str
    content: str

    def __post_init__(self) -> None:
        _require_text(self.role, "ModelChatMessage role")
        if self.role != self.role.strip() or self.role not in _MODEL_CHAT_ROLES:
            raise ValueError(
                "ModelChatMessage role must be one of: system, user, assistant."
            )
        if not isinstance(self.content, str):
            raise TypeError("ModelChatMessage content must be text.")
