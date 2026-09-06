from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import athena.storage.migration_executor as executor_module
from athena.storage.migration_executor import (
    MigrationExecutorError,
    migrate_schema_candidate,
)
from athena.storage.schema import SCHEMA_VERSION


class _Cursor:
    def __init__(self, row: tuple[Any, ...]) -> None:
        self._row = row

    def fetchone(self) -> tuple[Any, ...]:
        return self._row


class _Connection:
    row_factory: object = None

    def __init__(self, journal_mode: tuple[Any, ...]) -> None:
        self._journal_mode = journal_mode

    def execute(self, sql: str) -> _Cursor:
        if sql == "PRAGMA user_version":
            return _Cursor((SCHEMA_VERSION,))
        if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
            return _Cursor((0, 0, 0))
        if sql == "PRAGMA journal_mode = DELETE":
            return _Cursor(self._journal_mode)
        raise AssertionError(sql)

    def close(self) -> None:
        return


def _prepare_candidate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    journal_mode: tuple[Any, ...],
) -> Path:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")
    fake = _Connection(journal_mode)
    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *args, **kwargs: fake)
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *args, **kwargs: None)
    return candidate


@pytest.mark.parametrize("journal_mode", [(), ("delete", "unexpected")])
def test_candidate_executor_requires_exact_journal_mode_status_shape(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    journal_mode: tuple[Any, ...],
) -> None:
    candidate = _prepare_candidate(monkeypatch, tmp_path, journal_mode)

    with pytest.raises(MigrationExecutorError, match="journal_mode returned invalid status"):
        migrate_schema_candidate(candidate, created_at_us=123)


def test_candidate_executor_accepts_canonical_single_field_delete_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    candidate = _prepare_candidate(monkeypatch, tmp_path, ("delete",))

    migrate_schema_candidate(candidate, created_at_us=123)
