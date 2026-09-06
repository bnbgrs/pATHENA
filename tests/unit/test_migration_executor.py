from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

import athena.storage.migration_executor as executor_module
from athena.storage.migration_executor import (
    MigrationExecutorError,
    migrate_schema_candidate,
)
from athena.storage.schema import SCHEMA_VERSION


def test_candidate_executor_initializes_only_candidate_and_leaves_no_sidecars(
    tmp_path: Path,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    sqlite3.connect(candidate, autocommit=True).close()

    migrate_schema_candidate(candidate, created_at_us=123)

    connection = sqlite3.connect(candidate, autocommit=True)
    try:
        assert connection.execute("PRAGMA user_version").fetchone() == (SCHEMA_VERSION,)
        assert str(connection.execute("PRAGMA journal_mode").fetchone()[0]).casefold() == "delete"
    finally:
        connection.close()
    assert not candidate.with_name(f"{candidate.name}-wal").exists()
    assert not candidate.with_name(f"{candidate.name}-shm").exists()


def test_candidate_executor_rejects_invalid_created_at_before_sqlite_open(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    sqlite3.connect(candidate, autocommit=True).close()
    opened = False

    def fail_connect(*args: object, **kwargs: object) -> object:
        nonlocal opened
        opened = True
        raise AssertionError("sqlite must not open")

    monkeypatch.setattr(executor_module.sqlite3, "connect", fail_connect)

    with pytest.raises(ValueError, match="non-negative integer"):
        migrate_schema_candidate(candidate, created_at_us=True)  # type: ignore[arg-type]

    assert opened is False


def test_candidate_executor_rejects_reparse_parent_before_sqlite_open(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    parent = (tmp_path / "migration").absolute()
    parent.mkdir()
    candidate = parent / "candidate.db"
    sqlite3.connect(candidate, autocommit=True).close()
    original = executor_module.is_link_boundary
    opened = False

    def simulate_reparse(path: Path) -> bool:
        return path == parent or original(path)

    def fail_connect(*args: object, **kwargs: object) -> object:
        nonlocal opened
        opened = True
        raise AssertionError("sqlite must not open through reparse parent")

    monkeypatch.setattr(executor_module, "is_link_boundary", simulate_reparse)
    monkeypatch.setattr(executor_module.sqlite3, "connect", fail_connect)

    with pytest.raises(MigrationExecutorError, match="unsafe path ancestor"):
        migrate_schema_candidate(candidate, created_at_us=123)

    assert opened is False


def test_candidate_executor_reports_schema_failure_without_deleting_candidate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    sqlite3.connect(candidate, autocommit=True).close()

    def fail_initialize(_connection: sqlite3.Connection, *, created_at_us: int) -> None:
        assert created_at_us == 123
        raise sqlite3.OperationalError("simulated migration failure")

    monkeypatch.setattr(executor_module, "initialize_schema", fail_initialize)

    with pytest.raises(MigrationExecutorError, match="schema execution failed"):
        migrate_schema_candidate(candidate, created_at_us=123)

    assert candidate.is_file()


def test_candidate_executor_rejects_incomplete_wal_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")

    class _Cursor:
        def __init__(self, row: tuple[Any, ...]) -> None:
            self._row = row

        def fetchone(self) -> tuple[Any, ...]:
            return self._row

    class _Connection:
        def execute(self, sql: str) -> _Cursor:
            if sql == "PRAGMA user_version":
                return _Cursor((SCHEMA_VERSION,))
            if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
                return _Cursor((1, 1, 0))
            raise AssertionError(sql)

        def close(self) -> None:
            return

    fake = _Connection()
    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *a, **k: fake)
    monkeypatch.setattr(
        executor_module,
        "initialize_schema",
        lambda _connection, *, created_at_us: None,
    )

    with pytest.raises(MigrationExecutorError, match="checkpoint did not fully complete"):
        migrate_schema_candidate(candidate, created_at_us=123)


@pytest.mark.parametrize("invalid_user_version", [True, str(SCHEMA_VERSION), float(SCHEMA_VERSION)])
def test_candidate_executor_rejects_coercible_user_version_runtime_types(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    invalid_user_version: object,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")

    class _Cursor:
        def fetchone(self) -> tuple[object]:
            return (invalid_user_version,)

    class _Connection:
        row_factory: object = None

        def execute(self, sql: str) -> _Cursor:
            assert sql == "PRAGMA user_version"
            return _Cursor()

        def close(self) -> None:
            return

    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *a, **k: _Connection())
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *a, **k: None)

    with pytest.raises(MigrationExecutorError, match="user_version must be an integer"):
        migrate_schema_candidate(candidate, created_at_us=123)


@pytest.mark.parametrize("invalid_checkpoint_value", [True, "0", 0.0])
def test_candidate_executor_rejects_coercible_checkpoint_runtime_types(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    invalid_checkpoint_value: object,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")

    class _Cursor:
        def __init__(self, row: tuple[object, ...]) -> None:
            self._row = row

        def fetchone(self) -> tuple[object, ...]:
            return self._row

    class _Connection:
        row_factory: object = None

        def execute(self, sql: str) -> _Cursor:
            if sql == "PRAGMA user_version":
                return _Cursor((SCHEMA_VERSION,))
            if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
                return _Cursor((invalid_checkpoint_value, 0, 0))
            raise AssertionError(sql)

        def close(self) -> None:
            return

    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *a, **k: _Connection())
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *a, **k: None)

    with pytest.raises(MigrationExecutorError, match="checkpoint busy must be an integer"):
        migrate_schema_candidate(candidate, created_at_us=123)


@pytest.mark.parametrize("invalid_journal_mode", [True, 0, 0.0, b"delete"])
def test_candidate_executor_rejects_nontext_journal_mode_runtime_types(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    invalid_journal_mode: object,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")

    class _Cursor:
        def __init__(self, row: tuple[object, ...]) -> None:
            self._row = row

        def fetchone(self) -> tuple[object, ...]:
            return self._row

    class _Connection:
        row_factory: object = None

        def execute(self, sql: str) -> _Cursor:
            if sql == "PRAGMA user_version":
                return _Cursor((SCHEMA_VERSION,))
            if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
                return _Cursor((0, 0, 0))
            if sql == "PRAGMA journal_mode = DELETE":
                return _Cursor((invalid_journal_mode,))
            raise AssertionError(sql)

        def close(self) -> None:
            return

    monkeypatch.setattr(executor_module.sqlite3, "connect", lambda *a, **k: _Connection())
    monkeypatch.setattr(executor_module, "initialize_schema", lambda *a, **k: None)

    with pytest.raises(MigrationExecutorError, match="journal_mode must be a text"):
        migrate_schema_candidate(candidate, created_at_us=123)
