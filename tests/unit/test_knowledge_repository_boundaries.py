import pytest

from athena.knowledge.repository import KnowledgeRepository
from athena.storage.database import SQLiteDatabase


@pytest.mark.parametrize("limit", [True, False, 1.0, "1", None])
def test_list_current_rejects_non_integer_limits_before_sqlite(tmp_path, limit) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = KnowledgeRepository(database)
    with pytest.raises(TypeError):
        repository.list_current(limit=limit)
    database.stop()


@pytest.mark.parametrize("limit", [0, -1, 501])
def test_list_current_rejects_out_of_range_integer_limits(tmp_path, limit: int) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = KnowledgeRepository(database)
    with pytest.raises(ValueError):
        repository.list_current(limit=limit)
    database.stop()


def test_list_current_accepts_valid_integer_limit(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = KnowledgeRepository(database)
    assert repository.list_current(limit=1) == ()
    database.stop()
