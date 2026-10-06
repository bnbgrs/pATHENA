from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from athena.chat.repository import ChatNotFoundError
from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.knowledge.models import (
    KnowledgeKind,
    KnowledgeUnitDraft,
)
from athena.knowledge.repository import (
    KnowledgeNotFoundError,
)
from athena.lifecycle.service import (
    LifecycleDeletionPreviewStaleError,
)
from athena.source.repository import (
    SourceNotFoundError,
)


def _app(
    root: Path,
) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=root,
        )
    )

    app.start()

    return app


def test_knowledge_delete_requires_preview_and_hides_normal_reads(
    tmp_path: Path,
) -> None:
    app = _app(
        tmp_path
        / "runtime-knowledge"
    )

    try:
        actor_id = (
            app.chat.ensure_local_user()
        )

        knowledge = (
            app.knowledge_repository.create_knowledge_unit(
                actor_id=actor_id,
                draft=KnowledgeUnitDraft(
                    knowledge_kind=KnowledgeKind.FACT,
                    body=(
                        "15d payload must not appear "
                        "in deletion ledger metadata"
                    ),
                ),
                reason="15d test knowledge",
            )
        )

        preview = (
            app.lifecycle_deletion.preview(
                knowledge.knowledge_id
            )
        )

        assert (
            preview.entity_type
            == "knowledge_unit"
        )

        assert (
            len(
                preview.preview_digest
            )
            == 64
        )

        result = (
            app.lifecycle_deletion.delete(
                knowledge.knowledge_id,
                preview_digest=(
                    preview.preview_digest
                ),
            )
        )

        assert result.deleted_entity_ids == (
            knowledge.knowledge_id,
        )

        with pytest.raises(
            KnowledgeNotFoundError
        ):
            app.knowledge_repository.load_current(
                knowledge.knowledge_id
            )

        assert all(
            item.knowledge_id
            != knowledge.knowledge_id
            for item
            in app.knowledge_repository.list_current()
        )

        row = app.database.connection.execute(
            """
            SELECT lifecycle_state
            FROM entity_registry
            WHERE entity_id = ?
            """,
            (
                knowledge.knowledge_id.bytes,
            ),
        ).fetchone()

        assert row is not None
        assert (
            row[
                "lifecycle_state"
            ]
            == "deleted"
        )

        ledger = app.database.connection.execute(
            """
            SELECT
                entity_type,
                COUNT(*) AS count
            FROM deletion_ledger
            WHERE entity_id = ?
            GROUP BY entity_type
            """,
            (
                knowledge.knowledge_id.bytes,
            ),
        ).fetchone()

        assert ledger is not None
        assert (
            ledger[
                "entity_type"
            ]
            == "knowledge_unit"
        )
        assert int(
            ledger[
                "count"
            ]
        ) == 1

    finally:
        app.stop()


def test_source_preview_surfaces_blob_and_delete_does_not_delete_blob(
    tmp_path: Path,
) -> None:
    app = _app(
        tmp_path
        / "runtime-source"
    )

    source_file = (
        tmp_path
        / "source.txt"
    )

    source_file.write_text(
        "source content retained until physical purge",
        encoding="utf-8",
    )

    try:
        captured = (
            app.sources.capture_file(
                source_file
            )
        )

        source_id = (
            captured.source.source_id
        )

        blob_id = (
            captured.blob.blob_id
        )

        preview = (
            app.lifecycle_deletion.preview(
                source_id
            )
        )

        assert any(
            dependency.relation
            == "source.blob_reference"
            and dependency.dependent_entity_id
            == blob_id
            for dependency
            in preview.dependencies
        )

        app.lifecycle_deletion.delete(
            source_id,
            preview_digest=(
                preview.preview_digest
            ),
        )

        with pytest.raises(
            SourceNotFoundError
        ):
            app.sources.get(
                source_id
            )

        blob_row = app.database.connection.execute(
            """
            SELECT lifecycle_state
            FROM entity_registry
            WHERE entity_id = ?
            """,
            (
                blob_id.bytes,
            ),
        ).fetchone()

        assert blob_row is not None

        assert (
            blob_row[
                "lifecycle_state"
            ]
            != "deleted"
        )

    finally:
        app.stop()


def test_chat_preview_owns_messages_and_delete_hides_whole_chat(
    tmp_path: Path,
) -> None:
    app = _app(
        tmp_path
        / "runtime-chat"
    )

    try:
        chat_id = (
            app.chat.create_chat()
        )

        first = (
            app.chat.add_user_message(
                chat_id=chat_id,
                content="first",
            )
        )

        second = (
            app.chat.add_user_message(
                chat_id=chat_id,
                content="second",
            )
        )

        preview = (
            app.lifecycle_deletion.preview(
                chat_id
            )
        )

        owned = {
            dependency.dependent_entity_id
            for dependency
            in preview.dependencies
            if dependency.relation
            == "chat.owned_message"
        }

        assert owned == {
            first.message_id,
            second.message_id,
        }

        result = (
            app.lifecycle_deletion.delete(
                chat_id,
                preview_digest=(
                    preview.preview_digest
                ),
            )
        )

        assert set(
            result.deleted_entity_ids
        ) == {
            chat_id,
            first.message_id,
            second.message_id,
        }

        with pytest.raises(
            ChatNotFoundError
        ):
            app.chat.load_chat(
                chat_id
            )

        assert all(
            summary.chat_id
            != chat_id
            for summary
            in app.chat.list_chats()
        )

        rows = app.database.connection.execute(
            """
            SELECT
                entity_id,
                lifecycle_state
            FROM entity_registry
            WHERE entity_id IN (?, ?, ?)
            """,
            (
                chat_id.bytes,
                first.message_id.bytes,
                second.message_id.bytes,
            ),
        ).fetchall()

        assert len(
            rows
        ) == 3

        assert {
            str(
                row[
                    "lifecycle_state"
                ]
            )
            for row in rows
        } == {
            "deleted"
        }

    finally:
        app.stop()


def test_dependency_change_invalidates_old_preview(
    tmp_path: Path,
) -> None:
    app = _app(
        tmp_path
        / "runtime-stale"
    )

    try:
        chat_id = (
            app.chat.create_chat()
        )

        preview = (
            app.lifecycle_deletion.preview(
                chat_id
            )
        )

        app.chat.add_user_message(
            chat_id=chat_id,
            content=(
                "dependency created after preview"
            ),
        )

        with pytest.raises(
            LifecycleDeletionPreviewStaleError
        ):
            app.lifecycle_deletion.delete(
                chat_id,
                preview_digest=(
                    preview.preview_digest
                ),
            )

        loaded = (
            app.chat.load_chat(
                chat_id
            )
        )

        assert (
            loaded.lifecycle_state
            == "active"
        )

    finally:
        app.stop()


def test_old_snapshot_restore_reapplies_knowledge_deletion(
    tmp_path: Path,
) -> None:
    runtime = (
        tmp_path
        / "runtime-restore"
    )

    target = (
        tmp_path
        / "backup"
    )

    destination = (
        tmp_path
        / "restored"
    )

    app = _app(
        runtime
    )

    try:
        actor_id = (
            app.chat.ensure_local_user()
        )

        knowledge = (
            app.knowledge_repository.create_knowledge_unit(
                actor_id=actor_id,
                draft=KnowledgeUnitDraft(
                    knowledge_kind=KnowledgeKind.FACT,
                    body=(
                        "must remain deleted after old restore"
                    ),
                ),
                reason="15d restore test",
            )
        )

        snapshot = (
            app.backup.create_snapshot(
                target_root=target
            )
        )

        preview = (
            app.lifecycle_deletion.preview(
                knowledge.knowledge_id
            )
        )

        app.lifecycle_deletion.delete(
            knowledge.knowledge_id,
            preview_digest=(
                preview.preview_digest
            ),
        )

        app.backup.restore_to(
            snapshot.snapshot_id,
            destination_root=destination,
        )

    finally:
        app.stop()

    restored = sqlite3.connect(
        destination
        / "state"
        / "athena.db"
    )

    restored.row_factory = (
        sqlite3.Row
    )

    try:
        row = restored.execute(
            """
            SELECT lifecycle_state
            FROM entity_registry
            WHERE entity_id = ?
            """,
            (
                knowledge.knowledge_id.bytes,
            ),
        ).fetchone()

        assert row is not None

        assert (
            row[
                "lifecycle_state"
            ]
            == "deleted"
        )

        ledger = restored.execute(
            """
            SELECT entity_type
            FROM deletion_ledger
            WHERE entity_id = ?
            """,
            (
                knowledge.knowledge_id.bytes,
            ),
        ).fetchone()

        assert ledger is not None

        assert (
            ledger[
                "entity_type"
            ]
            == "knowledge_unit"
        )

        assert (
            restored.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()
            == []
        )

    finally:
        restored.close()


def test_chat_trash_is_reversible_and_does_not_write_deletion_ledger(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-chat-trash")
    try:
        chat_id = app.chat.create_chat()
        first = app.chat.add_user_message(chat_id=chat_id, content="first")
        second = app.chat.add_user_message(chat_id=chat_id, content="second")

        trashed = app.lifecycle_deletion.trash_chat(chat_id)

        assert trashed.entity_id == chat_id
        assert trashed.lifecycle_state == "trashed"
        assert set(trashed.affected_entity_ids) == {
            chat_id,
            first.message_id,
            second.message_id,
        }
        with pytest.raises(ChatNotFoundError):
            app.chat.load_chat(chat_id)
        assert all(item.chat_id != chat_id for item in app.chat.list_chats())
        trash = app.chat.list_trashed_chats()
        assert [item.chat_id for item in trash] == [chat_id]
        assert trash[0].lifecycle_state == "trashed"

        ledger_count = app.database.connection.execute(
            "SELECT COUNT(*) FROM deletion_ledger WHERE entity_id IN (?, ?, ?)",
            (chat_id.bytes, first.message_id.bytes, second.message_id.bytes),
        ).fetchone()[0]
        assert int(ledger_count) == 0

        operations = {
            str(row["operation"])
            for row in app.database.connection.execute(
                """
                SELECT operation
                FROM provenance_records
                WHERE subject_entity_id = ?
                """,
                (chat_id.bytes,),
            ).fetchall()
        }
        assert "chat.trash" in operations
    finally:
        app.stop()


def test_chat_restore_reopens_exact_entities_and_retains_lifecycle_audit(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-chat-restore-action")
    try:
        chat_id = app.chat.create_chat()
        message = app.chat.add_user_message(chat_id=chat_id, content="restore me")
        app.lifecycle_deletion.trash_chat(chat_id)

        restored = app.lifecycle_deletion.restore_chat(chat_id)

        assert restored.entity_id == chat_id
        assert restored.lifecycle_state == "active"
        assert set(restored.affected_entity_ids) == {chat_id, message.message_id}
        loaded = app.chat.load_chat(chat_id)
        assert loaded.chat_id == chat_id
        assert loaded.messages[0].content == "restore me"
        assert [item.chat_id for item in app.chat.list_trashed_chats()] == []

        history = [
            str(row["lifecycle_state"])
            for row in app.database.connection.execute(
                """
                SELECT lifecycle_state
                FROM entity_state_history
                WHERE entity_id = ?
                ORDER BY valid_from_commit_seq
                """,
                (chat_id.bytes,),
            ).fetchall()
        ]
        assert history[-3:] == ["active", "trashed", "active"]

        operations = {
            str(row["operation"])
            for row in app.database.connection.execute(
                """
                SELECT operation
                FROM provenance_records
                WHERE subject_entity_id = ?
                """,
                (chat_id.bytes,),
            ).fetchall()
        }
        assert {"chat.trash", "chat.restore"}.issubset(operations)

        ledger_count = app.database.connection.execute(
            "SELECT COUNT(*) FROM deletion_ledger WHERE entity_id = ?",
            (chat_id.bytes,),
        ).fetchone()[0]
        assert int(ledger_count) == 0
    finally:
        app.stop()


def test_trashed_chat_can_still_be_permanently_deleted_with_existing_ledger_path(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-chat-trash-delete")
    try:
        chat_id = app.chat.create_chat()
        message = app.chat.add_user_message(chat_id=chat_id, content="purge later")
        app.lifecycle_deletion.trash_chat(chat_id)

        preview = app.lifecycle_deletion.preview(chat_id)
        result = app.lifecycle_deletion.delete(
            chat_id,
            preview_digest=preview.preview_digest,
        )

        assert set(result.deleted_entity_ids) == {chat_id, message.message_id}
        assert app.chat.list_trashed_chats() == ()
        ledger_count = app.database.connection.execute(
            "SELECT COUNT(*) FROM deletion_ledger WHERE entity_id IN (?, ?)",
            (chat_id.bytes, message.message_id.bytes),
        ).fetchone()[0]
        assert int(ledger_count) == 2
    finally:
        app.stop()
