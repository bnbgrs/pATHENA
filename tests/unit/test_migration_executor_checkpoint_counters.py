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

    def __init__(self, checkpoint: tuple[Any, ...]) -> None:
        self._checkpoint = checkpoint
        self.journal_mode_attempted = False

    def execute(self, sql: str) -> _Cursor:
        if sql == "PRAGMA user_version":
            return _Cursor((SCHEMA_VERSION,))
        if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
            return _Cursor(self._checkpoint)
        if sql == "PRAGMA journal_mode = DELETE":
            self.journal_mode_attempted = True
            return _Cursor(("delete",))
        raise AssertionError(sql)

    def close(self) -> None:
        return


@pytest.mark.parametrize(
    ("checkpoint", "label"),
    [
        ((0, -1, -1), "log_frames"),
        ((0, 0, -1), "checkpointed_frames"),
    ],
)
def test_candidate_executor_rejects_negative_checkpoint_frame_counters(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    checkpoint: tuple[int, int, int],
    label: str,
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")
    fake = _Connection(checkpoint)

    monkeypatch.setattr(
        executor_module.sqlite3,
        "connect",
        lambda *args, **kwargs: fake,
    )
    monkeypatch.setattr(
        executor_module,
        "initialize_schema",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(MigrationExecutorError, match=rf"{label} must not be negative"):
        migrate_schema_candidate(candidate, created_at_us=123)

    assert fake.journal_mode_attempted is False


@pytest.mark.parametrize(
    "checkpoint",
    [
        (),
        (0,),
        (0, 0),
        (0, 0, 0, 0),
    ],
)
def test_candidate_executor_requires_exact_checkpoint_status_shape_before_journal_mode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    checkpoint: tuple[int, ...],
) -> None:
    candidate = (tmp_path / "candidate.db").absolute()
    candidate.write_bytes(b"placeholder")
    fake = _Connection(checkpoint)

    monkeypatch.setattr(
        executor_module.sqlite3,
        "connect",
        lambda *args, **kwargs: fake,
    )
    monkeypatch.setattr(
        executor_module,
        "initialize_schema",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(MigrationExecutorError, match="checkpoint returned invalid status"):
        migrate_schema_candidate(candidate, created_at_us=123)

    assert fake.journal_mode_attempted is False
