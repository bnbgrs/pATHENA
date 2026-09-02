from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.jobs.recovery import RestoredJobRecoverySummary, reconcile_jobs_after_restore


@dataclass
class _Cursor:
    rowcount: int = 0


class _RollbackFailureConnection:
    in_transaction = False

    def __init__(self) -> None:
        self.commands: list[str] = []

    def execute(self, sql: str, parameters: object = ()) -> _Cursor:
        command = sql.strip().split(maxsplit=1)[0].upper()
        self.commands.append(command)
        if command == "BEGIN":
            return _Cursor()
        if command == "UPDATE":
            raise RuntimeError("primary recovery failure")
        if command == "ROLLBACK":
            raise OSError("secondary rollback failure")
        return _Cursor()


@pytest.mark.parametrize("value", [True, False, 1.5, "1", None])
def test_recovery_summary_rejects_non_integer_paused_count(value: object) -> None:
    with pytest.raises(TypeError, match="paused_running must be an integer"):
        RestoredJobRecoverySummary(
            paused_running=value,  # type: ignore[arg-type]
            cancelled_requested=0,
        )


@pytest.mark.parametrize("field", ["paused_running", "cancelled_requested"])
def test_recovery_summary_rejects_negative_counts(field: str) -> None:
    values = {"paused_running": 0, "cancelled_requested": 0}
    values[field] = -1
    with pytest.raises(ValueError, match="must not be negative"):
        RestoredJobRecoverySummary(**values)


def test_recovery_summary_total_is_exact_sum() -> None:
    summary = RestoredJobRecoverySummary(paused_running=2, cancelled_requested=3)
    assert summary.total == 5


def test_recovery_preserves_primary_failure_when_rollback_also_fails() -> None:
    connection = _RollbackFailureConnection()

    with pytest.raises(RuntimeError, match="primary recovery failure"):
        reconcile_jobs_after_restore(
            connection,  # type: ignore[arg-type]
            now_us=10,
        )

    assert connection.commands == ["BEGIN", "UPDATE", "ROLLBACK"]
