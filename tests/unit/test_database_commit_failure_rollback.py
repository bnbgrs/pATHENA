from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from athena.storage.database import SQLiteDatabase


class _CommitFailingConnection:
    def __init__(self) -> None:
        self.in_transaction = False
        self.statements: list[str] = []

    def execute(self, statement: str, *args: Any, **kwargs: Any) -> object:
        del args, kwargs
        self.statements.append(statement)
        if statement == "BEGIN IMMEDIATE":
            self.in_transaction = True
            return object()
        if statement == "COMMIT":
            raise RuntimeError("simulated commit failure")
        if statement == "ROLLBACK":
            self.in_transaction = False
            return object()
        return object()


def test_write_transaction_rolls_back_when_commit_fails() -> None:
    database = SQLiteDatabase(Path("/tmp/unused.db"))
    connection = _CommitFailingConnection()
    database._connection = connection  # type: ignore[assignment]

    with pytest.raises(RuntimeError, match="simulated commit failure"):
        with database.write_transaction() as active:
            assert active is connection
            assert connection.in_transaction is True

    assert connection.statements == ["BEGIN IMMEDIATE", "COMMIT", "ROLLBACK"]
    assert connection.in_transaction is False
