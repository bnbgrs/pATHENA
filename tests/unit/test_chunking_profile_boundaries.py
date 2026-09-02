from __future__ import annotations

from typing import cast

import pytest

from athena.source.chunking_repository import ChunkingProfileRepository
from athena.storage.database import SQLiteDatabase


def _repository_without_database_access() -> ChunkingProfileRepository:
    return ChunkingProfileRepository(cast(SQLiteDatabase, object()))


@pytest.mark.parametrize(
    ("target_size", "overlap_size"),
    [
        (1, 1),
        (100, 100),
        (100, 101),
        (1200, 5000),
    ],
)
def test_chunking_profile_rejects_overlap_not_smaller_than_target(
    target_size: int,
    overlap_size: int,
) -> None:
    repository = _repository_without_database_access()

    with pytest.raises(
        ValueError,
        match="overlap_size must be smaller than target_size",
    ):
        repository.get_or_create(
            algorithm="paragraph_char_v1",
            tokenizer=None,
            target_size=target_size,
            overlap_size=overlap_size,
            structure_rules={"preserve_exact_text_slices": True},
            profile_version=1,
        )


@pytest.mark.parametrize(
    ("target_size", "overlap_size"),
    [
        (True, 0),
        (100, False),
        (1.5, 0),
        (100, 1.5),
    ],
)
def test_chunking_profile_rejects_non_integer_size_boundaries(
    target_size: object,
    overlap_size: object,
) -> None:
    repository = _repository_without_database_access()

    with pytest.raises(ValueError, match="must be an integer"):
        repository.get_or_create(
            algorithm="paragraph_char_v1",
            tokenizer=None,
            target_size=target_size,  # type: ignore[arg-type]
            overlap_size=overlap_size,  # type: ignore[arg-type]
            structure_rules={"preserve_exact_text_slices": True},
            profile_version=1,
        )
