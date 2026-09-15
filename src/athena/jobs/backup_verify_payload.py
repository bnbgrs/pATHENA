"""Strict durable payload contract for periodic Deep backup verification."""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

BACKUP_VERIFY_DEEP_JOB_TYPE = "backup.verify_deep"
BACKUP_VERIFY_DEEP_PIPELINE_VERSION = "backup-deep-verify-v1"


class BackupDeepVerifyPayloadError(ValueError):
    """Raised when a durable Deep-verify payload is malformed or ambiguous."""


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyPayload:
    """Validated immutable payload for one scheduled Deep verification occurrence."""

    snapshot_id: uuid.UUID
    occurrence_slot_us: int

    @property
    def requested_scope(self) -> dict[str, object]:
        return {
            "snapshot_id": str(self.snapshot_id),
            "occurrence_slot_us": self.occurrence_slot_us,
        }

    @property
    def pinned_configuration(self) -> dict[str, object]:
        return {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION}


def build_backup_deep_verify_payload(
    *,
    snapshot_id: uuid.UUID,
    occurrence_slot_us: int,
) -> BackupDeepVerifyPayload:
    """Build one validated payload without creating or mutating durable work."""
    if not isinstance(snapshot_id, uuid.UUID):
        raise TypeError("snapshot_id must be a UUID.")
    occurrence = _nonnegative_int(occurrence_slot_us, label="occurrence_slot_us")
    return BackupDeepVerifyPayload(
        snapshot_id=snapshot_id,
        occurrence_slot_us=occurrence,
    )


def validate_backup_deep_verify_payload(
    *,
    requested_scope: Mapping[str, Any] | None,
    pinned_configuration: Mapping[str, Any] | None,
) -> BackupDeepVerifyPayload:
    """Validate persisted Deep-verify payloads fail-closed with exact keys."""
    _require_exact_keys(
        requested_scope,
        {"snapshot_id", "occurrence_slot_us"},
        label="backup.verify_deep requested_scope",
    )
    _require_exact_keys(
        pinned_configuration,
        {"pipeline_version"},
        label="backup.verify_deep pinned_configuration",
    )
    assert requested_scope is not None
    assert pinned_configuration is not None

    snapshot_id = _canonical_uuid_text(
        requested_scope.get("snapshot_id"),
        label="snapshot_id",
    )
    occurrence_slot_us = _nonnegative_int(
        requested_scope.get("occurrence_slot_us"),
        label="occurrence_slot_us",
    )
    pipeline_version = pinned_configuration.get("pipeline_version")
    if pipeline_version != BACKUP_VERIFY_DEEP_PIPELINE_VERSION:
        raise BackupDeepVerifyPayloadError(
            "backup.verify_deep pipeline_version must match the durable contract."
        )

    return BackupDeepVerifyPayload(
        snapshot_id=snapshot_id,
        occurrence_slot_us=occurrence_slot_us,
    )


def _require_exact_keys(
    value: Mapping[str, Any] | None,
    expected: set[str],
    *,
    label: str,
) -> None:
    if not isinstance(value, Mapping):
        raise BackupDeepVerifyPayloadError(f"{label} must be an object.")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise BackupDeepVerifyPayloadError(
            f"{label} keys mismatch; missing={missing}, extra={extra}."
        )


def _canonical_uuid_text(value: object, *, label: str) -> uuid.UUID:
    if not isinstance(value, str):
        raise BackupDeepVerifyPayloadError(f"{label} must be a UUID string.")
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise BackupDeepVerifyPayloadError(f"{label} must be a valid UUID.") from exc
    if str(parsed) != value:
        raise BackupDeepVerifyPayloadError(f"{label} must use canonical UUID text.")
    return parsed


def _nonnegative_int(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BackupDeepVerifyPayloadError(
            f"{label} must be a non-negative integer."
        )
    return value
