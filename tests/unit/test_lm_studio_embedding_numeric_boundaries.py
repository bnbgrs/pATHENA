from __future__ import annotations

import pytest

from athena.model.adapters.lm_studio import ProviderProtocolError
from athena.model.adapters.lm_studio_embeddings import (
    LMStudioEmbeddingProvider,
    _positive_finite_timeout,
)


def test_embedding_timeout_rejects_huge_integer_as_value_error() -> None:
    with pytest.raises(ValueError, match="finite number"):
        _positive_finite_timeout(10**400)


def test_embedding_vector_rejects_huge_integer_as_protocol_error() -> None:
    with pytest.raises(ProviderProtocolError, match="non-finite"):
        LMStudioEmbeddingProvider._parse_vector([10**400])
