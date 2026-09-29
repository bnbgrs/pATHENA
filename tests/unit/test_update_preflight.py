from __future__ import annotations

import hashlib
import uuid
from dataclasses import replace
from unittest.mock import Mock

import pytest

from athena.backup.service import BackupSnapshotRecord
from athena.update.manifest import UpdateChannel, UpdateManifest, UpdateVerificationError
from athena.update.preflight import prepare_update_recovery_point


def _manifest(minimum: int = 40, maximum: int = 41) -> UpdateManifest:
    package = b"package"
    return UpdateManifest(
        channel=UpdateChannel.BETA,
        app_version="0.1.0-beta.1",
        package_name="athena.zip",
        package_size=len(package),
        package_sha256=hashlib.sha256(package).hexdigest(),
        minimum_schema_version=minimum,
        maximum_schema_version=maximum,
    )


def _snapshot() -> BackupSnapshotRecord:
    return BackupSnapshotRecord(
        snapshot_id=uuid.uuid4(),
        target_id=uuid.uuid4(),
        state="complete",
        verification_status="unverified",
        relative_path="snapshots/recovery",
        snapshot_commit_seq=73,
        schema_version=40,
        db_sha256=None,
        manifest_sha256=b"m" * 32,
        object_count=0,
        created_at_us=1,
        completed_at_us=2,
        last_verified_at_us=None,
        pruned_at_us=None,
    )


def test_preflight_requires_deep_verified_same_snapshot() -> None:
    created = _snapshot()
    verified = replace(created, verification_status="verified_deep", last_verified_at_us=3)
    backup = Mock()
    backup.create_snapshot.return_value = created
    backup.verify_deep.return_value = verified

    result = prepare_update_recovery_point(
        backup=backup,
        manifest=_manifest(),
        target_id=created.target_id,
    )

    backup.verify_deep.assert_called_once_with(created.snapshot_id)
    assert result.snapshot_id == created.snapshot_id
    assert result.snapshot_commit_seq == 73


def test_preflight_rejects_incompatible_schema_before_deep_verify() -> None:
    created = _snapshot()
    backup = Mock()
    backup.create_snapshot.return_value = created

    with pytest.raises(UpdateVerificationError, match="does not support"):
        prepare_update_recovery_point(
            backup=backup,
            manifest=_manifest(41, 41),
            target_id=created.target_id,
        )

    backup.verify_deep.assert_not_called()


def test_preflight_rejects_changed_snapshot_identity() -> None:
    created = _snapshot()
    backup = Mock()
    backup.create_snapshot.return_value = created
    backup.verify_deep.return_value = replace(
        created,
        snapshot_id=uuid.uuid4(),
        verification_status="verified_deep",
        last_verified_at_us=3,
    )

    with pytest.raises(UpdateVerificationError, match="identity changed"):
        prepare_update_recovery_point(
            backup=backup,
            manifest=_manifest(),
            target_id=created.target_id,
        )
