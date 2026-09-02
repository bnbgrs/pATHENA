from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pytest

from athena.source.chunking_repository import (
    ChunkingProfileRepository,
    _canonical_json,
)


@dataclass
class _NoWriteDatabase:
    calls: int = 0

    def write_transaction(self) -> object:
        self.calls += 1
        raise AssertionError("invalid chunking configuration reached database")


def _repository() -> tuple[ChunkingProfileRepository, _NoWriteDatabase]:
    database = _NoWriteDatabase()
    repository = ChunkingProfileRepository(database)  # type: ignore[arg-type]
    return repository, database


@pytest.mark.parametrize(
    "overrides",
    [
        {"algorithm": None},
        {"algorithm": 1},
        {"algorithm": ""},
        {"target_size": True},
        {"target_size": 1.5},
        {"target_size": 0},
        {"overlap_size": False},
        {"overlap_size": 1.5},
        {"overlap_size": -1},
        {"profile_version": True},
        {"profile_version": 1.0},
        {"profile_version": 0},
        {"tokenizer": True},
        {"tokenizer": "   "},
        {"structure_rules": []},
        {"structure_rules": {1: "value"}},
        {"structure_rules": {"value": ("tuple",)}},
        {"structure_rules": {"value": {"set"}}},
        {"structure_rules": {"value": b"bytes"}},
        {"structure_rules": {"value": math.nan}},
        {"structure_rules": {"value": math.inf}},
    ],
)
def test_invalid_chunking_profile_fails_before_database(
    overrides: dict[str, Any],
) -> None:
    repository, database = _repository()
    values: dict[str, Any] = {
        "algorithm": "paragraph_char_v1",
        "tokenizer": None,
        "target_size": 1200,
        "overlap_size": 0,
        "structure_rules": {
            "boundary_priority": ["paragraph", "hard_limit"],
            "preserve_exact_text_slices": True,
        },
        "profile_version": 1,
    }
    values.update(overrides)

    with pytest.raises(ValueError):
        repository.get_or_create(**values)

    assert database.calls == 0


@pytest.mark.parametrize(
    "value",
    [
        {"nested": ("tuple",)},
        {"nested": {"set"}},
        {"nested": bytearray(b"bytes")},
        {"nested": object()},
        {"nested": math.nan},
        {"nested": math.inf},
        {1: "non-string-key"},
    ],
)
def test_chunking_canonical_json_rejects_python_only_values(value: object) -> None:
    with pytest.raises(ValueError):
        _canonical_json(value)


def test_chunking_canonical_json_is_stable_for_valid_object() -> None:
    assert _canonical_json({"b": [2, 1], "a": True}) == (
        '{"a":true,"b":[2,1]}'
    )
