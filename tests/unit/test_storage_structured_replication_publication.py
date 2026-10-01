from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

import athena.storage.structured_replication_publication as publication
from athena.common.ids import uuid_to_blob
from athena.storage.canonical_commit_bundle import (
    CanonicalCommitBundle,
    CanonicalCommitRecord,
    serialize_canonical_commit_bundle,
)
from athena.storage.database import SQLiteDatabase
from athena.storage.durable_fs import durable_mkdir, durable_publish_new_bytes
from athena.storage.structured_replication import (
    ReplicationCommitState,
    ReplicationTargetState,
    StructuredReplicationInvariantError,
    StructuredReplicationRepository,
)
from athena.storage.structured_replication_publication import (
    StructuredReplicationConflictError,
    StructuredReplicationPublicationError,
    StructuredReplicationPublisher,
)


def _runtime(
    tmp_path: Path,
) -> tuple[SQLiteDatabase, StructuredReplicationRepository, uuid.UUID]:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    actor_id = uuid.uuid4()
    database.connection.execute(
        "INSERT INTO actors("
        "actor_id, actor_type, display_name, plugin_id, created_at_us, active"
        ") VALUES (?, 'user', 'Replication test', NULL, 1, 1)",
        (uuid_to_blob(actor_id),),
    )
    return database, StructuredReplicationRepository(database), actor_id


def _commit(
    database: SQLiteDatabase,
    actor_id: uuid.UUID,
    marker: int,
) -> tuple[int, uuid.UUID]:
    commit_id = uuid.uuid4()
    cursor = database.connection.execute(
        """
        INSERT INTO commit_records (
            commit_id, committed_at_us, actor_id, operation_type, reason
        ) VALUES (?, ?, ?, 'test.replication', NULL)
        """,
        (uuid_to_blob(commit_id), marker, uuid_to_blob(actor_id)),
    )
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid), commit_id


def _bundle(
    *,
    commit_id: uuid.UUID,
    commit_seq: int,
    previous_hash: str | None,
    marker: int,
) -> CanonicalCommitBundle:
    return serialize_canonical_commit_bundle(
        commit_id=commit_id,
        commit_seq=commit_seq,
        schema_version=41,
        previous_hash=previous_hash,
        records=(
            CanonicalCommitRecord(
                record_type="test_record",
                record_id=f"record-{marker}",
                schema_version=1,
                metadata={"state": "active"},
                payload_kind="json",
                payload={"marker": marker},
            ),
        ),
    )


def _stage(
    repository: StructuredReplicationRepository,
    target_id: uuid.UUID,
    bundle: CanonicalCommitBundle,
    *,
    commit_seq: int,
    previous_hash: str | None,
) -> None:
    repository.stage_commit(
        target_id,
        commit_seq=commit_seq,
        head_hash=bundle.bundle_hash,
        previous_head_hash=previous_hash,
    )


def _layout(root: Path) -> tuple[Path, Path]:
    return root / "commits", root / "manifests"


def _initialize_repository_root(
    root: Path,
    target_id: uuid.UUID,
) -> tuple[Path, Path]:
    durable_mkdir(root, parents=True, exist_ok=True)
    durable_publish_new_bytes(
        root / "repository.json",
        publication._canonical_repository_bytes(target_id),
    )
    commits_dir, manifest_dir = _layout(root)
    durable_mkdir(commits_dir, parents=False, exist_ok=True)
    durable_mkdir(manifest_dir, parents=False, exist_ok=True)
    return commits_dir, manifest_dir


def test_publish_verifies_filesystem_before_advancing_local_watermark(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )

        confirmed = StructuredReplicationPublisher(repository).publish_staged_bundle(
            target.target_id,
            bundle,
        )

        assert confirmed.state is ReplicationTargetState.ACTIVE
        assert confirmed.confirmed_commit_seq == commit_seq
        assert confirmed.confirmed_head_hash == bundle.bundle_hash
        assert (
            repository.get_commit(target.target_id, commit_seq).state
            is ReplicationCommitState.VERIFIED
        )

        commits_dir, manifest_dir = _layout(target_root)
        bundle_path = commits_dir / publication._bundle_name(
            commit_seq,
            bundle.bundle_hash,
        )
        manifest_path = manifest_dir / publication._manifest_name(commit_seq)
        assert bundle_path.read_bytes() == bundle.data
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["commit_seq"] == commit_seq
        assert manifest["head_hash"] == bundle.bundle_hash
        assert manifest["previous_head_hash"] is None
        repository_manifest = json.loads(
            (target_root / "repository.json").read_text(encoding="utf-8")
        )
        assert repository_manifest["repository_id"] == str(target.target_id)
        assert repository_manifest["hash_algorithm"] == "sha256"
        assert (target_root / "snapshots").is_dir()
        assert (target_root / "replication").is_dir()

        before = sorted(path.name for path in commits_dir.iterdir())
        again = StructuredReplicationPublisher(repository).publish_staged_bundle(
            target.target_id,
            bundle,
        )
        assert again == confirmed
        assert sorted(path.name for path in commits_dir.iterdir()) == before
    finally:
        database.stop()


def test_restart_recovers_post_manifest_pre_confirmation_crash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )
        publisher = StructuredReplicationPublisher(repository)

        def crash_before_confirmation(*_args: object, **_kwargs: object) -> object:
            raise RuntimeError("simulated crash before confirmation")

        monkeypatch.setattr(
            repository,
            "confirm_commit",
            crash_before_confirmation,
        )
        with pytest.raises(RuntimeError, match="simulated crash"):
            publisher.publish_staged_bundle(target.target_id, bundle)

        assert (
            repository.get_commit(target.target_id, commit_seq).state
            is ReplicationCommitState.PENDING
        )
        commits_dir, manifest_dir = _layout(target_root)
        assert (commits_dir / publication._bundle_name(
            commit_seq,
            bundle.bundle_hash,
        )).is_file()
        assert (manifest_dir / publication._manifest_name(commit_seq)).is_file()

        resumed_repository = StructuredReplicationRepository(database)
        resumed = StructuredReplicationPublisher(
            resumed_repository
        ).publish_staged_bundle(target.target_id, bundle)

        assert resumed.state is ReplicationTargetState.ACTIVE
        assert resumed.confirmed_commit_seq == commit_seq
        assert (
            resumed_repository.get_commit(target.target_id, commit_seq).state
            is ReplicationCommitState.VERIFIED
        )
    finally:
        database.stop()


def test_restart_recovers_orphan_bundle_before_manifest(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )

        commits_dir, manifest_dir = _initialize_repository_root(
            target_root,
            target.target_id,
        )
        durable_publish_new_bytes(
            commits_dir
            / publication._bundle_name(commit_seq, bundle.bundle_hash),
            bundle.data,
        )

        confirmed = StructuredReplicationPublisher(repository).publish_staged_bundle(
            target.target_id,
            bundle,
        )

        assert confirmed.confirmed_commit_seq == commit_seq
        assert (manifest_dir / publication._manifest_name(commit_seq)).is_file()
    finally:
        database.stop()


def test_existing_conflicting_orphan_is_never_overwritten_and_marks_conflict(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )

        commits_dir, _manifest_dir = _initialize_repository_root(
            target_root,
            target.target_id,
        )
        bundle_path = commits_dir / publication._bundle_name(
            commit_seq,
            bundle.bundle_hash,
        )
        conflicting = b"not-the-staged-bundle"
        durable_publish_new_bytes(bundle_path, conflicting)

        with pytest.raises(
            StructuredReplicationConflictError,
            match="do not match staged history",
        ):
            StructuredReplicationPublisher(repository).publish_staged_bundle(
                target.target_id,
                bundle,
            )

        assert bundle_path.read_bytes() == conflicting
        assert (
            repository.get_target(target.target_id).state
            is ReplicationTargetState.CONFLICT
        )
        assert (
            repository.get_commit(target.target_id, commit_seq).state
            is ReplicationCommitState.PENDING
        )
    finally:
        database.stop()


def test_unexpected_valid_remote_head_enters_conflict_without_overwrite(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        first_seq, first_id = _commit(database, actor_id, 1)
        first = _bundle(
            commit_id=first_id,
            commit_seq=first_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            first,
            commit_seq=first_seq,
            previous_hash=None,
        )
        StructuredReplicationPublisher(repository).publish_staged_bundle(
            target.target_id,
            first,
        )

        second_seq, second_id = _commit(database, actor_id, 2)
        expected = _bundle(
            commit_id=second_id,
            commit_seq=second_seq,
            previous_hash=first.bundle_hash,
            marker=2,
        )
        _stage(
            repository,
            target.target_id,
            expected,
            commit_seq=second_seq,
            previous_hash=first.bundle_hash,
        )
        forged = _bundle(
            commit_id=second_id,
            commit_seq=second_seq,
            previous_hash=first.bundle_hash,
            marker=999,
        )

        commits_dir, manifest_dir = _layout(target_root)
        forged_name = publication._bundle_name(
            second_seq,
            forged.bundle_hash,
        )
        forged_path = commits_dir / forged_name
        forged_manifest = publication._canonical_manifest_bytes(
            commit_seq=second_seq,
            head_hash=forged.bundle_hash,
            previous_head_hash=first.bundle_hash,
            bundle_file=forged_name,
        )
        durable_publish_new_bytes(forged_path, forged.data)
        durable_publish_new_bytes(
            manifest_dir / publication._manifest_name(second_seq),
            forged_manifest,
        )

        expected_path = commits_dir / publication._bundle_name(
            second_seq,
            expected.bundle_hash,
        )
        with pytest.raises(
            StructuredReplicationConflictError,
            match="does not match local confirmed history",
        ):
            StructuredReplicationPublisher(repository).publish_staged_bundle(
                target.target_id,
                expected,
            )

        assert forged_path.read_bytes() == forged.data
        assert not expected_path.exists()
        conflicted = repository.get_target(target.target_id)
        assert conflicted.state is ReplicationTargetState.CONFLICT
        assert conflicted.confirmed_commit_seq == first_seq
        assert conflicted.confirmed_head_hash == first.bundle_hash
    finally:
        database.stop()


def test_tampered_confirmed_bundle_is_detected_on_idempotent_recheck(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )
        publisher = StructuredReplicationPublisher(repository)
        publisher.publish_staged_bundle(target.target_id, bundle)

        commits_dir, _manifest_dir = _layout(target_root)
        bundle_path = commits_dir / publication._bundle_name(
            commit_seq,
            bundle.bundle_hash,
        )
        bundle_path.write_bytes(b"tampered")

        with pytest.raises(StructuredReplicationConflictError):
            publisher.publish_staged_bundle(target.target_id, bundle)

        assert (
            repository.get_target(target.target_id).state
            is ReplicationTargetState.CONFLICT
        )
    finally:
        database.stop()


def test_bundle_commit_identity_must_match_canonical_local_history(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, _commit_id = _commit(database, actor_id, 1)
        wrong = _bundle(
            commit_id=uuid.uuid4(),
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            wrong,
            commit_seq=commit_seq,
            previous_hash=None,
        )

        with pytest.raises(
            StructuredReplicationPublicationError,
            match="identity does not match local commit history",
        ):
            StructuredReplicationPublisher(repository).publish_staged_bundle(
                target.target_id,
                wrong,
            )

        assert not target_root.exists()
        assert (
            repository.get_target(target.target_id).state
            is ReplicationTargetState.PENDING
        )
    finally:
        database.stop()


def test_concurrent_confirmation_of_same_bundle_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )
        real_confirm = repository.confirm_commit

        def concurrent_confirm(
            target_id: uuid.UUID,
            *,
            commit_seq: int,
            head_hash: str,
            now_us: int | None = None,
        ) -> None:
            real_confirm(
                target_id,
                commit_seq=commit_seq,
                head_hash=head_hash,
                now_us=now_us,
            )
            raise StructuredReplicationInvariantError(
                "simulated losing confirmer"
            )

        monkeypatch.setattr(repository, "confirm_commit", concurrent_confirm)

        confirmed = StructuredReplicationPublisher(repository).publish_staged_bundle(
            target.target_id,
            bundle,
        )

        assert confirmed.state is ReplicationTargetState.ACTIVE
        assert confirmed.confirmed_commit_seq == commit_seq
        assert confirmed.confirmed_head_hash == bundle.bundle_hash
        assert (
            repository.get_commit(target.target_id, commit_seq).state
            is ReplicationCommitState.VERIFIED
        )
    finally:
        database.stop()


def test_current_remote_head_is_verified_before_extending_history(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        first_seq, first_id = _commit(database, actor_id, 1)
        first = _bundle(
            commit_id=first_id,
            commit_seq=first_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            first,
            commit_seq=first_seq,
            previous_hash=None,
        )
        publisher = StructuredReplicationPublisher(repository)
        publisher.publish_staged_bundle(target.target_id, first)

        commits_dir, _manifest_dir = _layout(target_root)
        first_path = commits_dir / publication._bundle_name(
            first_seq,
            first.bundle_hash,
        )
        first_path.write_bytes(b"tampered-current-head")

        second_seq, second_id = _commit(database, actor_id, 2)
        second = _bundle(
            commit_id=second_id,
            commit_seq=second_seq,
            previous_hash=first.bundle_hash,
            marker=2,
        )
        _stage(
            repository,
            target.target_id,
            second,
            commit_seq=second_seq,
            previous_hash=first.bundle_hash,
        )
        second_path = commits_dir / publication._bundle_name(
            second_seq,
            second.bundle_hash,
        )

        with pytest.raises(StructuredReplicationConflictError):
            publisher.publish_staged_bundle(target.target_id, second)

        assert not second_path.exists()
        conflicted = repository.get_target(target.target_id)
        assert conflicted.state is ReplicationTargetState.CONFLICT
        assert conflicted.confirmed_commit_seq == first_seq
    finally:
        database.stop()

def test_repository_identity_mismatch_conflicts_before_commit_publication(
    tmp_path: Path,
) -> None:
    database, repository, actor_id = _runtime(tmp_path)
    try:
        target_root = tmp_path / "long-term"
        target = repository.register_target(str(target_root))
        commit_seq, commit_id = _commit(database, actor_id, 1)
        bundle = _bundle(
            commit_id=commit_id,
            commit_seq=commit_seq,
            previous_hash=None,
            marker=1,
        )
        _stage(
            repository,
            target.target_id,
            bundle,
            commit_seq=commit_seq,
            previous_hash=None,
        )

        durable_mkdir(target_root, parents=True, exist_ok=True)
        foreign = publication._canonical_repository_bytes(uuid.uuid4())
        repository_path = target_root / "repository.json"
        durable_publish_new_bytes(repository_path, foreign)

        with pytest.raises(
            StructuredReplicationConflictError,
            match="identity does not match the target",
        ):
            StructuredReplicationPublisher(repository).publish_staged_bundle(
                target.target_id,
                bundle,
            )

        assert repository_path.read_bytes() == foreign
        assert not (target_root / "commits").exists()
        assert (
            repository.get_target(target.target_id).state
            is ReplicationTargetState.CONFLICT
        )
    finally:
        database.stop()

