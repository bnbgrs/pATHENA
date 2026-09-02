from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from athena.storage.database import SQLiteDatabase


class _CommitFailingConnection(sqlite3.Connection):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.statements: list[str] = []

    def execute(
        self,
        statement: str,
        parameters: Any = (),
        /,
    ) -> sqlite3.Cursor:
        self.statements.append(statement)
        if statement == "COMMIT":
            raise RuntimeError("simulated commit failure")
        return super().execute(statement, parameters)


def test_write_transaction_rolls_back_when_commit_fails() -> None:
    database = SQLiteDatabase(Path("/tmp/unused.db"))
    connection = _CommitFailingConnection(":memory:", isolation_level=None)
    database._connection = connection

    try:
        with pytest.raises(RuntimeError, match="simulated commit failure"):
            with database.write_transaction() as active:
                assert active is connection
                assert connection.in_transaction is True

        assert connection.statements == ["BEGIN IMMEDIATE", "COMMIT", "ROLLBACK"]
        assert connection.in_transaction is False
    finally:
        connection.close()
