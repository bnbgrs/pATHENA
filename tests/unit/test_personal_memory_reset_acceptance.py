import hashlib

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.knowledge.models import KnowledgeKind
from athena.knowledge.repository import KnowledgeRepository
from athena.knowledge.service import KnowledgeService
from athena.memory.models import MemoryKind
from athena.memory.repository import PersonalMemoryRepository
from athena.memory.service import PersonalMemoryService
from athena.source.blob_store import PreparedBlob
from athena.source.models import BlobStorageArea
from athena.source.repository import SourceRepository
from athena.storage.database import SQLiteDatabase


def test_personal_memory_reset_preserves_raw_chat_knowledge_and_sources(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    memory = PersonalMemoryService(PersonalMemoryRepository(database), chat)

    chat_id = chat.create_chat()
    chat.add_user_message(chat_id=chat_id, content="Keep this archived chat message.")

    knowledge_repository = KnowledgeRepository(database)
    knowledge = KnowledgeService(knowledge_repository, chat)
    knowledge_revision = knowledge.promote_chat_message(
        chat_id=chat_id,
        sequence_no=1,
        knowledge_kind=KnowledgeKind.FACT,
    )

    actor_id = chat.ensure_local_user()
    source_repository = SourceRepository(database)
    source_capture = source_repository.capture_file(
        actor_id=actor_id,
        original_name="reset-preservation.txt",
        source_uri="file:///reset-preservation.txt",
        prepared_blob=PreparedBlob(
            byte_length=3,
            media_type="text/plain",
            integrity_sha256=hashlib.sha256(b"raw").digest(),
            storage_area=BlobStorageArea.SPOOL,
            storage_locator="test/reset-preservation",
            source_modified_at_us=None,
        ),
    )

    first = memory.remember(
        content="Use Markdown.",
        memory_kind=MemoryKind.RESPONSE_STYLE,
    )
    second = memory.remember(
        content="Prefer German.",
        memory_kind=MemoryKind.LANGUAGE_PREFERENCE,
    )

    archived_before = chat.load_chat(chat_id)
    knowledge_before = knowledge_repository.load_current(knowledge_revision.knowledge_id)
    source_before = source_repository.get(source_capture.source.source_id)

    result = memory.reset()

    assert result.commit_id is not None
    assert result.deleted_count == 2
    assert memory.list(include_inactive=True) == ()

    archived_after = chat.load_chat(chat_id)
    assert archived_after == archived_before
    assert knowledge_repository.load_current(knowledge_revision.knowledge_id) == knowledge_before
    assert source_repository.get(source_capture.source.source_id) == source_before

    for created in (first, second):
        deleted = memory.repository.load_current(created.memory_id, include_deleted=True)
        assert deleted.lifecycle_state == "deleted"
        assert deleted.revision == created

    database.stop()
