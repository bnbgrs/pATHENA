"""Fail-closed comparison between a pinned model signature and runtime model facts."""

from __future__ import annotations

from typing import Protocol

from athena.model.domain import ModelInfo


class ModelSignatureDriftError(ValueError):
    """Raised when runtime model facts no longer satisfy a pinned signature."""


class PinnedModelSignature(Protocol):
    @property
    def provider(self) -> str: ...

    @property
    def model_identifier(self) -> str: ...

    @property
    def model_revision(self) -> str | None: ...

    @property
    def quantization(self) -> str | None: ...


def assert_runtime_model_matches_signature(
    *,
    model: ModelInfo,
    signature: PinnedModelSignature,
) -> None:
    """Reject identity or known-revision drift before provider execution.

    Unknown pinned revisions remain unknown rather than being inferred later.
    Once a revision was known and pinned, however, runtime discovery must report
    that exact same revision; a changed or newly unavailable revision fails
    closed because execution can no longer be tied to the recorded signature.
    """
    if not isinstance(model, ModelInfo):
        raise TypeError("Runtime model must be a ModelInfo.")

    if (
        model.provider != signature.provider
        or model.backend_model_id != signature.model_identifier
        or model.quantization != signature.quantization
    ):
        raise ModelSignatureDriftError(
            "Runtime model identity drifted from the pinned ModelSignature."
        )

    pinned_revision = signature.model_revision
    if pinned_revision is not None and model.model_revision != pinned_revision:
        raise ModelSignatureDriftError(
            "Runtime model revision drifted from the pinned ModelSignature."
        )
