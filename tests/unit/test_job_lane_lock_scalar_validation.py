from __future__ import annotations

from pathlib import Path

import pytest

from athena.jobs.lane_lock import SchedulerLaneProcessLock


@pytest.mark.parametrize(
    "lane_name",
    [
        pytest.param(None, id="none"),
        pytest.param(True, id="bool"),
        pytest.param(1, id="integer"),
        pytest.param([], id="list"),
        pytest.param({}, id="mapping"),
    ],
)
def test_lane_lock_rejects_non_text_identity_before_filesystem_access(
    tmp_path: Path,
    lane_name: object,
) -> None:
    parent = tmp_path / "not-created"
    lock_path = parent / "scheduler.lock"

    with pytest.raises(ValueError, match="must be text"):
        SchedulerLaneProcessLock.acquire(
            lock_path,
            lane_name=lane_name,  # type: ignore[arg-type]
        )

    assert not parent.exists()


@pytest.mark.parametrize(
    "lane_name",
    [
        pytest.param("", id="empty"),
        pytest.param(" ", id="space"),
        pytest.param("\t\n", id="whitespace"),
    ],
)
def test_lane_lock_rejects_blank_identity_before_filesystem_access(
    tmp_path: Path,
    lane_name: str,
) -> None:
    parent = tmp_path / "not-created"
    lock_path = parent / "scheduler.lock"

    with pytest.raises(ValueError, match="must not be empty"):
        SchedulerLaneProcessLock.acquire(lock_path, lane_name=lane_name)

    assert not parent.exists()
