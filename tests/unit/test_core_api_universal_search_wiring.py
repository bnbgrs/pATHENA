from __future__ import annotations

import uuid

import pytest

from athena.api.service import CoreApiFacade
from athena.retrieval.universal import (
    UniversalSearchEntityType,
    UniversalSearchResult,
)


class _FakeUniversalSearch:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                str,
                int,
                tuple[UniversalSearchEntityType, ...] | None,
            ]
        ] = []

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[UniversalSearchResult, ...]:
        self.calls.append((query, limit, entity_types))
        return (
            UniversalSearchResult(
                result_ref="source:11111111-1111-1111-1111-111111111111",
                entity_id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                revision_id=None,
                entity_type=UniversalSearchEntityType.SOURCE,
                title="Alpha design.pdf",
                preview="file · application/pdf",
                rank=1,
            ),
        )


def _facade() -> CoreApiFacade:
    return CoreApiFacade(
        health=object(),  # type: ignore[arg-type]
        chat=object(),  # type: ignore[arg-type]
        model_provider=object(),  # type: ignore[arg-type]
    )


def test_universal_search_capability_tracks_attachment() -> None:
    facade = _facade()

    assert "search.universal.local" not in facade.capabilities().features

    facade.attach_universal_search(_FakeUniversalSearch())

    assert "search.universal.local" in facade.capabilities().features


def test_universal_search_attachment_is_one_time() -> None:
    facade = _facade()
    first = _FakeUniversalSearch()
    facade.attach_universal_search(first)

    with pytest.raises(RuntimeError, match="already attached"):
        facade.attach_universal_search(_FakeUniversalSearch())

    assert facade._universal_search is first


def test_universal_search_delegates_filters_and_preserves_missing_revision() -> None:
    facade = _facade()
    search = _FakeUniversalSearch()
    facade.attach_universal_search(search)

    response = facade.universal_search(
        "alpha",
        limit=7,
        entity_types=(UniversalSearchEntityType.SOURCE,),
    )

    assert search.calls == [
        (
            "alpha",
            7,
            (UniversalSearchEntityType.SOURCE,),
        )
    ]
    assert len(response) == 1
    item = response[0]
    assert item.result_ref == "source:11111111-1111-1111-1111-111111111111"
    assert item.entity_type == "source"
    assert item.revision_id is None
    assert item.rank == 1
    assert item.retrieval_methods == ("lexical",)
    assert item.protection.state == "unprotected"
