"""Safe lexical degradation when semantic retrieval infrastructure is unavailable."""

from __future__ import annotations

from dataclasses import dataclass

from athena.model.adapters.lm_studio import ModelProviderError
from athena.model.adapters.lm_studio_embeddings import (
    LMStudioEmbeddingProvider,
)
from athena.model.domain import ModelInfo

HYBRID_RETRIEVAL_MODE = "hybrid"
LEXICAL_FALLBACK_RETRIEVAL_MODE = "lexical_fallback"

EMBEDDING_MODEL_UNAVAILABLE_WARNING = (
    "embedding_model_unavailable"
)
EMBEDDING_MODEL_NOT_LOADED_WARNING = (
    "embedding_model_not_loaded"
)


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{label} must not be empty.")
    return normalized


class SemanticRetrievalUnavailableError(
    RuntimeError
):
    """Raised only when semantic Derived State cannot be used."""

    def __init__(
        self,
        reason_code: str,
    ) -> None:
        normalized = _canonical_text(
            reason_code,
            "Semantic retrieval fallback reason code",
        )
        self.reason_code = normalized
        super().__init__(normalized)


@dataclass(
    frozen=True,
    slots=True,
)
class EmbeddingRetrievalResolution:
    """Resolved embedding infrastructure or explicit lexical fallback."""

    model: ModelInfo | None
    mode: str
    warning: str | None


def resolve_embedding_model_for_retrieval(
    provider: LMStudioEmbeddingProvider,
    requested_model_id: str | None,
) -> EmbeddingRetrievalResolution:
    """Resolve embeddings without making them a chat hard dependency."""

    if not isinstance(provider, LMStudioEmbeddingProvider):
        raise ValueError(
            "Embedding retrieval provider must be an LMStudioEmbeddingProvider value."
        )
    normalized_model_id = (
        None
        if requested_model_id is None
        else _canonical_text(requested_model_id, "Embedding model id")
    )

    try:
        model = provider.resolve_model(
            normalized_model_id
        )
    except ModelProviderError:
        return EmbeddingRetrievalResolution(
            model=None,
            mode=(
                LEXICAL_FALLBACK_RETRIEVAL_MODE
            ),
            warning=(
                EMBEDDING_MODEL_UNAVAILABLE_WARNING
            ),
        )

    if not model.loaded:
        return EmbeddingRetrievalResolution(
            model=None,
            mode=(
                LEXICAL_FALLBACK_RETRIEVAL_MODE
            ),
            warning=(
                EMBEDDING_MODEL_NOT_LOADED_WARNING
            ),
        )

    return EmbeddingRetrievalResolution(
        model=model,
        mode=HYBRID_RETRIEVAL_MODE,
        warning=None,
    )
