import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.knowledge.models import KnowledgeKind
from athena.knowledge.repository import KnowledgeNotFoundError, KnowledgeRepository
from athena.knowledge.service import KnowledgeService
from athena.storage.database import SQLiteDatabase


def _service(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    repository = KnowledgeRepository(database)
    return database, chat, KnowledgeService(repository, chat)


def _promote(knowledge: KnowledgeService, chat: ChatService, text: str):
    chat_id = chat.create_chat()
    chat.add_user_message(chat_id=chat_id, content=text)
    return knowledge.promote_chat_message(
        chat_id=chat_id,
        sequence_no=1,
        knowledge_kind=KnowledgeKind.FACT,
    )


def test_plan_merge_requires_existing_sources_and_performs_no_write(tmp_path) -> None:
    database, chat, knowledge = _service(tmp_path)
    try:
        left = _promote(knowledge, chat, "Left canonical fact")
        right = _promote(knowledge, chat, "Right canonical fact")
        before = (
            len(knowledge.history(left.knowledge_id)),
            len(knowledge.history(right.knowledge_id)),
        )

        plan = knowledge.plan_merge(
            left_knowledge_id=left.knowledge_id,
            right_knowledge_id=right.knowledge_id,
            result_knowledge_id=left.knowledge_id,
        )

        after = (
            len(knowledge.history(left.knowledge_id)),
            len(knowledge.history(right.knowledge_id)),
        )
        assert plan.result_entity_id == left.knowledge_id
        assert plan.superseded_entity_ids == (right.knowledge_id,)
        assert plan.retains_existing_identity is True
        assert after == before
    finally:
        database.stop()


def test_plan_merge_rejects_missing_canonical_source(tmp_path) -> None:
    database, chat, knowledge = _service(tmp_path)
    try:
        left = _promote(knowledge, chat, "Existing canonical fact")

        with pytest.raises(KnowledgeNotFoundError):
            knowledge.plan_merge(
                left_knowledge_id=left.knowledge_id,
                right_knowledge_id=uuid.uuid4(),
                result_knowledge_id=left.knowledge_id,
            )
    finally:
        database.stop()


def test_plan_split_requires_existing_source_and_performs_no_write(tmp_path) -> None:
    database, chat, knowledge = _service(tmp_path)
    try:
        source = _promote(knowledge, chat, "Canonical fact to split")
        result_ids = (uuid.uuid4(), uuid.uuid4())
        before = len(knowledge.history(source.knowledge_id))

        plan = knowledge.plan_split(
            source_knowledge_id=source.knowledge_id,
            result_knowledge_ids=result_ids,
        )

        after = len(knowledge.history(source.knowledge_id))
        assert plan.source_entity_id == source.knowledge_id
        assert plan.result_entity_ids == result_ids
        assert plan.superseded_entity_ids == (source.knowledge_id,)
        assert after == before
    finally:
        database.stop()


def test_plan_split_rejects_missing_canonical_source(tmp_path) -> None:
    database, _chat, knowledge = _service(tmp_path)
    try:
        with pytest.raises(KnowledgeNotFoundError):
            knowledge.plan_split(
                source_knowledge_id=uuid.uuid4(),
                result_knowledge_ids=(uuid.uuid4(), uuid.uuid4()),
            )
    finally:
        database.stop()
