from __future__ import annotations

import uuid

import pytest

from athena.source.repository import SourceRepository


class _DatabaseMustNotBeTouched:
    @property
    def connection(self) -> object:
        raise AssertionError("invalid list limit must fail before SQLite access")


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_source_list_rejects_non_integer_limits_before_sqlite(limit: object) -> None:
    repository = SourceRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list(limit=limit)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_protected_source_list_rejects_non_integer_limits_before_sqlite(
    limit: object,
) -> None:
    repository = SourceRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_protected_in_scopes(
            frozenset({uuid.uuid4()}),
            limit=limit,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("limit", [0, -1, 501])
def test_source_list_preserves_integer_range_validation(limit: int) -> None:
    repository = SourceRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="between 1 and 500"):
        repository.list(limit=limit)


@pytest.mark.parametrize("limit", [0, -1, 10002])
def test_protected_source_list_preserves_integer_range_validation(limit: int) -> None:
    repository = SourceRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="between 1 and 10001"):
        repository.list_protected_in_scopes(
            frozenset({uuid.uuid4()}),
            limit=limit,
        )


def test_empty_protected_scope_still_validates_limit_contract() -> None:
    repository = SourceRepository(_DatabaseMustNotBeTouched())  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="must be an integer"):
        repository.list_protected_in_scopes(
            frozenset(),
            limit=True,
        )
