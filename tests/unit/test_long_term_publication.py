from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from athena.common.ids import uuid_to_blob
from athena.storage import long_term_publication as publication
from athena.storage.canonical_commit_bundle import (
    CanonicalCommitRecord,
    serialize_canonical_commit_bundle,
    verify_canonical_commit_bundle,
)
from athena.storage.database import SQLiteDatabase
from athena.storage.long_term_publication import (
    LongTermPublicationConflictError,
    LongTermPublicationError,
    publish_staged_commit,
)
from athena.storage.structured_replication import (
    ReplicationCommitState,
    ReplicationTargetState,
    StructuredReplicationRepository,
)


def _runtime(tmp_path: Path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id = uuid.uuid4()
    database.connection.execute(
        """
        INSERT INTO actors(
            actor_id, actor_type, display_name, plugin_id, created_at_us, active
        ) VALUES (?, 'user', 'Tester', NULL, 1, 1)
        """,
        (uuid_to_blob(actor_id),),
    )
    repository = StructuredReplicationRepository(database)
    root = (tmp_path / "long-term").absolute()
    target = repository.register_target(
        str(root),
        target_id=uuid.uuid4(),
        now_us=10,
    )
    return database, repository, actor_id, root, target.target_id


def _commit(
    database: SQLiteDatabase,
    actor_id: uuid.UUID,
    *,
    commit_id: uuid.UUID,
    marker: int,
) -> int:
    cursor = database.connection.execute(
        """
        INSERT INTO commit_records(
            commit_id, committed_at_us, actor_id, operation_type, reason
        ) VALUES (?, ?, ?, 'test.commit', NULL)
        """,
        (uuid_to_blob(commit_id), marker, uuid_to_blob(actor_id)),
    )
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid)


def _bundle(
    *,
    commit_id: uuid.UUID,
    commit_seq: int,
    previous_hash: str | None,
):
    return serialize_canonical_commit_bundle(
        commit_id=commit_id,
        commit_seq=commit_seq,
        schema_version=41,
        previous_hash=previous_hash,
        records=[
            CanonicalCommitRecord(
                record_type="test_revision",
                record_id=f"record-{commit_seq}",
                schema_version=1,
                metadata={"state": "active"},
                payload={"value": commit_seq},
                payload_kind="json",
            )
        ],
    )


def _stage(
    repository: StructuredReplicationRepository,
    target_id: uuid.UUID,
    *,
    bundle,
    commit_seq: int,
    previous_hash: str | None,
) -> None:
    repository.stage_commit(
        target_id,
        commit_seq=commit_seq,
        head_hash=bundle.bundle_hash,
        previous_head_hash=previous_hash,
        now_us=20 + commit_seq,
    )


def _canonical_json(value: dict[str, object]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def test_publish_staged_commit_writes_verified_object_head_and_watermark(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    target = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=bundle.data,
        now_us=30,
    )

    assert target.state is ReplicationTargetState.ACTIVE
    assert target.confirmed_commit_seq == commit_seq
    assert target.confirmed_head_hash == bundle.bundle_hash
    commit = repository.get_commit(target_id, commit_seq)
    assert commit.state is ReplicationCommitState.VERIFIED
    assert commit.verified_at_us == 30

    descriptor = json.loads((root / "repository.json").read_text(encoding="utf-8"))
    assert descriptor == {
        "format": "athena.long-term-repository",
        "format_version": 1,
        "target_id": str(target_id),
    }

    commit_path = root / "commits" / f"{commit_seq:020d}.json"
    assert commit_path.read_bytes() == bundle.data
    assert verify_canonical_commit_bundle(commit_path.read_bytes()) == bundle

    head = json.loads((root / "replication" / "head.json").read_text(encoding="utf-8"))
    assert head == {
        "commit_seq": commit_seq,
        "format": "athena.long-term-head",
        "format_version": 1,
        "head_hash": bundle.bundle_hash,
        "target_id": str(target_id),
    }
    database.stop()


def test_publication_advances_two_commits_without_replacing_first_object(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)

    first_id = uuid.uuid4()
    first_seq = _commit(database, actor_id, commit_id=first_id, marker=1)
    first = _bundle(commit_id=first_id, commit_seq=first_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=first,
        commit_seq=first_seq,
        previous_hash=None,
    )
    publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=first.data,
        now_us=30,
    )
    first_path = root / "commits" / f"{first_seq:020d}.json"
    first_bytes = first_path.read_bytes()

    second_id = uuid.uuid4()
    second_seq = _commit(database, actor_id, commit_id=second_id, marker=2)
    second = _bundle(
        commit_id=second_id,
        commit_seq=second_seq,
        previous_hash=first.bundle_hash,
    )
    _stage(
        repository,
        target_id,
        bundle=second,
        commit_seq=second_seq,
        previous_hash=first.bundle_hash,
    )
    target = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=second.data,
        now_us=40,
    )

    assert target.confirmed_commit_seq == second_seq
    assert target.confirmed_head_hash == second.bundle_hash
    assert first_path.read_bytes() == first_bytes == first.data
    assert (root / "commits" / f"{second_seq:020d}.json").read_bytes() == second.data
    database.stop()


def test_retry_after_commit_object_write_before_head_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    real_write = publication.durable_write_bytes

    def crash_before_head(path: Path, data: bytes, *, mode: int = 0o600) -> None:
        if path.name == "head.json":
            raise RuntimeError("simulated crash before head publication")
        real_write(path, data, mode=mode)

    with monkeypatch.context() as scoped:
        scoped.setattr(publication, "durable_write_bytes", crash_before_head)
        with pytest.raises(RuntimeError, match="simulated crash"):
            publish_staged_commit(
                repository,
                target_id=target_id,
                target_root=root,
                bundle_data=bundle.data,
            )

    commit_path = root / "commits" / f"{commit_seq:020d}.json"
    assert commit_path.read_bytes() == bundle.data
    assert not (root / "replication" / "head.json").exists()
    assert repository.get_commit(target_id, commit_seq).state is ReplicationCommitState.PENDING

    target = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=bundle.data,
        now_us=31,
    )
    assert target.confirmed_commit_seq == commit_seq
    assert repository.get_commit(target_id, commit_seq).state is ReplicationCommitState.VERIFIED
    database.stop()


def test_retry_after_head_write_before_database_confirmation_resumes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    def crash_before_confirmation(*args, **kwargs):
        raise RuntimeError("simulated crash before DB confirmation")

    with monkeypatch.context() as scoped:
        scoped.setattr(repository, "confirm_commit", crash_before_confirmation)
        with pytest.raises(RuntimeError, match="simulated crash"):
            publish_staged_commit(
                repository,
                target_id=target_id,
                target_root=root,
                bundle_data=bundle.data,
            )

    assert (root / "commits" / f"{commit_seq:020d}.json").read_bytes() == bundle.data
    assert (root / "replication" / "head.json").is_file()
    assert repository.get_commit(target_id, commit_seq).state is ReplicationCommitState.PENDING

    target = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=bundle.data,
        now_us=32,
    )
    assert target.confirmed_commit_seq == commit_seq
    assert target.confirmed_head_hash == bundle.bundle_hash
    database.stop()


def test_unexpected_physical_head_enters_conflict_without_overwriting_it(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)

    first_id = uuid.uuid4()
    first_seq = _commit(database, actor_id, commit_id=first_id, marker=1)
    first = _bundle(commit_id=first_id, commit_seq=first_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=first,
        commit_seq=first_seq,
        previous_hash=None,
    )
    publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=first.data,
    )

    second_id = uuid.uuid4()
    second_seq = _commit(database, actor_id, commit_id=second_id, marker=2)
    second = _bundle(
        commit_id=second_id,
        commit_seq=second_seq,
        previous_hash=first.bundle_hash,
    )
    _stage(
        repository,
        target_id,
        bundle=second,
        commit_seq=second_seq,
        previous_hash=first.bundle_hash,
    )

    foreign_head = _canonical_json(
        {
            "commit_seq": 999,
            "format": "athena.long-term-head",
            "format_version": 1,
            "head_hash": "cc" * 32,
            "target_id": str(target_id),
        }
    )
    head_path = root / "replication" / "head.json"
    head_path.write_bytes(foreign_head)

    with pytest.raises(LongTermPublicationConflictError, match="Physical long-term head"):
        publish_staged_commit(
            repository,
            target_id=target_id,
            target_root=root,
            bundle_data=second.data,
            now_us=55,
        )

    conflicted = repository.get_target(target_id)
    assert conflicted.state is ReplicationTargetState.CONFLICT
    assert conflicted.conflict_code == "unexpected_target_head"
    assert head_path.read_bytes() == foreign_head
    assert not (root / "commits" / f"{second_seq:020d}.json").exists()
    database.stop()


def test_head_without_matching_commit_object_fails_closed_on_resume(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    (root / "replication").mkdir(parents=True)
    (root / "commits").mkdir()
    (root / "replication" / "head.json").write_bytes(
        _canonical_json(
            {
                "commit_seq": commit_seq,
                "format": "athena.long-term-head",
                "format_version": 1,
                "head_hash": bundle.bundle_hash,
                "target_id": str(target_id),
            }
        )
    )

    with pytest.raises(LongTermPublicationConflictError, match="no matching immutable"):
        publish_staged_commit(
            repository,
            target_id=target_id,
            target_root=root,
            bundle_data=bundle.data,
            now_us=60,
        )

    target = repository.get_target(target_id)
    assert target.state is ReplicationTargetState.CONFLICT
    assert target.conflict_code == "head_without_commit_object"
    database.stop()


def test_existing_tampered_commit_object_is_never_overwritten(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    commit_root = root / "commits"
    (root / "replication").mkdir(parents=True)
    commit_root.mkdir()
    commit_path = commit_root / f"{commit_seq:020d}.json"
    commit_path.write_bytes(b'{"tampered":true}')

    with pytest.raises(LongTermPublicationConflictError, match="invalid"):
        publish_staged_commit(
            repository,
            target_id=target_id,
            target_root=root,
            bundle_data=bundle.data,
            now_us=70,
        )

    assert commit_path.read_bytes() == b'{"tampered":true}'
    target = repository.get_target(target_id)
    assert target.state is ReplicationTargetState.CONFLICT
    assert target.conflict_code == "commit_object_invalid"
    database.stop()


def test_bundle_commit_identity_must_match_local_commit_record(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    local_commit_id = uuid.uuid4()
    commit_seq = _commit(
        database,
        actor_id,
        commit_id=local_commit_id,
        marker=1,
    )
    bundle = _bundle(
        commit_id=uuid.uuid4(),
        commit_seq=commit_seq,
        previous_hash=None,
    )
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )

    with pytest.raises(LongTermPublicationError, match="commit_id does not match"):
        publish_staged_commit(
            repository,
            target_id=target_id,
            target_root=root,
            bundle_data=bundle.data,
        )

    assert not root.exists()
    assert repository.get_target(target_id).state is ReplicationTargetState.PENDING
    database.stop()


def test_target_locator_must_match_exact_physical_root(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )
    different = (tmp_path / "different-long-term").absolute()

    with pytest.raises(LongTermPublicationError, match="does not match long_term_root"):
        publish_staged_commit(
            repository,
            target_id=target_id,
            target_root=different,
            bundle_data=bundle.data,
        )

    assert not root.exists()
    assert not different.exists()
    database.stop()


def test_retry_of_already_verified_commit_is_read_only_and_successful(tmp_path: Path) -> None:
    database, repository, actor_id, root, target_id = _runtime(tmp_path)
    commit_id = uuid.uuid4()
    commit_seq = _commit(database, actor_id, commit_id=commit_id, marker=1)
    bundle = _bundle(commit_id=commit_id, commit_seq=commit_seq, previous_hash=None)
    _stage(
        repository,
        target_id,
        bundle=bundle,
        commit_seq=commit_seq,
        previous_hash=None,
    )
    first = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=bundle.data,
        now_us=80,
    )
    head_path = root / "replication" / "head.json"
    commit_path = root / "commits" / f"{commit_seq:020d}.json"
    head_bytes = head_path.read_bytes()
    commit_bytes = commit_path.read_bytes()

    second = publish_staged_commit(
        repository,
        target_id=target_id,
        target_root=root,
        bundle_data=bundle.data,
        now_us=90,
    )

    assert second == first
    assert head_path.read_bytes() == head_bytes
    assert commit_path.read_bytes() == commit_bytes
    assert repository.get_commit(target_id, commit_seq).verified_at_us == 80
    database.stop()
