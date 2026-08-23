from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.retrieval.ranking import RetrievalRankingService


@dataclass
class _SearchStub:
    database: object
    calls: int = 0

    def search(self, *args: object, **kwargs: object) -> tuple[()]:
        self.calls += 1
        return ()


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "20", None, 201])
def test_ranking_rejects_invalid_limit_before_search(value: object) -> None:
    search = _SearchStub(database=object())
    service = RetrievalRankingService(search)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="integer between 1 and 200"):
        service.search("query", limit=value)  # type: ignore[arg-type]

    assert search.calls == 0


@pytest.mark.parametrize("value", [1, 20, 200])
def test_ranking_accepts_integer_limit_boundaries(value: int) -> None:
    search = _SearchStub(database=object())
    service = RetrievalRankingService(search)  # type: ignore[arg-type]

    assert service.search("query", limit=value) == ()
    assert search.calls == 1
