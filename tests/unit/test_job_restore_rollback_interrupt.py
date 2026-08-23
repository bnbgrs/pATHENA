from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.jobs.recovery import reconcile_jobs_after_restore


@dataclass
class _Cursor:
    rowcount: object


class _Connection:
    def __init__(self) -> None:
        self.in_transaction = False
        self.statements: list[str] = []

    def execute(self, sql: str, parameters: object = ()) -> object:
        normalized = sql.strip().split()[0].upper()
        self.statements.append(normalized)
        if normalized == "BEGIN":
            self.in_transaction = True
            return _Cursor(0)
        if normalized == "UPDATE":
            return _Cursor(None)
        if normalized == "ROLLBACK":
            self.in_transaction = False
            raise KeyboardInterrupt("rollback interrupted")
        if normalized == "COMMIT":
            self.in_transaction = False
            return _Cursor(0)
        raise AssertionError(sql)


def test_restore_reconciliation_preserves_primary_failure_when_rollback_interrupts() -> None:
    connection = _Connection()

    with pytest.raises(RuntimeError, match="invalid SQLite row count"):
        reconcile_jobs_after_restore(connection, now_us=1)  # type: ignore[arg-type]

    assert connection.statements == ["BEGIN", "UPDATE", "UPDATE", "ROLLBACK"]
