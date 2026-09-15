from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

import pytest

import athena.jobs.backup_verify_control as control_module
from athena.jobs.backup_verify_control import (
    BackupDeepVerifyControlRoutingError,
    build_backup_deep_verify_control_route,
)
from athena.jobs.backup_verify_payload import BACKUP_VERIFY_DEEP_JOB_TYPE
from athena.jobs.backup_verify_worker import DurableBackupDeepVerifyWorker


def _worker() -> DurableBackupDeepVerifyWorker:
    return DurableBackupDeepVerifyWorker(jobs=Mock(), backup=Mock())


def test_control_route_exposes_existing_worker_without_execution() -> None:
    worker = _worker()

    route = build_backup_deep_verify_control_route(worker)

    assert route.job_type == BACKUP_VERIFY_DEEP_JOB_TYPE
    assert route.process_leased == worker.process_leased
    worker.jobs.acquire.assert_not_called()
    worker.backup.verify_deep.assert_not_called()


def test_control_route_rejects_wrong_worker_type() -> None:
    with pytest.raises(TypeError, match="DurableBackupDeepVerifyWorker"):
        build_backup_deep_verify_control_route(Mock())  # type: ignore[arg-type]


def test_control_route_fails_closed_if_control_safety_drifts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsafe = replace(control_module.BACKUP_VERIFY_DEEP_REGISTRATION, control_lane_safe=False)
    monkeypatch.setattr(control_module, "BACKUP_VERIFY_DEEP_REGISTRATION", unsafe)

    with pytest.raises(BackupDeepVerifyControlRoutingError, match="CONTROL-lane safe"):
        build_backup_deep_verify_control_route(_worker())


def test_control_route_fails_closed_if_backup_create_retry_is_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unsafe = replace(control_module.BACKUP_VERIFY_DEEP_REGISTRATION, retry_via_backup_create=True)
    monkeypatch.setattr(control_module, "BACKUP_VERIFY_DEEP_REGISTRATION", unsafe)

    with pytest.raises(BackupDeepVerifyControlRoutingError, match="backup.create"):
        build_backup_deep_verify_control_route(_worker())
