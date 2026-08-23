from __future__ import annotations

import uuid
from typing import Any, cast

import pytest

from athena.backup.retention import (
    BackupRetentionPolicy,
    RetentionCandidate,
    plan_retention,
)

TARGET_ID = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
SNAPSHOT_ID = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")


def _candidate(
    *,
    snapshot_id: object = SNAPSHOT_ID,
    completed_at_us: object = 1_000_000,
) -> RetentionCandidate:
    return RetentionCandidate(
        snapshot_id=cast(Any, snapshot_id),
        completed_at_us=cast(Any, completed_at_us),
    )


def test_retention_rejects_invalid_target_identity() -> None:
    with pytest.raises(ValueError, match="target_id"):
        plan_retention(
            target_id=cast(Any, str(TARGET_ID)),
            snapshots=(),
            policy=BackupRetentionPolicy(),
        )


@pytest.mark.parametrize(
    "snapshots",
    [
        pytest.param([], id="list"),
        pytest.param([_candidate()], id="candidate-list"),
        pytest.param("not-snapshots", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_retention_requires_tuple_container(snapshots: object) -> None:
    with pytest.raises(ValueError, match="tuple"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=cast(Any, snapshots),
            policy=BackupRetentionPolicy(),
        )


def test_retention_rejects_foreign_candidate_object() -> None:
    with pytest.raises(ValueError, match="RetentionCandidate"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=cast(Any, (object(),)),
            policy=BackupRetentionPolicy(),
        )


@pytest.mark.parametrize(
    "snapshot_id",
    [
        pytest.param(str(SNAPSHOT_ID), id="text"),
        pytest.param(SNAPSHOT_ID.bytes, id="bytes"),
        pytest.param(None, id="none"),
    ],
)
def test_retention_rejects_non_uuid_snapshot_identity(snapshot_id: object) -> None:
    with pytest.raises(ValueError, match="snapshot_id"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=(_candidate(snapshot_id=snapshot_id),),
            policy=BackupRetentionPolicy(),
        )


@pytest.mark.parametrize(
    "completed_at_us",
    [
        pytest.param(True, id="true"),
        pytest.param(False, id="false"),
        pytest.param(-1, id="negative"),
        pytest.param(1.5, id="float"),
        pytest.param("1", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_retention_rejects_invalid_completion_timestamp(completed_at_us: object) -> None:
    with pytest.raises(ValueError, match="completed_at_us"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=(_candidate(completed_at_us=completed_at_us),),
            policy=BackupRetentionPolicy(),
        )


def test_retention_rejects_duplicate_snapshot_identity() -> None:
    with pytest.raises(ValueError, match="unique snapshot"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=(
                _candidate(completed_at_us=1_000_000),
                _candidate(completed_at_us=2_000_000),
            ),
            policy=BackupRetentionPolicy(),
        )


def test_retention_rejects_non_policy_object() -> None:
    with pytest.raises(ValueError, match="policy"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=(),
            policy=cast(Any, {"daily": 7}),
        )


def test_retention_rejects_timestamp_outside_datetime_range() -> None:
    with pytest.raises(ValueError, match="datetime range"):
        plan_retention(
            target_id=TARGET_ID,
            snapshots=(_candidate(completed_at_us=10**30),),
            policy=BackupRetentionPolicy(daily=1, weekly=0, monthly=0, yearly=0),
        )


def test_retention_accepts_epoch_boundary_and_keeps_newest() -> None:
    snapshot = _candidate(completed_at_us=0)

    plan = plan_retention(
        target_id=TARGET_ID,
        snapshots=(snapshot,),
        policy=BackupRetentionPolicy(daily=0, weekly=0, monthly=0, yearly=0),
    )

    assert plan.target_id == TARGET_ID
    assert plan.keep_snapshot_ids == (SNAPSHOT_ID,)
    assert plan.prune_snapshot_ids == ()
