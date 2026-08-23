from __future__ import annotations

import uuid
from typing import cast

import pytest

from athena.chat.service import ChatService
from athena.source.anchor_repository import SourceAnchorRepository
from athena.source.anchor_service import SourceAnchorService
from athena.source.chunk_store import SourceChunkStore
from athena.source.chunking_service import SourceChunkingService
from athena.source.representation_service import SourceTextRepresentationService


def _service_without_dependency_access() -> SourceAnchorService:
    unavailable = object()
    return SourceAnchorService(
        repository=cast(SourceAnchorRepository, unavailable),
        source_text=cast(SourceTextRepresentationService, unavailable),
        source_chunks=cast(SourceChunkingService, unavailable),
        chunk_store=cast(SourceChunkStore, unavailable),
        chat=cast(ChatService, unavailable),
    )


@pytest.mark.parametrize("start_offset", [True, False, 1.5, "0", None])
def test_materialize_text_range_rejects_non_integer_start_offset(
    start_offset: object,
) -> None:
    service = _service_without_dependency_access()

    with pytest.raises(TypeError, match="start_offset must be an integer"):
        service.materialize_text_range(
            uuid.uuid4(),
            start_offset=start_offset,  # type: ignore[arg-type]
            end_offset=2,
        )


@pytest.mark.parametrize("end_offset", [True, False, 2.5, "2", None])
def test_materialize_text_range_rejects_non_integer_end_offset(
    end_offset: object,
) -> None:
    service = _service_without_dependency_access()

    with pytest.raises(TypeError, match="end_offset must be an integer"):
        service.materialize_text_range(
            uuid.uuid4(),
            start_offset=0,
            end_offset=end_offset,  # type: ignore[arg-type]
        )


def test_materialize_text_range_rejects_negative_start_before_dependency_access() -> None:
    service = _service_without_dependency_access()

    with pytest.raises(ValueError, match="start_offset must not be negative"):
        service.materialize_text_range(
            uuid.uuid4(),
            start_offset=-1,
            end_offset=2,
        )


@pytest.mark.parametrize(("start_offset", "end_offset"), [(0, 0), (2, 2), (3, 2)])
def test_materialize_text_range_rejects_empty_or_reversed_range(
    start_offset: int,
    end_offset: int,
) -> None:
    service = _service_without_dependency_access()

    with pytest.raises(ValueError, match="start_offset < end_offset"):
        service.materialize_text_range(
            uuid.uuid4(),
            start_offset=start_offset,
            end_offset=end_offset,
        )
