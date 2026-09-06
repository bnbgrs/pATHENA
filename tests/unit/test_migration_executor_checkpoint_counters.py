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

    class _Cursor:
        def __init__(self, row: tuple[Any, ...]) -> None:
            self._row = row

        def fetchone(self) -> tuple[Any, ...]:
            return self._row

    class _Connection:
        row_factory: object = None

        def execute(self, sql: str) -> _Cursor:
            if sql == "PRAGMA user_version":
                return _Cursor((SCHEMA_VERSION,))
            if sql == "PRAGMA wal_checkpoint(TRUNCATE)":
                return _Cursor(checkpoint)
            raise AssertionError(sql)

        def close(self) -> None:
            return

    monkeypatch.setattr(
        executor_module.sqlite3,
        "connect",
        lambda *args, **kwargs: _Connection(),
    )
    monkeypatch.setattr(
        executor_module,
        "initialize_schema",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(MigrationExecutorError, match=rf"{label} must not be negative"):
        migrate_schema_candidate(candidate, created_at_us=123)
