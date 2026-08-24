"""Provider-independent model failure taxonomy and retry semantics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProviderFailureKind(str, Enum):
    """Stable Core-facing classes for provider/backend generation failures."""

    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"
    BACKEND_CRASH = "backend_crash"
    REFUSAL = "refusal"
    CONTEXT_LIMIT = "context_limit"
    OUTPUT_LIMIT = "output_limit"
    UNKNOWN = "unknown"


class ProviderFailureRetryClass(str, Enum):
    """Whether automatic retry can be considered without changing the request."""

    RETRYABLE = "retryable"
    TERMINAL = "terminal"
    REQUEST_CHANGE_REQUIRED = "request_change_required"
    UNKNOWN = "unknown"


_RETRY_CLASS_BY_KIND = {
    ProviderFailureKind.TIMEOUT: ProviderFailureRetryClass.RETRYABLE,
    ProviderFailureKind.RESOURCE_EXHAUSTED: (
        ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED
    ),
    ProviderFailureKind.UNAVAILABLE: ProviderFailureRetryClass.RETRYABLE,
    ProviderFailureKind.INVALID_RESPONSE: ProviderFailureRetryClass.TERMINAL,
    ProviderFailureKind.BACKEND_CRASH: ProviderFailureRetryClass.RETRYABLE,
    ProviderFailureKind.REFUSAL: ProviderFailureRetryClass.TERMINAL,
    ProviderFailureKind.CONTEXT_LIMIT: ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED,
    ProviderFailureKind.OUTPUT_LIMIT: ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED,
    ProviderFailureKind.UNKNOWN: ProviderFailureRetryClass.UNKNOWN,
}


def _canonical_code(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    if normalized != value:
        raise ValueError(f"{label} must use canonical trimmed text.")
    if len(normalized) > 128:
        raise ValueError(f"{label} must not exceed 128 characters.")
    if not all(
        character.isascii()
        and (character.isalnum() or character in {"_", ".", "-"})
        for character in normalized
    ):
        raise ValueError(
            f"{label} must contain only ASCII letters, digits, underscore, dot or hyphen."
        )
    return normalized


@dataclass(frozen=True, slots=True)
class ProviderFailure:
    """Sanitized Core-facing description of one provider failure.

    Human-readable backend exception text deliberately does not belong here.
    Durable callers may persist ``code`` and ``kind`` without leaking arbitrary
    provider response bodies, paths, prompts, or transport diagnostics.
    """

    kind: ProviderFailureKind
    code: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ProviderFailureKind):
            raise TypeError("ProviderFailure kind must be a ProviderFailureKind.")
        _canonical_code(self.code, "ProviderFailure code")

    @property
    def retry_class(self) -> ProviderFailureRetryClass:
        return _RETRY_CLASS_BY_KIND[self.kind]

    @property
    def retryable(self) -> bool:
        return self.retry_class is ProviderFailureRetryClass.RETRYABLE

    @property
    def request_change_required(self) -> bool:
        return self.retry_class is ProviderFailureRetryClass.REQUEST_CHANGE_REQUIRED

    @property
    def terminal(self) -> bool:
        return self.retry_class is ProviderFailureRetryClass.TERMINAL

    def durable_code(self) -> str:
        """Return a compact stable machine code suitable for durable error fields."""
        return f"provider.{self.kind.value}.{self.code}"
