from __future__ import annotations

import uuid

import pytest

from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
    BackupDeepVerifyPayloadError,
    build_backup_deep_verify_payload,
    validate_backup_deep_verify_payload,
)


def _valid() -> tuple[dict[str, object], dict[str, object], uuid.UUID]:
    snapshot_id = uuid.uuid4()
    return (
        {
            "snapshot_id": str(snapshot_id),
            "occurrence_slot_us": 123_000_000,
        },
        {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION},
        snapshot_id,
    )


def test_build_and_validate_round_trip() -> None:
    snapshot_id = uuid.uuid4()
    built = build_backup_deep_verify_payload(
        snapshot_id=snapshot_id,
        occurrence_slot_us=0,
    )
    validated = validate_backup_deep_verify_payload(
        requested_scope=built.requested_scope,
        pinned_configuration=built.pinned_configuration,
    )
    assert validated == built


@pytest.mark.parametrize(
    "scope",
    [
        None,
        {},
        {"snapshot_id": str(uuid.uuid4())},
        {
            "snapshot_id": str(uuid.uuid4()),
            "occurrence_slot_us": 1,
            "target_id": str(uuid.uuid4()),
        },
    ],
)
def test_scope_requires_exact_keys(scope) -> None:
    _, config, _ = _valid()
    with pytest.raises(BackupDeepVerifyPayloadError):
        validate_backup_deep_verify_payload(
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize("occurrence", [True, -1, 1.5, "1"])
def test_occurrence_slot_rejects_non_integer_or_negative_values(occurrence) -> None:
    scope, config, _ = _valid()
    scope["occurrence_slot_us"] = occurrence
    with pytest.raises(BackupDeepVerifyPayloadError):
        validate_backup_deep_verify_payload(
            requested_scope=scope,
            pinned_configuration=config,
        )


def test_snapshot_id_requires_canonical_uuid_text() -> None:
    scope, config, snapshot_id = _valid()
    scope["snapshot_id"] = str(snapshot_id).upper()
    with pytest.raises(BackupDeepVerifyPayloadError):
        validate_backup_deep_verify_payload(
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize(
    "config",
    [
        None,
        {},
        {"pipeline_version": "backup-deep-verify-v0"},
        {
            "pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
            "retry": True,
        },
    ],
)
def test_configuration_is_exact_and_version_pinned(config) -> None:
    scope, _, _ = _valid()
    with pytest.raises(BackupDeepVerifyPayloadError):
        validate_backup_deep_verify_payload(
            requested_scope=scope,
            pinned_configuration=config,
        )


def test_builder_rejects_bool_occurrence_and_non_uuid_snapshot() -> None:
    snapshot_id = uuid.uuid4()
    with pytest.raises(BackupDeepVerifyPayloadError):
        build_backup_deep_verify_payload(
            snapshot_id=snapshot_id,
            occurrence_slot_us=True,
        )
    with pytest.raises(TypeError):
        build_backup_deep_verify_payload(
            snapshot_id=str(snapshot_id),  # type: ignore[arg-type]
            occurrence_slot_us=0,
        )
