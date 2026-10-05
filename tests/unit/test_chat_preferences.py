from __future__ import annotations

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.storage.database import SQLiteDatabase
from athena.storage.schema import CHAT_PREFERENCES_SCHEMA_VERSION


def test_chat_preferences_persist_without_mutating_chat_history(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        service = ChatService(ChatRepository(database))
        first = service.create_chat()
        second = service.create_chat()

        assert service.get_chat_preferences(first).pinned is False
        assert service.get_chat_preferences(first).favorited is False

        pinned = service.set_chat_preferences(
            chat_id=first,
            pinned=True,
        )
        favorite = service.set_chat_preferences(
            chat_id=second,
            favorited=True,
        )

        assert pinned.pinned is True
        assert pinned.favorited is False
        assert favorite.pinned is False
        assert favorite.favorited is True

        summaries = service.list_chats()
        assert tuple(item.chat_id for item in summaries[:2]) == (first, second)
        assert summaries[0].pinned is True
        assert summaries[0].favorited is False
        assert summaries[1].pinned is False
        assert summaries[1].favorited is True

        first_thread = service.load_chat(first)
        assert first_thread.messages == ()

        cleared = service.set_chat_preferences(
            chat_id=first,
            pinned=False,
        )
        assert cleared.pinned is False
        assert cleared.favorited is False
        assert database.connection.execute(
            "SELECT 1 FROM chat_preferences WHERE chat_id = ?",
            (first.bytes,),
        ).fetchone() is None
    finally:
        database.stop()


def test_fresh_database_installs_chat_preferences_schema_v43(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        connection = database.connection
        assert connection.execute("PRAGMA user_version").fetchone()[0] == (
            CHAT_PREFERENCES_SCHEMA_VERSION
        )
        columns = tuple(
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(chat_preferences)"
            ).fetchall()
        )
        assert columns == (
            "chat_id",
            "pinned_at_us",
            "favorited_at_us",
            "updated_at_us",
        )
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        database.stop()
