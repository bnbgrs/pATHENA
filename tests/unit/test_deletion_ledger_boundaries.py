from __future__ import annotations

import uuid

import pytest

from athena.lifecycle.deletion import (
    read_deletion_records,
    record_deletion,
)


class _NoSqlConnection:
    def execute(self, *_args: object, **_kwargs: object) -> object:
        raise AssertionError("malformed deletion input reached SQL")


@pytest.mark.parametrize("entity_type", [None, 1, False, object()])
def test_record_deletion_rejects_non_string_entity_type_before_sql(
    entity_type: object,
) -> None:
    with pytest.raises(ValueError):
        record_deletion(
            _NoSqlConnection(),  # type: ignore[arg-type]
            entity_id=uuid.uuid4(),
            entity_type=entity_type,  # type: ignore[arg-type]
            deleted_at_us=0,
            deletion_commit_seq=1,
            deleted_by_actor_id=uuid.uuid4(),
        )


@pytest.mark.parametrize("deleted_at_us", [False, True, 1.5, "1", None])
def test_record_deletion_rejects_non_integer_timestamp_before_sql(
    deleted_at_us: object,
) -> None:
    with pytest.raises(ValueError):
        record_deletion(
            _NoSqlConnection(),  # type: ignore[arg-type]
            entity_id=uuid.uuid4(),
            entity_type="source",
            deleted_at_us=deleted_at_us,  # type: ignore[arg-type]
            deletion_commit_seq=1,
            deleted_by_actor_id=uuid.uuid4(),
        )


@pytest.mark.parametrize(
    "deletion_commit_seq",
    [False, True, 0, -1, 1.5, "1", None],
)
def test_record_deletion_rejects_invalid_commit_sequence_before_sql(
    deletion_commit_seq: object,
) -> None:
    with pytest.raises(ValueError):
        record_deletion(
            _NoSqlConnection(),  # type: ignore[arg-type]
            entity_id=uuid.uuid4(),
            entity_type="source",
            deleted_at_us=0,
            deletion_commit_seq=deletion_commit_seq,  # type: ignore[arg-type]
            deleted_by_actor_id=uuid.uuid4(),
        )


@pytest.mark.parametrize("after_seq", [False, True, -1, 1.5, "1", None])
def test_read_deletion_records_rejects_invalid_cursor_before_sql(
    after_seq: object,
) -> None:
    with pytest.raises(ValueError):
        read_deletion_records(
            _NoSqlConnection(),  # type: ignore[arg-type]
            after_seq=after_seq,  # type: ignore[arg-type]
        )
