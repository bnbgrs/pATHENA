from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication


def test_core_api_exposes_reversible_chat_trash_contract(tmp_path: Path) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path / "runtime")
    )
    app.start()
    try:
        thread = app.api.create_chat()
        chat_id = thread.chat_id

        features = app.api.capabilities().features
        assert "chat.trash" in features
        assert "chat.restore" in features
        assert "chat.trash.list" in features

        trashed = app.api.trash_chat(chat_id)
        assert trashed.entity_id == chat_id
        assert trashed.entity_type == "chat"
        assert trashed.lifecycle_state == "trashed"
        assert chat_id in trashed.affected_entity_ids

        assert all(item.chat_id != chat_id for item in app.api.list_chats())
        trash = app.api.list_trashed_chats()
        assert [item.chat_id for item in trash] == [chat_id]
        assert trash[0].lifecycle_state == "trashed"

        restored = app.api.restore_chat(chat_id)
        assert restored.entity_id == chat_id
        assert restored.lifecycle_state == "active"
        assert all(item.chat_id != chat_id for item in app.api.list_trashed_chats())
        assert any(item.chat_id == chat_id for item in app.api.list_chats())
    finally:
        app.stop()
