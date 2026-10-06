from __future__ import annotations

from pathlib import Path

import pytest

from athena.chat.repository import ChatNotFoundError
from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.lifecycle.trash import LifecycleTrashStateError


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=root)
    )
    app.start()
    return app


def test_chat_trash_is_reversible_and_does_not_write_deletion_ledger(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-trash")
    try:
        chat_id = app.chat.create_chat()
        message = app.chat.add_user_message(
            chat_id=chat_id,
            content="durable trash payload",
        )

        trashed = app.lifecycle_trash.trash_chat(chat_id)

        assert trashed.entity_id == chat_id
        assert trashed.lifecycle_state == "trashed"
        assert set(trashed.affected_entity_ids) == {
            chat_id,
            message.message_id,
        }
        assert all(
            item.chat_id != chat_id
            for item in app.chat.list_chats()
        )
        trash_items = app.lifecycle_trash.list_trashed_chats()
        assert [item.chat_id for item in trash_items] == [chat_id]
        assert trash_items[0].lifecycle_state == "trashed"
        assert trash_items[0].message_count == 1

        with pytest.raises(ChatNotFoundError):
            app.chat.load_chat(chat_id)
        with pytest.raises(ChatNotFoundError):
            app.chat.add_user_message(
                chat_id=chat_id,
                content="must stay blocked while trashed",
            )

        rows = app.database.connection.execute(
            """
            SELECT entity_id, lifecycle_state
            FROM entity_registry
            WHERE entity_id IN (?, ?)
            ORDER BY entity_id
            """,
            (chat_id.bytes, message.message_id.bytes),
        ).fetchall()
        assert len(rows) == 2
        assert {str(row["lifecycle_state"]) for row in rows} == {"trashed"}

        assert (
            app.database.connection.execute(
                """
                SELECT COUNT(*)
                FROM deletion_ledger
                WHERE entity_id IN (?, ?)
                """,
                (chat_id.bytes, message.message_id.bytes),
            ).fetchone()[0]
            == 0
        )

        audit = app.database.connection.execute(
            """
            SELECT operation_type
            FROM commit_records
            WHERE commit_id = ?
            """,
            (trashed.commit_id.bytes,),
        ).fetchone()
        assert audit is not None
        assert audit["operation_type"] == "lifecycle.trash.chat"

        restored = app.lifecycle_trash.restore_chat(chat_id)
        assert restored.entity_id == chat_id
        assert restored.lifecycle_state == "active"
        assert set(restored.affected_entity_ids) == {
            chat_id,
            message.message_id,
        }

        thread = app.chat.load_chat(chat_id)
        assert thread.chat_id == chat_id
        assert [item.message_id for item in thread.messages] == [message.message_id]
        assert thread.messages[0].revision_id == message.revision_id
        assert thread.messages[0].content == "durable trash payload"
        assert app.lifecycle_trash.list_trashed_chats() == ()

        open_history = app.database.connection.execute(
            """
            SELECT lifecycle_state
            FROM entity_state_history
            WHERE entity_id = ?
              AND valid_to_commit_seq IS NULL
            """,
            (chat_id.bytes,),
        ).fetchall()
        assert len(open_history) == 1
        assert open_history[0]["lifecycle_state"] == "active"
    finally:
        app.stop()


def test_trashed_chat_can_be_permanently_deleted_but_not_restored(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-trash-delete")
    try:
        chat_id = app.chat.create_chat()
        message = app.chat.add_user_message(
            chat_id=chat_id,
            content="delete after trash",
        )
        app.lifecycle_trash.trash_chat(chat_id)

        preview = app.lifecycle_deletion.preview(chat_id)
        assert preview.lifecycle_state == "trashed"
        result = app.lifecycle_deletion.delete(
            chat_id,
            preview_digest=preview.preview_digest,
        )
        assert set(result.deleted_entity_ids) == {
            chat_id,
            message.message_id,
        }

        ledger = app.database.connection.execute(
            """
            SELECT entity_id, entity_type
            FROM deletion_ledger
            WHERE entity_id IN (?, ?)
            """,
            (chat_id.bytes, message.message_id.bytes),
        ).fetchall()
        assert {bytes(row["entity_id"]) for row in ledger} == {
            chat_id.bytes,
            message.message_id.bytes,
        }

        with pytest.raises(LifecycleTrashStateError):
            app.lifecycle_trash.restore_chat(chat_id)
    finally:
        app.stop()


def test_chat_trash_restore_delete_cycle_keeps_single_open_history_row(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-trash-cycle")
    try:
        chat_id = app.chat.create_chat()
        app.chat.add_user_message(chat_id=chat_id, content="cycle")

        for _ in range(3):
            app.lifecycle_trash.trash_chat(chat_id)
            app.lifecycle_trash.restore_chat(chat_id)

        rows = app.database.connection.execute(
            """
            SELECT lifecycle_state, valid_to_commit_seq
            FROM entity_state_history
            WHERE entity_id = ?
            ORDER BY valid_from_commit_seq
            """,
            (chat_id.bytes,),
        ).fetchall()
        assert sum(row["valid_to_commit_seq"] is None for row in rows) == 1
        assert rows[-1]["lifecycle_state"] == "active"

        preview = app.lifecycle_deletion.preview(chat_id)
        app.lifecycle_deletion.delete(
            chat_id,
            preview_digest=preview.preview_digest,
        )

        final = app.database.connection.execute(
            """
            SELECT lifecycle_state
            FROM entity_registry
            WHERE entity_id = ?
            """,
            (chat_id.bytes,),
        ).fetchone()
        assert final is not None
        assert final["lifecycle_state"] == "deleted"
    finally:
        app.stop()
