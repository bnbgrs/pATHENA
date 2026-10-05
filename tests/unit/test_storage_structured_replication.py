from __future__ import annotations

import sqlite3
import uuid

import pytest

from athena.common.ids import uuid_to_blob
from athena.storage.database import SQLiteDatabase
from athena.storage.schema_contract import (
    CHAT_PREFERENCES_MIGRATION_ID,
    CHAT_PREFERENCES_SCHEMA_VERSION,
    GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID,
    GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
    DatabaseCompatibilityError,
)
from athena.storage.structured_replication import (
    ReplicationCommitState,
    ReplicationTargetState,
    StructuredReplicationInvariantError,
    StructuredReplicationRepository,
)


def _runtime(tmp_path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id = uuid.uuid4()
    database.connection.execute(
        "INSERT INTO actors("
        "actor_id, actor_type, display_name, plugin_id, created_at_us, active"
        ") VALUES (?, 'user', 'Tester', NULL, 1, 1)",
        (uuid_to_blob(actor_id),),
    )
    return database, StructuredReplicationRepository(database), actor_id


def _commit(database, actor_id: uuid.UUID, marker: int) -> int:
    cursor = database.connection.execute(
        """
        INSERT INTO commit_records (
            commit_id, committed_at_us, actor_id, operation_type, reason
        ) VALUES (?, ?, ?, 'test.commit', NULL)
        """,
        (uuid_to_blob(uuid.uuid4()), marker, uuid_to_blob(actor_id)),
    )
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid)


def test_replication_state_survives_restart_and_conflict_recovery(tmp_path) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    first_seq = _commit(database, actor_id, 1)
    target = repository.register_target("long-term/primary", now_us=10)
    first_hash = "11" * 32

    staged = repository.stage_commit(
        target.target_id,
        commit_seq=first_seq,
        head_hash=first_hash,
        previous_head_hash=None,
        now_us=11,
    )
    assert staged.state is ReplicationCommitState.PENDING
    database.stop()

    database.start()
    repository = StructuredReplicationRepository(database)
    assert repository.get_commit(target.target_id, first_seq) == staged
    confirmed = repository.confirm_commit(
        target.target_id,
        commit_seq=first_seq,
        head_hash=first_hash,
        now_us=12,
    )
    assert confirmed.state is ReplicationTargetState.ACTIVE
    assert confirmed.confirmed_commit_seq == first_seq
    assert confirmed.confirmed_head_hash == first_hash

    conflicted = repository.mark_conflict(
        target.target_id,
        conflict_code="unexpected_target_head",
        now_us=13,
    )
    assert conflicted.state is ReplicationTargetState.CONFLICT
    with pytest.raises(StructuredReplicationInvariantError):
        repository.stage_commit(
            target.target_id,
            commit_seq=first_seq + 1,
            head_hash="22" * 32,
            previous_head_hash=first_hash,
        )
    recovering = repository.begin_recovery(target.target_id, now_us=14)
    assert recovering.state is ReplicationTargetState.RECOVERING
    assert recovering.conflict_code is None
    database.stop()


def test_confirmation_is_monotone_and_hash_fenced(tmp_path) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    first_seq = _commit(database, actor_id, 1)
    second_seq = _commit(database, actor_id, 2)
    target = repository.register_target("long-term/primary")
    first_hash = "aa" * 32
    second_hash = "bb" * 32
    repository.stage_commit(
        target.target_id,
        commit_seq=first_seq,
        head_hash=first_hash,
        previous_head_hash=None,
    )
    repository.stage_commit(
        target.target_id,
        commit_seq=second_seq,
        head_hash=second_hash,
        previous_head_hash=first_hash,
    )

    with pytest.raises(StructuredReplicationInvariantError):
        repository.confirm_commit(
            target.target_id,
            commit_seq=second_seq,
            head_hash=second_hash,
        )
    with pytest.raises(StructuredReplicationInvariantError):
        repository.confirm_commit(
            target.target_id,
            commit_seq=first_seq,
            head_hash="cc" * 32,
        )

    first = repository.confirm_commit(
        target.target_id,
        commit_seq=first_seq,
        head_hash=first_hash,
    )
    second = repository.confirm_commit(
        target.target_id,
        commit_seq=second_seq,
        head_hash=second_hash,
    )
    assert first.confirmed_commit_seq == first_seq
    assert second.confirmed_commit_seq == second_seq
    assert second.confirmed_head_hash == second_hash
    database.stop()


def test_staging_rejects_gap_and_unexpected_history(tmp_path) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    first_seq = _commit(database, actor_id, 1)
    _commit(database, actor_id, 2)
    target = repository.register_target("long-term/primary")

    with pytest.raises(StructuredReplicationInvariantError):
        repository.stage_commit(
            target.target_id,
            commit_seq=first_seq + 1,
            head_hash="11" * 32,
            previous_head_hash=None,
        )
    repository.stage_commit(
        target.target_id,
        commit_seq=first_seq,
        head_hash="11" * 32,
        previous_head_hash=None,
    )
    with pytest.raises(StructuredReplicationInvariantError):
        repository.stage_commit(
            target.target_id,
            commit_seq=first_seq + 1,
            head_hash="22" * 32,
            previous_head_hash="33" * 32,
        )
    database.stop()


def test_structured_replication_migration_restarts_from_compatible_partial_state(
    tmp_path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    with database.write_transaction() as connection:
        connection.execute(
            """
            UPDATE schema_metadata
            SET schema_version = ?,
                last_migration_id = ?,
                minimum_reader_version = ?
            WHERE singleton_id = 1
            """,
            (
                GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
                GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID,
                GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
            ),
        )
        connection.execute(
            f"PRAGMA user_version = {GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION}"
        )
    database.stop()

    restarted = SQLiteDatabase(path)
    restarted.start()
    try:
        metadata = restarted.connection.execute(
            """
            SELECT schema_version, last_migration_id, minimum_reader_version
            FROM schema_metadata
            WHERE singleton_id = 1
            """
        ).fetchone()
        assert metadata is not None
        assert tuple(metadata) == (
            CHAT_PREFERENCES_SCHEMA_VERSION,
            CHAT_PREFERENCES_MIGRATION_ID,
            CHAT_PREFERENCES_SCHEMA_VERSION,
        )
    finally:
        restarted.stop()


def test_structured_replication_migration_rejects_incompatible_partial_table(
    tmp_path,
) -> None:
    path = tmp_path / "athena.db"
    database = SQLiteDatabase(path)
    database.start()
    with database.write_transaction() as connection:
        connection.execute("DROP INDEX idx_replication_commits_state")
        connection.execute("DROP TABLE replication_commits")
        connection.execute("DROP TABLE replication_targets")
        connection.execute(
            "CREATE TABLE replication_targets (target_id BLOB PRIMARY KEY)"
        )
        connection.execute(
            """
            UPDATE schema_metadata
            SET schema_version = ?,
                last_migration_id = ?,
                minimum_reader_version = ?
            WHERE singleton_id = 1
            """,
            (
                GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
                GROUNDED_RESPONSE_RECEIPT_MIGRATION_ID,
                GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION,
            ),
        )
        connection.execute(
            f"PRAGMA user_version = {GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION}"
        )
    database.stop()

    incompatible = SQLiteDatabase(path)
    with pytest.raises(DatabaseCompatibilityError, match="incompatible schema"):
        incompatible.start()

    connection = sqlite3.connect(path)
    try:
        user_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
        columns = tuple(
            str(row[1])
            for row in connection.execute(
                "PRAGMA table_info(replication_targets)"
            ).fetchall()
        )
        assert user_version == GROUNDED_RESPONSE_RECEIPT_SCHEMA_VERSION
        assert columns == ("target_id",)
    finally:
        connection.close()
