from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import pytest

import athena.source.archive_replication as archive_replication
from athena.source.archive_replication import (
    ArchiveReplicationRepository,
    ArchiveReplicationService,
)


class _ForbiddenDatabase:
    @property
    def connection(self) -> object:
        raise AssertionError("invalid input must fail before database access")

    @contextmanager
    def write_transaction(self) -> Iterator[object]:
        raise AssertionError("invalid input must fail before transaction start")
        yield object()


def _repository() -> ArchiveReplicationRepository:
    repository = ArchiveReplicationRepository.__new__(ArchiveReplicationRepository)
    repository.database = _ForbiddenDatabase()  # type: ignore[assignment]
    return repository


@pytest.mark.parametrize("limit", [True, False, 1.5, "10", None])
def test_list_pending_rejects_non_integer_limit_before_database(limit: object) -> None:
    repository = _repository()

    with pytest.raises(TypeError, match="limit must be an integer"):
        repository.list_pending(limit=limit)  # type: ignore[arg-type]


@pytest.mark.parametrize("limit", [0, -1, 1001])
def test_list_verified_rejects_out_of_range_limit_before_database(limit: int) -> None:
    repository = _repository()

    with pytest.raises(ValueError, match="between 1 and 1000"):
        repository.list_verified(limit=limit)


@pytest.mark.parametrize("sequence", [True, False, 1.5, "1", None])
def test_get_rejects_non_integer_outbox_sequence_before_database(sequence: object) -> None:
    repository = _repository()

    with pytest.raises(TypeError, match="outbox_seq must be an integer"):
        repository.get(sequence)  # type: ignore[arg-type]


@pytest.mark.parametrize("sequence", [0, -1])
def test_get_rejects_nonpositive_outbox_sequence_before_database(sequence: int) -> None:
    repository = _repository()

    with pytest.raises(ValueError, match="outbox_seq must be >= 1"):
        repository.get(sequence)


@pytest.mark.parametrize("timestamp", [True, False, 1.5, "1"])
def test_mark_attempt_rejects_non_integer_timestamp_before_transaction(timestamp: object) -> None:
    repository = _repository()

    with pytest.raises(TypeError, match="timestamp must be an integer"):
        repository.mark_attempt(1, now_us=timestamp)  # type: ignore[arg-type]


def test_confirm_verified_rejects_negative_timestamp_before_transaction() -> None:
    repository = _repository()

    with pytest.raises(ValueError, match="timestamp must be >= 0"):
        repository.confirm_verified(1, now_us=-1)


@pytest.mark.parametrize("error_code", [True, 1, 1.5, None])
def test_record_failure_rejects_non_text_error_code_before_transaction(
    error_code: object,
) -> None:
    repository = _repository()

    with pytest.raises(TypeError, match="error_code must be text"):
        repository.record_failure(
            1,
            error_code=error_code,  # type: ignore[arg-type]
            error_detail="detail",
        )


def test_record_failure_rejects_blank_error_code_before_transaction() -> None:
    repository = _repository()

    with pytest.raises(ValueError, match="error_code must not be empty"):
        repository.record_failure(1, error_code="   ", error_detail="detail")


def test_record_failure_rejects_non_text_error_detail_before_transaction() -> None:
    repository = _repository()

    with pytest.raises(TypeError, match="error_detail must be text"):
        repository.record_failure(
            1,
            error_code="Failure",
            error_detail=123,  # type: ignore[arg-type]
        )


def test_sync_pending_validates_limit_before_runtime_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository()
    service = ArchiveReplicationService.__new__(ArchiveReplicationService)
    service.repository = repository
    service.runtime_lock_root = None
    service.blob_store = object()  # type: ignore[assignment]

    def forbidden_lock(*args: object, **kwargs: object) -> object:
        raise AssertionError("invalid limit must fail before runtime lock")

    monkeypatch.setattr(archive_replication, "runtime_data_lock", forbidden_lock)

    with pytest.raises(TypeError, match="limit must be an integer"):
        service.sync_pending(limit=True)


def test_cleanup_validates_limit_before_runtime_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository()
    service = ArchiveReplicationService.__new__(ArchiveReplicationService)
    service.repository = repository
    service.runtime_lock_root = None
    service.blob_store = object()  # type: ignore[assignment]

    def forbidden_lock(*args: object, **kwargs: object) -> object:
        raise AssertionError("invalid limit must fail before runtime lock")

    monkeypatch.setattr(archive_replication, "runtime_data_lock", forbidden_lock)

    with pytest.raises(ValueError, match="between 1 and 1000"):
        service.cleanup_verified_spool_duplicates(limit=1001)
