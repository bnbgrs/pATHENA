from __future__ import annotations

from pathlib import Path

import pytest

from athena.jobs.lane_lock import SchedulerLaneOwnershipError, SchedulerLaneProcessLock


def _symlink_directory(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"Directory symlink unavailable: {exc}")


def test_lane_lock_rejects_symlink_ancestor(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_directory(link, real)

    with pytest.raises(SchedulerLaneOwnershipError, match="symlink ancestor"):
        SchedulerLaneProcessLock.acquire(
            link / "locks" / "scheduler.lock",
            lane_name="test",
        )

    assert not (real / "locks").exists()


def test_lane_lock_file_has_owner_only_permissions_on_posix(tmp_path: Path) -> None:
    lock_path = tmp_path / "scheduler.lock"
    lock = SchedulerLaneProcessLock.acquire(lock_path, lane_name="test")
    try:
        assert lock_path.exists()
    finally:
        lock.close()
