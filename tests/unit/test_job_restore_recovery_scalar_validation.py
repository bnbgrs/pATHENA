from __future__ import annotations

import sqlite3
from typing import Any

import pytest

from athena.jobs.recovery import reconcile_jobs_after_restore


@pytest.mark.parametrize(
    "now_us",
    [
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
        pytest.param(1.5, id="float"),
        pytest.param("1", id="text"),
        pytest.param(None, id="none"),
        pytest.param(-1, id="negative"),
    ],
)
def test_restore_reconciliation_rejects_invalid_timestamp_before_sql(
    now_us: Any,
) -> None:
    connection = sqlite3.connect(":memory:")
    try:
        with pytest.raises(ValueError, match="non-negative integer"):
            reconcile_jobs_after_restore(connection, now_us=now_us)
        assert connection.in_transaction is False
    finally:
        connection.close()


def test_restore_reconciliation_rejects_foreign_transaction_before_mutation() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("BEGIN")
        with pytest.raises(RuntimeError, match="transaction ownership"):
            reconcile_jobs_after_restore(connection, now_us=0)
        assert connection.in_transaction is True
    finally:
        connection.rollback()
        connection.close()
