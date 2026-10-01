import pytest

from athena.chat.repository import (
    ChatMessageNotFoundError,
    ChatRepository,
    UnsupportedMessageEditError,
)
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase


def _service(tmp_path) -> tuple[SQLiteDatabase, ChatService]:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    return database, ChatService(ChatRepository(database))


def test_edit_user_message_creates_immutable_successor_revision(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    original = service.add_user_message(chat_id=chat_id, content="original")

    edited = service.edit_user_message(
        chat_id=chat_id,
        message_id=original.message_id,
        content="revised",
    )

    assert edited.message_id == original.message_id
    assert edited.revision_id != original.revision_id
    assert edited.content == "revised"
    assert service.load_chat(chat_id).messages[0].content == "revised"

    old_payload = database.connection.execute(
        """
        SELECT content
        FROM chat_message_revisions
        WHERE revision_id = ?
        """,
        (uuid_to_blob(original.revision_id),),
    ).fetchone()
    assert old_payload is not None
    assert old_payload["content"] == "original"

    revision = database.connection.execute(
        """
        SELECT revision_no, parent_revision_id, provenance_id, change_kind
        FROM revisions
        WHERE revision_id = ?
        """,
        (uuid_to_blob(edited.revision_id),),
    ).fetchone()
    assert revision is not None
    assert int(revision["revision_no"]) == 2
    assert bytes(revision["parent_revision_id"]) == uuid_to_blob(original.revision_id)
    assert revision["change_kind"] == "update"

    provenance_input = database.connection.execute(
        """
        SELECT input_entity_id, input_revision_id, input_role, ordinal
        FROM provenance_inputs
        WHERE provenance_id = ?
        """,
        (bytes(revision["provenance_id"]),),
    ).fetchone()
    assert provenance_input is not None
    assert bytes(provenance_input["input_entity_id"]) == uuid_to_blob(
        original.message_id
    )
    assert bytes(provenance_input["input_revision_id"]) == uuid_to_blob(
        original.revision_id
    )
    assert provenance_input["input_role"] == "prior_revision"
    assert int(provenance_input["ordinal"]) == 0
    database.stop()


def test_edit_rejects_assistant_message_without_new_revision(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    assistant = service.add_assistant_message(
        chat_id=chat_id,
        content="answer",
        provider_id="lmstudio",
        model_id="local-model",
    )

    with pytest.raises(UnsupportedMessageEditError):
        service.edit_user_message(
            chat_id=chat_id,
            message_id=assistant.message_id,
            content="tampered",
        )

    revision_count = database.connection.execute(
        """
        SELECT COUNT(*)
        FROM revisions
        WHERE entity_id = ?
        """,
        (uuid_to_blob(assistant.message_id),),
    ).fetchone()[0]
    assert int(revision_count) == 1
    assert service.load_chat(chat_id).messages[0].content == "answer"
    database.stop()


def test_fork_chat_copies_history_through_exact_revision_with_provenance(tmp_path) -> None:
    database, service = _service(tmp_path)
    source_chat_id = service.create_chat()
    first = service.add_user_message(chat_id=source_chat_id, content="first")
    reply = service.add_assistant_message(
        chat_id=source_chat_id,
        content="reply",
        provider_id="lmstudio",
        model_id="local-model",
    )
    fork_point = service.add_user_message(chat_id=source_chat_id, content="branch here")
    later = service.add_assistant_message(
        chat_id=source_chat_id,
        content="later",
        provider_id="lmstudio",
        model_id="local-model",
    )

    fork_chat_id = service.fork_chat_from_message(
        chat_id=source_chat_id,
        source_message_id=fork_point.message_id,
    )

    forked = service.load_chat(fork_chat_id)
    source = service.load_chat(source_chat_id)
    assert [message.content for message in forked.messages] == [
        "first",
        "reply",
        "branch here",
    ]
    assert [message.content for message in source.messages] == [
        "first",
        "reply",
        "branch here",
        "later",
    ]
    assert later.message_id not in {message.message_id for message in forked.messages}

    source_prefix = (first, reply, fork_point)
    for source_message, forked_message in zip(
        source_prefix,
        forked.messages,
        strict=True,
    ):
        assert forked_message.message_id != source_message.message_id
        assert forked_message.revision_id != source_message.revision_id
        assert forked_message.message_type == source_message.message_type
        assert forked_message.actor_id == source_message.actor_id

        provenance = database.connection.execute(
            """
            SELECT provenance_id
            FROM provenance_records
            WHERE subject_entity_id = ?
              AND subject_revision_id = ?
              AND operation = 'chat_message.fork'
            """,
            (
                uuid_to_blob(forked_message.message_id),
                uuid_to_blob(forked_message.revision_id),
            ),
        ).fetchone()
        assert provenance is not None

        provenance_input = database.connection.execute(
            """
            SELECT input_entity_id, input_revision_id, input_role, ordinal
            FROM provenance_inputs
            WHERE provenance_id = ?
            """,
            (bytes(provenance["provenance_id"]),),
        ).fetchone()
        assert provenance_input is not None
        assert bytes(provenance_input["input_entity_id"]) == uuid_to_blob(
            source_message.message_id
        )
        assert bytes(provenance_input["input_revision_id"]) == uuid_to_blob(
            source_message.revision_id
        )
        assert provenance_input["input_role"] == "fork_source"
        assert int(provenance_input["ordinal"]) == 0

    chat_provenance = database.connection.execute(
        """
        SELECT provenance_id
        FROM provenance_records
        WHERE subject_entity_id = ?
          AND subject_revision_id IS NULL
          AND operation = 'chat.fork'
        """,
        (uuid_to_blob(fork_chat_id),),
    ).fetchone()
    assert chat_provenance is not None
    fork_input = database.connection.execute(
        """
        SELECT input_entity_id, input_revision_id, input_role, ordinal
        FROM provenance_inputs
        WHERE provenance_id = ?
        """,
        (bytes(chat_provenance["provenance_id"]),),
    ).fetchone()
    assert fork_input is not None
    assert bytes(fork_input["input_entity_id"]) == uuid_to_blob(fork_point.message_id)
    assert bytes(fork_input["input_revision_id"]) == uuid_to_blob(
        fork_point.revision_id
    )
    assert fork_input["input_role"] == "fork_point"
    assert int(fork_input["ordinal"]) == 0
    database.stop()


def test_fork_rejects_message_from_another_chat_without_partial_chat(tmp_path) -> None:
    database, service = _service(tmp_path)
    first_chat = service.create_chat()
    second_chat = service.create_chat()
    foreign_message = service.add_user_message(
        chat_id=second_chat,
        content="belongs elsewhere",
    )
    before = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]

    with pytest.raises(ChatMessageNotFoundError):
        service.fork_chat_from_message(
            chat_id=first_chat,
            source_message_id=foreign_message.message_id,
        )

    after = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    assert int(after) == int(before)
    database.stop()
