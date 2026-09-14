import uuid

import pytest

from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_PIPELINE_VERSION
from athena.jobs.backup_verify_registration import (
    BACKUP_VERIFY_DEEP_BUILTIN_JOB_TYPES,
    BACKUP_VERIFY_DEEP_REGISTRATION,
    BackupDeepVerifyRegistration,
    BackupDeepVerifyRegistrationError,
)


def _scope(snapshot_id: uuid.UUID) -> dict[str, object]:
    return {"snapshot_id": str(snapshot_id), "occurrence_slot_us": 4_000_000}


def _config() -> dict[str, object]:
    return {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION}


def test_registration_declares_exact_builtin_type_and_control_safety() -> None:
    assert BACKUP_VERIFY_DEEP_BUILTIN_JOB_TYPES == frozenset({"backup.verify_deep"})
    assert BACKUP_VERIFY_DEEP_REGISTRATION.job_type == "backup.verify_deep"
    assert BACKUP_VERIFY_DEEP_REGISTRATION.control_lane_safe is True
    assert BACKUP_VERIFY_DEEP_REGISTRATION.retry_via_backup_create is False


def test_registration_validates_and_normalizes_create_payload() -> None:
    snapshot_id = uuid.uuid4()
    payload = BACKUP_VERIFY_DEEP_REGISTRATION.validate_create_payload(
        requested_scope=_scope(snapshot_id),
        pinned_configuration=_config(),
    )
    assert payload.snapshot_id == snapshot_id
    assert payload.occurrence_slot_us == 4_000_000


@pytest.mark.parametrize(
    ("scope", "config"),
    [
        ({"snapshot_id": str(uuid.uuid4())}, _config()),
        ({"snapshot_id": str(uuid.uuid4()), "occurrence_slot_us": True}, _config()),
        ({"snapshot_id": str(uuid.uuid4()), "occurrence_slot_us": 1, "extra": 1}, _config()),
        (_scope(uuid.uuid4()), {"pipeline_version": "wrong"}),
        (_scope(uuid.uuid4()), {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION, "extra": True}),
    ],
)
def test_registration_rejects_malformed_create_payload(
    scope: dict[str, object],
    config: dict[str, object],
) -> None:
    with pytest.raises(BackupDeepVerifyRegistrationError):
        BACKUP_VERIFY_DEEP_REGISTRATION.validate_create_payload(
            requested_scope=scope,
            pinned_configuration=config,
        )


def test_registration_defaults_are_fail_closed_against_backup_create_retry() -> None:
    registration = BackupDeepVerifyRegistration()
    assert registration.retry_via_backup_create is False
