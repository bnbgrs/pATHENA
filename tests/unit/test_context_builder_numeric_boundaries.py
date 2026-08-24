from __future__ import annotations

import pytest

from athena.retrieval.context import (
    ContextBuilderError,
    ContextBuilderService,
    estimate_tokens,
)


@pytest.mark.parametrize("value", [True, False, 0, 127, 64_001, 128.5, "1200", None])
def test_context_builder_rejects_invalid_token_budget(value: object) -> None:
    service = ContextBuilderService()

    with pytest.raises(ContextBuilderError):
        service.build_from_hybrid(
            query="query",
            results=(),
            max_estimated_tokens=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [True, False, 0, -1, 101, 1.5, "8", None])
def test_context_builder_rejects_invalid_max_items(value: object) -> None:
    service = ContextBuilderService()

    with pytest.raises(ContextBuilderError):
        service.build_from_hybrid(
            query="query",
            results=(),
            max_items=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [True, False, -1, 101, 1.5, "8", None])
def test_context_builder_rejects_invalid_max_memory_items(value: object) -> None:
    service = ContextBuilderService()

    with pytest.raises(ContextBuilderError):
        service.build_from_hybrid(
            query="query",
            results=(),
            max_memory_items=value,  # type: ignore[arg-type]
        )


def test_context_builder_accepts_zero_memory_limit() -> None:
    service = ContextBuilderService()

    bundle = service.build_from_hybrid(
        query="query",
        results=(),
        max_estimated_tokens=128,
        max_items=1,
        max_memory_items=0,
    )

    assert bundle.max_estimated_tokens == 128
    assert bundle.memory_items == ()


def test_context_builder_rejects_non_text_query() -> None:
    service = ContextBuilderService()

    with pytest.raises(ContextBuilderError, match="query must be text"):
        service.build_from_hybrid(
            query=123,  # type: ignore[arg-type]
            results=(),
        )


def test_estimate_tokens_rejects_non_text_input() -> None:
    with pytest.raises(TypeError, match="requires text"):
        estimate_tokens(123)  # type: ignore[arg-type]
