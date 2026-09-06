from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import athena.storage.migration_executor as executor_module
from athena.storage.migration_executor import MigrationExecutorError, migrate_schema_candidate
from athena.storage.schema import SCHEMA_VERSION


class _Cursor:
    def __init__(self, row: tuple[Any, ...]) -> None:
        self._row = row

    def fetchone(self) -> tuple[Any, ...]:
        return self._row


class _Connection:
    row_factory: object = None

    def __init__(self, user_version: tuple[Any, ...]) -> None:
        self._user_version = user_version
        self.checkpoint_attempted = False

    def execute(self, sql: str) -> _Cursor:
        if sql == "PRAGMA user_version":
            return _Cursor(self._user_version)
        if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
            self.checkpoint_attempted = True
            return _Cursor((0, 0, 0))
        if sql == "PRAGMA journal_mode = DELETE":
            return _Cursor(("delete",))
        raise AssertionError(sql)

    def close(self) -> None:
        return


@pytest.mark.parametrize("user_version", [(), (SCHEMA_VERSION, 0)])
def test_candidate_executor_requires_exact_user_version_status_shape_before_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    user_version: tuple[Any, ...],
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")
    fake = _Connection(user_version)
    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *args, **kwargs: fake)
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *args, **kwargs: None)

    with pytest.raises(MigrationExecutorError, match="user_version returned invalid status"):
        migrate_schema_candidate(candidate, created_at_us=123)

    assert fake.checkpoint_attempted is False


def test_candidate_executor_accepts_canonical_single_field_user_version_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")
    fake = _Connection((SCHEMA_VERSION,))
    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *args, **kwargs: fake)
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *args, **kwargs: None)

    migrate_schema_candidate(candidate, created_at_us=123)

    assert fake.checkpoint_attempted is True
