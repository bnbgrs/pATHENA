from __future__ import annotations

from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.capabilities import CONTROL_LANE_JOB_TYPES, requires_provider_isolation


def test_backup_deep_verify_is_explicitly_control_lane_safe() -> None:
    assert BACKUP_VERIFY_DEEP_JOB_TYPE in CONTROL_LANE_JOB_TYPES
    assert requires_provider_isolation(BACKUP_VERIFY_DEEP_JOB_TYPE) is False


def test_unknown_backup_maintenance_job_remains_provider_isolated() -> None:
    assert requires_provider_isolation("backup.unknown-maintenance") is True
