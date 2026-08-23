"""Ephemeral execution guard for model calls using Protected Source context.

This module deliberately carries protected plaintext only in memory. Durable
metadata emitted here contains stable identifiers and counts, never protected
plaintext, rendered context, document hashes, or quoted-text hashes.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from athena.retrieval.protected_source import ProtectedRuntimeContextBundle


class ProtectedRuntimeBundleVerifier(Protocol):
    """Minimal authorization/integrity contract required at execution time."""

    def verify_bundle(self, bundle: ProtectedRuntimeContextBundle) -> None:
        ...


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
