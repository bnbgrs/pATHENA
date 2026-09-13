import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.knowledge.models import KnowledgeKind, KnowledgeUnitDraft
from athena.knowledge.orphan_knowledge import create_orphan_user_knowledge
from athena.knowledge.repository import KnowledgeRepository
from athena.storage.database import SQLiteDatabase


def test_direct_user_knowledge_allows_no_source_and_keeps_provenance(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()

    try:
        chat = ChatService(ChatRepository(database))
        repository = KnowledgeRepository(database)
        actor_id = chat.ensure_local_user()

        created = create_orphan_user_knowledge(
            repository=repository,
            actor_id=actor_id,
            draft=KnowledgeUnitDraft(
                knowledge_kind=KnowledgeKind.DECISION,
                title="Release decision",
                body="Ship the release after the focused gate is green.",
            ),
        )

        assert created.created_by_actor_id == actor_id
        assert repository.list_provenance_inputs(created.provenance_id) == ()

        provenance_row = database.connection.execute(
            """
            SELECT operation, actor_id, reason
            FROM provenance_records
            WHERE provenance_id = ?
            """,
            (created.provenance_id.bytes,),
        ).fetchone()
        assert provenance_row is not None
        assert provenance_row[0] == "knowledge.create"
        assert uuid.UUID(bytes=provenance_row[1]) == actor_id
        assert provenance_row[2] == "direct user knowledge without external source"
    finally:
        database.stop()


def test_orphan_user_knowledge_rejects_malformed_boundaries_before_write(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()

    try:
        chat = ChatService(ChatRepository(database))
        repository = KnowledgeRepository(database)
        chat.ensure_local_user()
        draft = KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.DECISION,
            body="Keep this decision source-free but attributable to the user.",
        )

        with pytest.raises(TypeError, match="actor_id must be a UUID"):
            create_orphan_user_knowledge(
                repository=repository,
                actor_id="not-a-uuid",  # type: ignore[arg-type]
                draft=draft,
            )

        count = database.connection.execute(
            "SELECT COUNT(*) FROM knowledge_units"
        ).fetchone()[0]
        assert count == 0
    finally:
        database.stop()
