from __future__ import annotations

import uuid

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.knowledge.models import KnowledgeKind
from athena.knowledge.obsidian_import import (
    ObsidianImportConflictError,
    ObsidianImportError,
    ObsidianKnowledgeReconciler,
    parse_obsidian_knowledge_edit,
)
from athena.knowledge.obsidian_projection import project_knowledge_snapshot
from athena.knowledge.repository import KnowledgeRepository
from athena.knowledge.service import KnowledgeService
from athena.storage.database import SQLiteDatabase


def _fixture(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    repository = KnowledgeRepository(database)
    knowledge = KnowledgeService(repository, chat)
    chat_id = chat.create_chat()
    chat.add_user_message(chat_id=chat_id, content="Original body")
    created = knowledge.promote_chat_message(
        chat_id=chat_id,
        sequence_no=1,
        knowledge_kind=KnowledgeKind.DECISION,
        title="Original title",
    )
    return database, chat, repository, knowledge, created


def _edit(markdown: str, *, title: str, body: str) -> str:
    lines = markdown.splitlines()
    heading = next(index for index, line in enumerate(lines) if line.startswith("# "))
    lines[heading] = f"# {title}"
    lines[heading + 2 :] = body.splitlines()
    return "\n".join(lines) + "\n"


def test_roundtrip_creates_user_revision_with_base_provenance(tmp_path) -> None:
    database, chat, repository, _knowledge, created = _fixture(tmp_path)
    try:
        snapshot = repository.load_current(created.knowledge_id)
        edited = _edit(
            project_knowledge_snapshot(snapshot).markdown,
            title="Edited in Obsidian",
            body="Edited body\nwith another line.",
        )

        revision = ObsidianKnowledgeReconciler(
            repository=repository,
            chat=chat,
        ).apply_markdown(edited)

        assert revision.knowledge_id == created.knowledge_id
        assert revision.revision_no == created.revision_no + 1
        assert revision.payload.title == "Edited in Obsidian"
        assert revision.payload.body == "Edited body\nwith another line."
        inputs = repository.list_provenance_inputs(revision.provenance_id)
        assert len(inputs) == 1
        assert inputs[0].input_entity_id == created.knowledge_id
        assert inputs[0].input_revision_id == created.revision_id
        assert inputs[0].input_role == "obsidian_projection_base"
    finally:
        database.stop()


def test_stale_export_conflicts_instead_of_overwriting_newer_revision(tmp_path) -> None:
    database, chat, repository, knowledge, created = _fixture(tmp_path)
    try:
        stale = project_knowledge_snapshot(repository.load_current(created.knowledge_id)).markdown
        newer = knowledge.revise(
            knowledge_id=created.knowledge_id,
            title="Canonical newer",
            body="Newer canonical body",
        )
        edited_stale = _edit(stale, title="Stale external", body="Stale external body")

        with pytest.raises(ObsidianImportConflictError, match="stale"):
            ObsidianKnowledgeReconciler(
                repository=repository,
                chat=chat,
            ).apply_markdown(edited_stale)

        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_id == newer.revision_id
        assert current.payload.body == "Newer canonical body"
    finally:
        database.stop()


def test_identity_alias_mismatch_fails_closed() -> None:
    knowledge_id = uuid.uuid4()
    revision_id = uuid.uuid4()
    markdown = (
        "---\n"
        f'athena_id: "{knowledge_id}"\n'
        f'athena_knowledge_id: "{uuid.uuid4()}"\n'
        'entity_type: "knowledge_unit"\n'
        f'revision_id: "{revision_id}"\n'
        f'athena_revision_id: "{revision_id}"\n'
        "revision_no: 1\n"
        "athena_revision_no: 1\n"
        "projection_version: 1\n"
        "---\n\n"
        "# Title\n\n"
        "Body\n"
    )

    with pytest.raises(ObsidianImportError, match="aliases"):
        parse_obsidian_knowledge_edit(markdown)


def test_legacy_projection_identity_remains_parseable(tmp_path) -> None:
    database, _chat, repository, _knowledge, created = _fixture(tmp_path)
    try:
        markdown = project_knowledge_snapshot(
            repository.load_current(created.knowledge_id)
        ).markdown
        lines = [
            line
            for line in markdown.splitlines()
            if not line.startswith(
                ("athena_id:", "entity_type:", "revision_id:", "revision_no:", "projection_version:")
            )
        ]
        parsed = parse_obsidian_knowledge_edit("\n".join(lines) + "\n")
        assert parsed.knowledge_id == created.knowledge_id
        assert parsed.expected_revision_id == created.revision_id
    finally:
        database.stop()


def test_projected_semantic_metadata_cannot_be_silently_edited(tmp_path) -> None:
    database, chat, repository, _knowledge, created = _fixture(tmp_path)
    try:
        markdown = project_knowledge_snapshot(
            repository.load_current(created.knowledge_id)
        ).markdown.replace(
            'athena_kind: "decision"',
            'athena_kind: "fact"',
        )

        with pytest.raises(ObsidianImportError, match="cannot be edited"):
            ObsidianKnowledgeReconciler(
                repository=repository,
                chat=chat,
            ).apply_markdown(markdown)
    finally:
        database.stop()
