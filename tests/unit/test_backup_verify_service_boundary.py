from __future__ import annotations

import uuid

import pytest

from athena.jobs.backup_verify_payload import (
    BACKUP_VERIFY_DEEP_JOB_TYPE,
    BACKUP_VERIFY_DEEP_PIPELINE_VERSION,
)
from athena.jobs.backup_verify_service_boundary import (
    BackupDeepVerifyServiceBoundaryError,
    validate_backup_deep_verify_service_create,
)


def _scope() -> dict[str, object]:
    return {
        "snapshot_id": str(uuid.UUID("12345678-1234-5678-1234-567812345678")),
        "occurrence_slot_us": 1_700_000_000_000_000,
    }


def _configuration() -> dict[str, object]:
    return {"pipeline_version": BACKUP_VERIFY_DEEP_PIPELINE_VERSION}


def test_service_boundary_returns_exact_validated_payload() -> None:
    validated = validate_backup_deep_verify_service_create(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        requested_scope=_scope(),
        pinned_configuration=_configuration(),
    )

    assert validated.requested_scope == _scope()
    assert validated.pinned_configuration == _configuration()


@pytest.mark.parametrize(
    ("job_type", "scope", "configuration"),
    [
        ("backup.create", _scope(), _configuration()),
        (BACKUP_VERIFY_DEEP_JOB_TYPE, None, _configuration()),
        (BACKUP_VERIFY_DEEP_JOB_TYPE, _scope(), None),
        (
            BACKUP_VERIFY_DEEP_JOB_TYPE,
            {**_scope(), "unexpected": True},
            _configuration(),
        ),
        (
            BACKUP_VERIFY_DEEP_JOB_TYPE,
            _scope(),
            {"pipeline_version": "wrong"},
        ),
    ],
)
def test_service_boundary_rejects_unsafe_create_input(
    job_type: str,
    scope: dict[str, object] | None,
    configuration: dict[str, object] | None,
) -> None:
    with pytest.raises(BackupDeepVerifyServiceBoundaryError):
        validate_backup_deep_verify_service_create(
            job_type=job_type,
            requested_scope=scope,
            pinned_configuration=configuration,
        )
