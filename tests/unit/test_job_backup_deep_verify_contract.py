from __future__ import annotations

import uuid

import pytest

from athena.jobs.backup_verify_worker import BACKUP_DEEP_VERIFY_JOB_TYPE
from athena.jobs.payload_validation import (
    BuiltinJobPayloadValidationError,
    validate_builtin_job_payload,
)
from athena.jobs.service import DurableJobService

_SNAPSHOT_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
_TARGET_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")


def _scope() -> dict[str, object]:
    return {
        "occurrence_slot_us": 0,
        "snapshot_id": str(_SNAPSHOT_ID),
        "target_id": str(_TARGET_ID),
    }


def _config() -> dict[str, object]:
    return {
        "interval_seconds": 7 * 24 * 60 * 60,
        "pipeline_version": "backup-deep-verify-v1",
    }


def test_deep_verify_job_type_is_registered() -> None:
    assert BACKUP_DEEP_VERIFY_JOB_TYPE in DurableJobService.BUILTIN_JOB_TYPES


def test_deep_verify_payload_accepts_canonical_contract() -> None:
    validate_builtin_job_payload(
        BACKUP_DEEP_VERIFY_JOB_TYPE,
        requested_scope=_scope(),
        pinned_configuration=_config(),
    )


@pytest.mark.parametrize(
    ("scope_mutation", "config_mutation"),
    [
        ({"unexpected": True}, {}),
        ({"snapshot_id": str(_SNAPSHOT_ID).upper()}, {}),
        ({"target_id": str(_TARGET_ID).upper()}, {}),
        ({"occurrence_slot_us": -1}, {}),
        ({"occurrence_slot_us": True}, {}),
        ({}, {"interval_seconds": 0}),
        ({}, {"interval_seconds": True}),
        ({}, {"pipeline_version": "backup-deep-verify-v2"}),
        ({}, {"unexpected": True}),
    ],
)
def test_deep_verify_payload_rejects_noncanonical_contract(
    scope_mutation: dict[str, object],
    config_mutation: dict[str, object],
) -> None:
    scope = _scope()
    scope.update(scope_mutation)
    config = _config()
    config.update(config_mutation)

    with pytest.raises(BuiltinJobPayloadValidationError):
        validate_builtin_job_payload(
            BACKUP_DEEP_VERIFY_JOB_TYPE,
            requested_scope=scope,
            pinned_configuration=config,
        )
