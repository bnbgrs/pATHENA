"""Stable model-provider domain types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProviderHealthStatus(str, Enum):
    """Normalized provider health states used by the Core."""

    UNAVAILABLE = "unavailable"
    READY = "ready"
    DEGRADED = "degraded"
    ERROR = "error"


def _require_text(value: object, label: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{label} must not be empty.")


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

    def __post_init__(self) -> None:
        _require_text(self.provider, "ModelInfo provider")
        _require_text(self.backend_model_id, "ModelInfo backend_model_id")
        _require_text(self.display_name, "ModelInfo display_name")
        _require_text(self.model_type, "ModelInfo model_type")
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
        if (
            self.context_capacity is not None
            and self.loaded_context_length is not None
            and self.loaded_context_length > self.context_capacity
        ):
            raise ValueError(
                "ModelInfo loaded_context_length must not exceed context_capacity."
            )


@dataclass(frozen=True, slots=True)
class ModelChatMessage:
    """One stateless chat-history item passed to a model provider."""

    role: str
    content: str

    def __post_init__(self) -> None:
        _require_text(self.role, "ModelChatMessage role")
        if not isinstance(self.content, str):
            raise TypeError("ModelChatMessage content must be text.")
