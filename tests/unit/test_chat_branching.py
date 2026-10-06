import pytest

from athena.chat.repository import (
    ChatMessageNotFoundError,
    ChatRepository,
    ChatRevisionConflictError,
    UnsupportedChatForkError,
    UnsupportedChatRegenerationError,
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
        expected_revision_id=original.revision_id,
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


def test_edit_rejects_stale_expected_revision_without_mutation(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    original = service.add_user_message(chat_id=chat_id, content="original")
    current = service.edit_user_message(
        chat_id=chat_id,
        message_id=original.message_id,
        expected_revision_id=original.revision_id,
        content="current",
    )

    with pytest.raises(ChatRevisionConflictError):
        service.edit_user_message(
            chat_id=chat_id,
            message_id=original.message_id,
            expected_revision_id=original.revision_id,
            content="stale overwrite",
        )

    loaded = service.load_chat(chat_id).messages[0]
    assert loaded.revision_id == current.revision_id
    assert loaded.content == "current"
    revision_count = database.connection.execute(
        "SELECT COUNT(*) FROM revisions WHERE entity_id = ?",
        (uuid_to_blob(original.message_id),),
    ).fetchone()[0]
    assert int(revision_count) == 2
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
            expected_revision_id=assistant.revision_id,
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


def test_edit_fails_closed_for_protected_user_message(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    message = service.add_user_message(chat_id=chat_id, content="private")
    message_blob = uuid_to_blob(message.message_id)
    revision_blob = uuid_to_blob(message.revision_id)

    def revision_count() -> int:
        return int(
            database.connection.execute(
                "SELECT COUNT(*) FROM revisions WHERE entity_id = ?",
                (message_blob,),
            ).fetchone()[0]
        )

    database.connection.execute(
        """
        UPDATE chats
        SET protection_scope_id = ?
        WHERE chat_id = ?
        """,
        (b"c" * 16, uuid_to_blob(chat_id)),
    )
    with pytest.raises(UnsupportedMessageEditError):
        service.edit_user_message(
            chat_id=chat_id,
            message_id=message.message_id,
            expected_revision_id=message.revision_id,
            content="should not persist",
        )
    assert revision_count() == 1

    database.connection.execute(
        """
        UPDATE chats
        SET protection_scope_id = NULL
        WHERE chat_id = ?
        """,
        (uuid_to_blob(chat_id),),
    )
    database.connection.execute(
        """
        UPDATE entity_registry
        SET protection_scope_id = ?
        WHERE entity_id = ?
        """,
        (b"m" * 16, message_blob),
    )
    with pytest.raises(UnsupportedMessageEditError):
        service.edit_user_message(
            chat_id=chat_id,
            message_id=message.message_id,
            expected_revision_id=message.revision_id,
            content="still blocked",
        )
    assert revision_count() == 1

    database.connection.execute(
        """
        UPDATE entity_registry
        SET protection_scope_id = NULL
        WHERE entity_id = ?
        """,
        (message_blob,),
    )
    database.connection.execute(
        """
        UPDATE chat_message_revisions
        SET protected_payload_id = ?
        WHERE revision_id = ?
        """,
        (b"p" * 16, revision_blob),
    )
    with pytest.raises(UnsupportedMessageEditError):
        service.edit_user_message(
            chat_id=chat_id,
            message_id=message.message_id,
            expected_revision_id=message.revision_id,
            content="also blocked",
        )
    assert revision_count() == 1
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
        source_revision_id=fork_point.revision_id,
    )

    origin = service.get_fork_origin(fork_chat_id)
    assert origin is not None
    assert origin.chat_id == fork_chat_id
    assert origin.source_message_id == fork_point.message_id
    assert origin.source_revision_id == fork_point.revision_id
    assert service.get_fork_origin(source_chat_id) is None

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


def test_fork_rejects_stale_source_revision_without_partial_chat(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    original = service.add_user_message(chat_id=chat_id, content="original")
    service.edit_user_message(
        chat_id=chat_id,
        message_id=original.message_id,
        expected_revision_id=original.revision_id,
        content="new head",
    )
    before = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]

    with pytest.raises(ChatRevisionConflictError):
        service.fork_chat_from_message(
            chat_id=chat_id,
            source_message_id=original.message_id,
            source_revision_id=original.revision_id,
        )

    after = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    assert int(after) == int(before)
    database.stop()


def test_fork_fails_closed_for_protected_chat_or_message(tmp_path) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    message = service.add_user_message(chat_id=chat_id, content="protected")
    before = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]

    database.connection.execute(
        """
        UPDATE chats
        SET protection_scope_id = ?
        WHERE chat_id = ?
        """,
        (b"s" * 16, uuid_to_blob(chat_id)),
    )
    with pytest.raises(UnsupportedChatForkError):
        service.fork_chat_from_message(
            chat_id=chat_id,
            source_message_id=message.message_id,
            source_revision_id=message.revision_id,
        )

    database.connection.execute(
        """
        UPDATE chats
        SET protection_scope_id = NULL
        WHERE chat_id = ?
        """,
        (uuid_to_blob(chat_id),),
    )
    database.connection.execute(
        """
        UPDATE entity_registry
        SET protection_scope_id = ?
        WHERE entity_id = ?
        """,
        (b"e" * 16, uuid_to_blob(message.message_id)),
    )
    with pytest.raises(UnsupportedChatForkError):
        service.fork_chat_from_message(
            chat_id=chat_id,
            source_message_id=message.message_id,
            source_revision_id=message.revision_id,
        )

    database.connection.execute(
        """
        UPDATE entity_registry
        SET protection_scope_id = NULL
        WHERE entity_id = ?
        """,
        (uuid_to_blob(message.message_id),),
    )
    database.connection.execute(
        """
        UPDATE chat_message_revisions
        SET protected_payload_id = ?
        WHERE revision_id = ?
        """,
        (b"p" * 16, uuid_to_blob(message.revision_id)),
    )
    with pytest.raises(UnsupportedChatForkError):
        service.fork_chat_from_message(
            chat_id=chat_id,
            source_message_id=message.message_id,
            source_revision_id=message.revision_id,
        )

    after = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    assert int(after) == int(before)
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
            source_revision_id=foreign_message.revision_id,
        )

    after = database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    assert int(after) == int(before)
    database.stop()


def test_regeneration_plan_branches_before_prompt_and_records_exact_origin(tmp_path) -> None:
    database, service = _service(tmp_path)
    source_chat_id = service.create_chat()
    first = service.add_user_message(chat_id=source_chat_id, content="first")
    first_reply = service.add_assistant_message(
        chat_id=source_chat_id,
        content="first reply",
        provider_id="lmstudio",
        model_id="local-model",
    )
    prompt = service.add_user_message(chat_id=source_chat_id, content="try again")
    answer = service.add_assistant_message(
        chat_id=source_chat_id,
        content="old answer",
        provider_id="lmstudio",
        model_id="local-model",
    )
    service.add_user_message(chat_id=source_chat_id, content="later")

    plan = service.prepare_assistant_regeneration(
        chat_id=source_chat_id,
        source_assistant_message_id=answer.message_id,
        source_assistant_revision_id=answer.revision_id,
    )

    assert plan.branch_chat_id != source_chat_id
    assert plan.source_assistant_message_id == answer.message_id
    assert plan.source_assistant_revision_id == answer.revision_id
    assert plan.source_prompt.message_id == prompt.message_id
    assert plan.source_prompt.revision_id == prompt.revision_id
    assert plan.source_prompt.content == "try again"

    branch = service.load_chat(plan.branch_chat_id)
    assert [message.content for message in branch.messages] == [
        "first",
        "first reply",
    ]
    assert [message.content for message in service.load_chat(source_chat_id).messages] == [
        "first",
        "first reply",
        "try again",
        "old answer",
        "later",
    ]
    assert branch.messages[0].message_id != first.message_id
    assert branch.messages[1].message_id != first_reply.message_id

    provenance = database.connection.execute(
        """
        SELECT provenance_id
        FROM provenance_records
        WHERE subject_entity_id = ?
          AND subject_revision_id IS NULL
          AND operation = 'chat.regenerate'
        """,
        (uuid_to_blob(plan.branch_chat_id),),
    ).fetchone()
    assert provenance is not None
    inputs = database.connection.execute(
        """
        SELECT input_entity_id, input_revision_id, input_role, ordinal
        FROM provenance_inputs
        WHERE provenance_id = ?
        ORDER BY ordinal ASC
        """,
        (bytes(provenance["provenance_id"]),),
    ).fetchall()
    assert len(inputs) == 2
    assert bytes(inputs[0]["input_entity_id"]) == uuid_to_blob(answer.message_id)
    assert bytes(inputs[0]["input_revision_id"]) == uuid_to_blob(answer.revision_id)
    assert inputs[0]["input_role"] == "regenerated_assistant"
    assert int(inputs[0]["ordinal"]) == 0
    assert bytes(inputs[1]["input_entity_id"]) == uuid_to_blob(prompt.message_id)
    assert bytes(inputs[1]["input_revision_id"]) == uuid_to_blob(prompt.revision_id)
    assert inputs[1]["input_role"] == "regeneration_prompt"
    assert int(inputs[1]["ordinal"]) == 1
    database.stop()


def test_regeneration_of_first_reply_creates_empty_branch_ready_for_prompt(tmp_path) -> None:
    database, service = _service(tmp_path)
    source_chat_id = service.create_chat()
    prompt = service.add_user_message(chat_id=source_chat_id, content="hello")
    answer = service.add_assistant_message(
        chat_id=source_chat_id,
        content="world",
        provider_id="lmstudio",
        model_id="local-model",
    )

    plan = service.prepare_assistant_regeneration(
        chat_id=source_chat_id,
        source_assistant_message_id=answer.message_id,
        source_assistant_revision_id=answer.revision_id,
    )

    assert service.load_chat(plan.branch_chat_id).messages == ()
    assert plan.source_prompt.message_id == prompt.message_id
    assert plan.source_prompt.content == "hello"
    database.stop()


def test_regeneration_rejects_non_assistant_or_stale_revision_without_partial_chat(
    tmp_path,
) -> None:
    database, service = _service(tmp_path)
    chat_id = service.create_chat()
    prompt = service.add_user_message(chat_id=chat_id, content="hello")
    answer = service.add_assistant_message(
        chat_id=chat_id,
        content="world",
        provider_id="lmstudio",
        model_id="local-model",
    )
    before = int(database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0])

    with pytest.raises(UnsupportedChatRegenerationError):
        service.prepare_assistant_regeneration(
            chat_id=chat_id,
            source_assistant_message_id=prompt.message_id,
            source_assistant_revision_id=prompt.revision_id,
        )

    with pytest.raises(ChatRevisionConflictError):
        service.prepare_assistant_regeneration(
            chat_id=chat_id,
            source_assistant_message_id=answer.message_id,
            source_assistant_revision_id=prompt.revision_id,
        )

    after = int(database.connection.execute("SELECT COUNT(*) FROM chats").fetchone()[0])
    assert after == before
    database.stop()
