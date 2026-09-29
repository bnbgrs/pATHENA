"""Fail-closed recovery preflight for application updates."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from athena.backup.service import BackupService, BackupSnapshotRecord
from athena.update.manifest import UpdateManifest, UpdateVerificationError


@dataclass(frozen=True, slots=True)
class UpdateRecoveryPoint:
    """Deep-verified restore point required before an update may switch."""

    snapshot_id: uuid.UUID
    target_id: uuid.UUID
    snapshot_commit_seq: int
    schema_version: int


def prepare_update_recovery_point(
    *,
    backup: BackupService,
    manifest: UpdateManifest,
    target_root: Path | None = None,
    target_id: uuid.UUID | None = None,
) -> UpdateRecoveryPoint:
    """Create and deep-verify a schema-compatible recovery point.

    This function deliberately performs no package installation or runtime
    switch. Callers must treat successful return as a prerequisite for those
    later operations.
    """
    snapshot = backup.create_snapshot(
        target_root=target_root,
        target_id=target_id,
    )
    _require_snapshot_compatible(snapshot, manifest)

    verified = backup.verify_deep(snapshot.snapshot_id)
    _require_same_snapshot(snapshot, verified)
    _require_snapshot_compatible(verified, manifest)

    if verified.verification_status != "verified_deep":
        raise UpdateVerificationError(
            "Update recovery snapshot did not complete Deep verification."
        )
    if verified.last_verified_at_us is None:
        raise UpdateVerificationError(
            "Update recovery snapshot has no persisted verification timestamp."
        )

    assert verified.snapshot_commit_seq is not None
    assert verified.schema_version is not None
    return UpdateRecoveryPoint(
        snapshot_id=verified.snapshot_id,
        target_id=verified.target_id,
        snapshot_commit_seq=verified.snapshot_commit_seq,
        schema_version=verified.schema_version,
    )


def _require_snapshot_compatible(
    snapshot: BackupSnapshotRecord,
    manifest: UpdateManifest,
) -> None:
    if snapshot.state != "complete" or snapshot.pruned_at_us is not None:
        raise UpdateVerificationError(
            "Update recovery snapshot is not an active completed restore point."
        )
    if snapshot.snapshot_commit_seq is None:
        raise UpdateVerificationError(
            "Update recovery snapshot has no durable commit sequence."
        )
    if snapshot.schema_version is None:
        raise UpdateVerificationError(
            "Update recovery snapshot has no recorded schema version."
        )
    if not manifest.supports_schema(snapshot.schema_version):
        raise UpdateVerificationError(
            "Update package does not support the recovery snapshot schema."
        )


def _require_same_snapshot(
    created: BackupSnapshotRecord,
    verified: BackupSnapshotRecord,
) -> None:
    if (
        verified.snapshot_id != created.snapshot_id
        or verified.target_id != created.target_id
        or verified.relative_path != created.relative_path
        or verified.snapshot_commit_seq != created.snapshot_commit_seq
        or verified.schema_version != created.schema_version
        or verified.manifest_sha256 != created.manifest_sha256
    ):
        raise UpdateVerificationError(
            "Update recovery snapshot identity changed during verification."
        )
