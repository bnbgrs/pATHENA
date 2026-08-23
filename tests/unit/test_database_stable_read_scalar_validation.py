from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest

from athena.storage.database import DatabaseNotStartedError, SQLiteDatabase


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("1", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_stable_read_rejects_invalid_attempt_count_before_database_access(
    value: object,
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")

    with pytest.raises(ValueError, match="max_attempts"):
        database.stable_read(
            lambda connection: connection,
            max_attempts=cast(Any, value),
        )


def test_stable_read_valid_attempt_count_reaches_database_boundary(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")

    with pytest.raises(DatabaseNotStartedError):
        database.stable_read(
            lambda connection: connection,
            max_attempts=1,
        )
