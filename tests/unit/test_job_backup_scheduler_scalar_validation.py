from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from athena.jobs.backup import DurableBackupWorker, daily_backup_slot_us


@pytest.mark.parametrize(
    "value",
    [True, False, -1, 1.5, "1", None],
)
def test_daily_backup_slot_rejects_invalid_now_us(value: Any) -> None:
    with pytest.raises((TypeError, ValueError)):
        daily_backup_slot_us(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "value",
    [True, False, -1, 24, 1.5, "3", None],
)
def test_daily_backup_slot_rejects_invalid_quiet_hour(value: Any) -> None:
    with pytest.raises(ValueError):
        daily_backup_slot_us(0, quiet_hour_utc=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("quiet_hour", [0, 3, 23])
def test_daily_backup_slot_accepts_boundary_hours(quiet_hour: int) -> None:
    assert daily_backup_slot_us(86_400_000_000, quiet_hour_utc=quiet_hour) >= 0


@dataclass
class _ExplodingBackup:
    @property
    def database(self) -> Any:
        raise AssertionError("invalid scheduler input must fail before database access")


@pytest.mark.parametrize(
    "field,value",
    [
        ("quiet_hour_utc", True),
        ("quiet_hour_utc", False),
        ("quiet_hour_utc", -1),
        ("quiet_hour_utc", 24),
        ("quiet_hour_utc", 3.0),
        ("retry_seconds", True),
        ("retry_seconds", False),
        ("retry_seconds", 0),
        ("retry_seconds", -1),
        ("retry_seconds", 1.0),
        ("lease_extension_seconds", True),
        ("lease_extension_seconds", False),
        ("lease_extension_seconds", 0),
        ("lease_extension_seconds", -1),
        ("lease_extension_seconds", 1.0),
    ],
)
def test_backup_worker_rejects_invalid_configuration_scalars(
    field: str,
    value: Any,
) -> None:
    kwargs: dict[str, Any] = {
        "jobs": object(),
        "backup": _ExplodingBackup(),
    }
    kwargs[field] = value

    with pytest.raises(ValueError):
        DurableBackupWorker(**kwargs)  # type: ignore[arg-type]


def test_backup_schedule_due_rejects_invalid_timestamp_before_database_access() -> None:
    worker = DurableBackupWorker(
        jobs=object(),  # type: ignore[arg-type]
        backup=_ExplodingBackup(),  # type: ignore[arg-type]
    )

    for value in (True, False, -1, 1.5, "1"):
        with pytest.raises(ValueError):
            worker.schedule_due(now_us=value)  # type: ignore[arg-type]


def test_backup_worker_accepts_valid_scalar_boundaries() -> None:
    worker = DurableBackupWorker(
        jobs=object(),  # type: ignore[arg-type]
        backup=_ExplodingBackup(),  # type: ignore[arg-type]
        quiet_hour_utc=23,
        retry_seconds=1,
        lease_extension_seconds=1,
    )

    assert worker.quiet_hour_utc == 23
    assert worker.retry_seconds == 1
    assert worker.lease_extension_seconds == 1
