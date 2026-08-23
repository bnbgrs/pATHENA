"""Deterministic backup retention policy and planning."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class BackupRetentionPolicy:
    daily: int = 7
    weekly: int = 4
    monthly: int = 12
    yearly: int = 5

    def __post_init__(self) -> None:
        for name, value in (
            ("daily", self.daily),
            ("weekly", self.weekly),
            ("monthly", self.monthly),
            ("yearly", self.yearly),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"Backup retention {name} must be a non-negative integer."
                )


@dataclass(frozen=True, slots=True)
class BackupTargetRecord:
    target_id: uuid.UUID
    root_path: Path
    status: str
    policy: BackupRetentionPolicy
    identity_initialized: bool
    created_at_us: int
    last_successful_backup_at_us: int | None
    last_verified_at_us: int | None
    deletion_ledger_watermark: int = 0
    deletion_sync_pending: bool = False


@dataclass(frozen=True, slots=True)
class RetentionCandidate:
    snapshot_id: uuid.UUID
    completed_at_us: int


@dataclass(frozen=True, slots=True)
class BackupRetentionPlan:
    target_id: uuid.UUID
    keep_snapshot_ids: tuple[uuid.UUID, ...]
    prune_snapshot_ids: tuple[uuid.UUID, ...]


@dataclass(frozen=True, slots=True)
class BackupRetentionResult:
    plan: BackupRetentionPlan
    pruned_snapshot_ids: tuple[uuid.UUID, ...]
    deleted_object_count: int


def plan_retention(
    *,
    target_id: uuid.UUID,
    snapshots: tuple[RetentionCandidate, ...],
    policy: BackupRetentionPolicy,
) -> BackupRetentionPlan:
    validated_target_id = _uuid_value(target_id, "Backup retention target_id")
    validated_policy = _retention_policy(policy)
    validated_snapshots = _retention_candidates(snapshots)

    ordered = sorted(
        validated_snapshots,
        key=lambda item: (
            item.completed_at_us,
            item.snapshot_id.int,
        ),
        reverse=True,
    )

    if not ordered:
        return BackupRetentionPlan(
            target_id=validated_target_id,
            keep_snapshot_ids=(),
            prune_snapshot_ids=(),
        )

    keep: set[uuid.UUID] = {ordered[0].snapshot_id}

    def stamp(item: RetentionCandidate) -> datetime:
        seconds = item.completed_at_us // 1_000_000
        try:
            return datetime.fromtimestamp(seconds, tz=UTC)
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError(
                "Backup retention completed_at_us is outside the supported datetime range."
            ) from exc

    def retain_slots(limit: int, kind: str) -> None:
        if limit <= 0:
            return

        seen: set[object] = set()

        for item in ordered:
            value = stamp(item)

            if kind == "daily":
                bucket: object = (
                    value.year,
                    value.month,
                    value.day,
                )
            elif kind == "weekly":
                iso = value.isocalendar()
                bucket = (
                    iso.year,
                    iso.week,
                )
            elif kind == "monthly":
                bucket = (
                    value.year,
                    value.month,
                )
            elif kind == "yearly":
                bucket = value.year
            else:
                raise AssertionError(kind)

            if bucket in seen:
                continue

            if len(seen) >= limit:
                continue

            seen.add(bucket)
            keep.add(item.snapshot_id)

    retain_slots(validated_policy.daily, "daily")
    retain_slots(validated_policy.weekly, "weekly")
    retain_slots(validated_policy.monthly, "monthly")
    retain_slots(validated_policy.yearly, "yearly")

    keep_ordered = tuple(
        item.snapshot_id
        for item in ordered
        if item.snapshot_id in keep
    )
    prune_ordered = tuple(
        item.snapshot_id
        for item in ordered
        if item.snapshot_id not in keep
    )

    return BackupRetentionPlan(
        target_id=validated_target_id,
        keep_snapshot_ids=keep_ordered,
        prune_snapshot_ids=prune_ordered,
    )


def _retention_policy(value: object) -> BackupRetentionPolicy:
    if not isinstance(value, BackupRetentionPolicy):
        raise ValueError("Backup retention policy must be a BackupRetentionPolicy value.")
    return value


def _retention_candidates(value: object) -> tuple[RetentionCandidate, ...]:
    if not isinstance(value, tuple):
        raise ValueError("Backup retention snapshots must be a tuple of RetentionCandidate values.")

    seen: set[uuid.UUID] = set()
    validated: list[RetentionCandidate] = []

    for item in value:
        if not isinstance(item, RetentionCandidate):
            raise ValueError(
                "Backup retention snapshots must contain RetentionCandidate values only."
            )
        snapshot_id = _uuid_value(
            item.snapshot_id,
            "Backup retention snapshot_id",
        )
        completed_at_us = _nonnegative_int(
            item.completed_at_us,
            "Backup retention completed_at_us",
        )
        if snapshot_id in seen:
            raise ValueError("Backup retention snapshots must have unique snapshot identities.")
        seen.add(snapshot_id)
        validated.append(
            RetentionCandidate(
                snapshot_id=snapshot_id,
                completed_at_us=completed_at_us,
            )
        )

    return tuple(validated)


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _uuid_value(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise ValueError(f"{label} must be a UUID value.")
    return value
