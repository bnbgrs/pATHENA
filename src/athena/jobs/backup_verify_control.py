"""CONTROL-lane routing contract for durable Deep backup verification."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.backup_verify_registration import BACKUP_VERIFY_DEEP_REGISTRATION
from athena.jobs.backup_verify_worker import DurableBackupDeepVerifyWorker
from athena.jobs.models import JobRecord


class BackupDeepVerifyControlRoutingError(RuntimeError):
    """Raised when Deep verification cannot be routed fail-closed on CONTROL."""


@dataclass(frozen=True, slots=True)
class BackupDeepVerifyControlRoute:
    """Validated CONTROL-lane route for one durable Deep-verify job type."""

    job_type: str
    process_leased: Callable[[JobRecord], JobRecord]


def build_backup_deep_verify_control_route(
    worker: DurableBackupDeepVerifyWorker,
) -> BackupDeepVerifyControlRoute:
    """Expose the existing worker only when its registration remains CONTROL-safe."""
    if not isinstance(worker, DurableBackupDeepVerifyWorker):
        raise TypeError("worker must be a DurableBackupDeepVerifyWorker.")
    if BACKUP_VERIFY_DEEP_REGISTRATION.job_type != BACKUP_VERIFY_DEEP_JOB_TYPE:
        raise BackupDeepVerifyControlRoutingError(
            "Deep-verify registration job type drifted from the durable payload contract."
        )
    if BACKUP_VERIFY_DEEP_REGISTRATION.control_lane_safe is not True:
        raise BackupDeepVerifyControlRoutingError(
            "Deep-verify registration must remain CONTROL-lane safe."
        )
    if BACKUP_VERIFY_DEEP_REGISTRATION.retry_via_backup_create is not False:
        raise BackupDeepVerifyControlRoutingError(
            "Deep-verify CONTROL retries must never route through backup.create."
        )
    return BackupDeepVerifyControlRoute(
        job_type=BACKUP_VERIFY_DEEP_JOB_TYPE,
        process_leased=worker.process_leased,
    )
