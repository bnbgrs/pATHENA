from unittest.mock import patch

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService, EmptyMessageError
from athena.storage.database import SQLiteDatabase


def test_local_user_actor_is_reused(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    service = ChatService(ChatRepository(database))

    first = service.ensure_local_user()
    second = service.ensure_local_user()

    assert first == second
    actor_count = database.connection.execute(
        "SELECT COUNT(*) FROM actors WHERE actor_type = 'user'"
    ).fetchone()[0]
    assert actor_count == 1
    database.stop()


def test_actor_ensure_reuses_identity_inside_repository_boundary(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = ChatRepository(database)

    first = repository.ensure_actor(
        actor_type="primary_model",
        display_name="lmstudio:model-a",
    )
    second = repository.ensure_actor(
        actor_type="primary_model",
        display_name="lmstudio:model-a",
    )

    assert first == second
    actor_count = database.connection.execute(
        """
        SELECT COUNT(*)
        FROM actors
        WHERE actor_type = 'primary_model'
          AND display_name = 'lmstudio:model-a'
          AND active = 1
        """
    ).fetchone()[0]
    assert actor_count == 1
    database.stop()


def test_service_actor_ensure_does_not_split_lookup_from_creation(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    repository = ChatRepository(database)
    service = ChatService(repository)

    with (
        patch.object(
            repository,
            "find_active_actor",
            side_effect=AssertionError("split actor lookup must not be used"),
        ),
        patch.object(
            repository,
            "create_actor",
            side_effect=AssertionError("split actor creation must not be used"),
        ),
    ):
        local_user = service.ensure_local_user()
        primary_model = service.ensure_primary_model(
            provider_id="lmstudio",
            model_id="model-a",
        )

    assert local_user != primary_model
    database.stop()


def test_blank_user_message_is_rejected_before_persistence(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    service = ChatService(ChatRepository(database))
    chat_id = service.create_chat()

    with pytest.raises(EmptyMessageError):
        service.add_user_message(chat_id=chat_id, content="   ")

    count = database.connection.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
    assert count == 0
    database.stop()


def test_chat_list_reports_message_counts(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    service = ChatService(ChatRepository(database))
    first_chat = service.create_chat()
    second_chat = service.create_chat()
    service.add_user_message(chat_id=first_chat, content="one")
    service.add_user_message(chat_id=first_chat, content="two")

    summaries = {summary.chat_id: summary for summary in service.list_chats()}

    assert summaries[first_chat].message_count == 2
    assert summaries[second_chat].message_count == 0
    database.stop()
