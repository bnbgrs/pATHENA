"""Ephemeral execution guard for model calls using Protected Source context.

This module deliberately carries protected plaintext only in memory. Durable
metadata emitted here contains stable identifiers and counts, never protected
plaintext, rendered context, document hashes, or quoted-text hashes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from athena.retrieval.protected_source import (
    ProtectedRuntimeContextBundle,
    ProtectedRuntimeContextItem,
)


class ProtectedRuntimeBundleVerifier(Protocol):
    """Minimal authorization/integrity contract required at execution time."""

    def verify_bundle(self, bundle: ProtectedRuntimeContextBundle) -> None:
        ...


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


def _validate_bundle_shape(bundle: ProtectedRuntimeContextBundle) -> None:
    if not isinstance(bundle.query, str) or not bundle.query.strip():
        raise ValueError("Protected execution query must be non-empty text.")
    if bundle.mode != "protected_runtime_lexical":
        raise ValueError("Protected execution mode is unsupported.")
    if not isinstance(bundle.items, tuple) or not all(
        isinstance(item, ProtectedRuntimeContextItem) for item in bundle.items
    ):
        raise TypeError(
            "Protected execution items must be a tuple of ProtectedRuntimeContextItem values."
        )
    _nonnegative_int(
        bundle.omitted_count,
        "Protected execution omitted_count",
    )
    estimated = _nonnegative_int(
        bundle.estimated_tokens,
        "Protected execution estimated_tokens",
    )
    maximum = _nonnegative_int(
        bundle.max_estimated_tokens,
        "Protected execution max_estimated_tokens",
    )
    if maximum < 1:
        raise ValueError("Protected execution max_estimated_tokens must be positive.")
    if estimated > maximum:
        raise ValueError(
            "Protected execution estimated_tokens must not exceed its token budget."
        )
    if not isinstance(bundle.rendered_text, str) or not bundle.rendered_text:
        raise ValueError("Protected execution rendered context must be non-empty text.")


@dataclass(frozen=True, slots=True)
class ProtectedRuntimeExecutionGuard:
    """Keep protected model context ephemeral and re-verify it before execution.

    Construction verifies the bundle once. Callers must invoke
    ``before_provider_call`` immediately before each provider attempt; this is
    intentionally compatible with chat-generation pre-call callbacks and catches
    a ProtectionScope relock or protected-byte change after context assembly.
    """

    verifier: ProtectedRuntimeBundleVerifier
    bundle: ProtectedRuntimeContextBundle

    def __post_init__(self) -> None:
        verify_bundle = getattr(self.verifier, "verify_bundle", None)
        if not callable(verify_bundle):
            raise TypeError(
                "Protected execution verifier must expose verify_bundle()."
            )
        if not isinstance(self.bundle, ProtectedRuntimeContextBundle):
            raise TypeError(
                "Protected execution bundle must be a ProtectedRuntimeContextBundle."
            )
        _validate_bundle_shape(self.bundle)
        verify_bundle(self.bundle)

    @property
    def rendered_text(self) -> str:
        """Return protected plaintext for request-local model input only."""
        return self.bundle.rendered_text

    @property
    def before_provider_call(self) -> Callable[[], None]:
        """Return the required immediate pre-provider authorization check."""
        return self.verify_now

    def verify_now(self) -> None:
        """Re-verify current unlock state and protected-byte integrity."""
        _validate_bundle_shape(self.bundle)
        self.verifier.verify_bundle(self.bundle)

    def durable_metadata(self) -> Mapping[str, object]:
        """Return persistence-safe metadata with no protected plaintext hashes."""
        source_ids = tuple(
            sorted({str(item.source_id) for item in self.bundle.items})
        )
        protection_scope_ids = tuple(
            sorted({str(item.protection_scope_id) for item in self.bundle.items})
        )
        context_ids = tuple(item.context_id for item in self.bundle.items)
        return {
            "protected_runtime_context": True,
            "mode": self.bundle.mode,
            "item_count": len(self.bundle.items),
            "omitted_count": self.bundle.omitted_count,
            "estimated_tokens": self.bundle.estimated_tokens,
            "max_estimated_tokens": self.bundle.max_estimated_tokens,
            "source_ids": source_ids,
            "protection_scope_ids": protection_scope_ids,
            "context_ids": context_ids,
        }


def protected_execution_guard(
    *,
    verifier: ProtectedRuntimeBundleVerifier,
    bundle: ProtectedRuntimeContextBundle,
) -> ProtectedRuntimeExecutionGuard:
    """Construct a verified request-local Protected Source execution guard."""
    return ProtectedRuntimeExecutionGuard(verifier=verifier, bundle=bundle)
