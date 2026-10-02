from __future__ import annotations

import uuid

import pytest

from athena.knowledge.claim_repository import ClaimRepository
from athena.memory.repository import PersonalMemoryRepository
from athena.source.analysis_repository import SourceAnalysisRepository
from athena.source.anchor_repository import SourceAnchorRepository


class _DatabaseMustNotBeTouched:
    @property
    def connection(self) -> object:
        raise AssertionError("invalid pagination input must fail before SQLite access")


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_memory_list_rejects_non_integer_limit_before_sqlite(limit: object) -> None:
    repository = PersonalMemoryRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_current(limit=limit)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_claim_list_rejects_non_integer_limit_before_sqlite(limit: object) -> None:
    repository = ClaimRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_current(limit=limit)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_analysis_list_rejects_non_integer_limit_before_sqlite(limit: object) -> None:
    repository = SourceAnalysisRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_analyses_for_source(
            uuid.uuid4(),
            limit=limit,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_anchor_list_rejects_non_integer_limit_before_sqlite(limit: object) -> None:
    repository = SourceAnchorRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_for_source(
            uuid.uuid4(),
            limit=limit,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("factory", "call", "message"),
    [
        (
            PersonalMemoryRepository,
            lambda repository: repository.list_current(limit=0),
            "between 1 and 500",
        ),
        (
            ClaimRepository,
            lambda repository: repository.list_current(limit=501),
            "between 1 and 500",
        ),
        (
            SourceAnalysisRepository,
            lambda repository: repository.list_analyses_for_source(
                uuid.uuid4(),
                limit=1001,
            ),
            "between 1 and 1000",
        ),
        (
            SourceAnchorRepository,
            lambda repository: repository.list_for_source(
                uuid.uuid4(),
                limit=5001,
            ),
            "between 1 and 5000",
        ),
    ],
)
def test_repository_pagination_preserves_integer_range_contracts(
    factory: object,
    call: object,
    message: str,
) -> None:
    repository = factory(_DatabaseMustNotBeTouched())  # type: ignore[operator]

    with pytest.raises(ValueError, match=message):
        call(repository)  # type: ignore[operator]
