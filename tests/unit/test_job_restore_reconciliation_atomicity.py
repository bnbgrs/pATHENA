from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.jobs.recovery import reconcile_jobs_after_restore


@dataclass
class _Cursor:
    rowcount: object


class _Connection:
    def __init__(self, rowcounts: tuple[object, object]) -> None:
        self.in_transaction = False
        self.rowcounts = iter(rowcounts)
        self.statements: list[str] = []

    def execute(self, sql: str, parameters: object = ()) -> _Cursor:
        del parameters
        statement = " ".join(sql.split())
        self.statements.append(statement)
        if statement == "BEGIN IMMEDIATE":
            self.in_transaction = True
            return _Cursor(0)
        if statement == "COMMIT":
            self.in_transaction = False
            return _Cursor(0)
        if statement == "ROLLBACK":
            self.in_transaction = False
            return _Cursor(0)
        if statement.startswith("UPDATE jobs"):
            return _Cursor(next(self.rowcounts))
        raise AssertionError(f"Unexpected SQL: {statement}")


def test_invalid_rowcount_rolls_back_before_commit() -> None:
    connection = _Connection((-1, 0))

    with pytest.raises(RuntimeError, match="invalid SQLite row count"):
        reconcile_jobs_after_restore(connection, now_us=1)  # type: ignore[arg-type]

    assert "COMMIT" not in connection.statements
    assert connection.statements[-1] == "ROLLBACK"
    assert connection.in_transaction is False


def test_valid_rowcounts_commit_and_return_summary() -> None:
    connection = _Connection((2, 1))

    summary = reconcile_jobs_after_restore(connection, now_us=1)  # type: ignore[arg-type]

    assert summary.paused_running == 2
    assert summary.cancelled_requested == 1
    assert summary.total == 3
    assert connection.statements[-1] == "COMMIT"
    assert "ROLLBACK" not in connection.statements
    assert connection.in_transaction is False
