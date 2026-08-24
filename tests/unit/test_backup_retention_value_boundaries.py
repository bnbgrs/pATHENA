from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.backup.retention import (
    BackupRetentionPlan,
    BackupRetentionPolicy,
    BackupRetentionResult,
    BackupTargetRecord,
    RetentionCandidate,
)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def test_retention_candidate_rejects_bool_timestamp() -> None:
    with pytest.raises(ValueError, match="completed_at_us must be a non-negative integer"):
        RetentionCandidate(snapshot_id=_uuid(), completed_at_us=True)


def test_backup_target_rejects_non_path_root() -> None:
    with pytest.raises(ValueError, match="root_path must be a Path"):
        BackupTargetRecord(
            target_id=_uuid(),
            root_path="/tmp/backup",  # type: ignore[arg-type]
            status="ready",
            policy=BackupRetentionPolicy(),
            identity_initialized=True,
            created_at_us=0,
            last_successful_backup_at_us=None,
            last_verified_at_us=None,
        )


def test_backup_target_rejects_bool_deletion_watermark() -> None:
    with pytest.raises(ValueError, match="deletion_ledger_watermark"):
        BackupTargetRecord(
            target_id=_uuid(),
            root_path=Path("backup"),
            status="ready",
            policy=BackupRetentionPolicy(),
            identity_initialized=True,
            created_at_us=0,
            last_successful_backup_at_us=None,
            last_verified_at_us=None,
            deletion_ledger_watermark=True,
        )


def test_retention_plan_rejects_duplicate_keep_ids() -> None:
    snapshot_id = _uuid()
    with pytest.raises(ValueError, match="duplicate UUID"):
        BackupRetentionPlan(
            target_id=_uuid(),
            keep_snapshot_ids=(snapshot_id, snapshot_id),
            prune_snapshot_ids=(),
        )


def test_retention_plan_rejects_keep_prune_overlap() -> None:
    snapshot_id = _uuid()
    with pytest.raises(ValueError, match="must not overlap"):
        BackupRetentionPlan(
            target_id=_uuid(),
            keep_snapshot_ids=(snapshot_id,),
            prune_snapshot_ids=(snapshot_id,),
        )


def test_retention_result_rejects_snapshot_outside_prune_plan() -> None:
    planned = _uuid()
    unexpected = _uuid()
    plan = BackupRetentionPlan(
        target_id=_uuid(),
        keep_snapshot_ids=(),
        prune_snapshot_ids=(planned,),
    )
    with pytest.raises(ValueError, match="outside the prune plan"):
        BackupRetentionResult(
            plan=plan,
            pruned_snapshot_ids=(unexpected,),
            deleted_object_count=0,
        )


def test_retention_result_rejects_bool_deleted_object_count() -> None:
    plan = BackupRetentionPlan(
        target_id=_uuid(),
        keep_snapshot_ids=(),
        prune_snapshot_ids=(),
    )
    with pytest.raises(ValueError, match="deleted_object_count"):
        BackupRetentionResult(
            plan=plan,
            pruned_snapshot_ids=(),
            deleted_object_count=True,
        )


def test_valid_retention_value_objects_remain_constructible() -> None:
    snapshot_id = _uuid()
    candidate = RetentionCandidate(snapshot_id=snapshot_id, completed_at_us=1)
    plan = BackupRetentionPlan(
        target_id=_uuid(),
        keep_snapshot_ids=(snapshot_id,),
        prune_snapshot_ids=(),
    )
    result = BackupRetentionResult(
        plan=plan,
        pruned_snapshot_ids=(),
        deleted_object_count=0,
    )
    assert candidate.snapshot_id == snapshot_id
    assert result.plan is plan
