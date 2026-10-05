from __future__ import annotations

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.storage.database import SQLiteDatabase
from athena.storage.schema import SCHEMA_VERSION
from athena.storage.schema_contract import CHAT_PREFERENCES_SCHEMA_VERSION


def _service(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    return database, ChatService(ChatRepository(database))


def test_chat_pin_is_durable_and_orders_favorites_first(tmp_path) -> None:
    database, service = _service(tmp_path)
    older_chat = service.create_chat()
    newer_chat = service.create_chat()

    service.set_chat_pinned(chat_id=older_chat, pinned=True)

    summaries = service.list_chats()
    assert summaries[0].chat_id == older_chat
    assert summaries[0].pinned is True
    assert next(item for item in summaries if item.chat_id == newer_chat).pinned is False
    assert database.connection.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION
    assert SCHEMA_VERSION == CHAT_PREFERENCES_SCHEMA_VERSION
    database.stop()

    reopened = SQLiteDatabase(tmp_path / "athena.db")
    reopened.start()
    reopened_service = ChatService(ChatRepository(reopened))
    restored = reopened_service.list_chats()
    assert restored[0].chat_id == older_chat
    assert restored[0].pinned is True

    reopened_service.set_chat_pinned(chat_id=older_chat, pinned=False)
    updated = reopened_service.list_chats()
    assert all(not item.pinned for item in updated)
    reopened.stop()
