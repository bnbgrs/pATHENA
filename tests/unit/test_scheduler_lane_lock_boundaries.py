from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from athena.jobs.lane_lock import (
    SchedulerLaneOwnershipError,
    SchedulerLaneProcessLock,
)


def test_lane_lock_rejects_non_path_before_io() -> None:
    with pytest.raises(ValueError, match="pathlib.Path"):
        SchedulerLaneProcessLock.acquire(  # type: ignore[arg-type]
            "/tmp/lane.lock",
            lane_name="provider",
        )


def test_lane_lock_rejects_empty_lane_name(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        SchedulerLaneProcessLock.acquire(
            tmp_path / "lane.lock",
            lane_name="   ",
        )


def test_lane_lock_rejects_symlink_without_touching_target(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_bytes(b"")
    link = tmp_path / "lane.lock"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation unavailable")

    with pytest.raises(SchedulerLaneOwnershipError, match="must not be a symlink"):
        SchedulerLaneProcessLock.acquire(link, lane_name="provider")

    assert target.read_bytes() == b""


def test_lane_lock_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(real, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")

    with pytest.raises(SchedulerLaneOwnershipError, match="symlink ancestor"):
        SchedulerLaneProcessLock.acquire(
            link / "lane.lock",
            lane_name="provider",
        )


def test_lane_lock_secures_existing_file_permissions_on_posix(tmp_path: Path) -> None:
    if os.name != "posix":
        pytest.skip("POSIX file-mode assertion")

    path = tmp_path / "lane.lock"
    path.write_bytes(b"\0")
    path.chmod(0o666)

    lock = SchedulerLaneProcessLock.acquire(path, lane_name="provider")
    try:
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    finally:
        lock.close()


def test_lane_lock_close_is_idempotent(tmp_path: Path) -> None:
    lock = SchedulerLaneProcessLock.acquire(
        tmp_path / "lane.lock",
        lane_name="provider",
    )

    lock.close()
    lock.close()
