from __future__ import annotations

import sys

import pytest

from athena.storage.wal_maintenance import (
    WalMaintenanceError,
    WalMaintenanceOrchestrator,
)
from athena.storage.wal_schedule import WalMaintenanceIntervalRunner


class _NoSideEffectOrchestrator(WalMaintenanceOrchestrator):
    def __init__(self) -> None:
        pass

    def run_cycle(self):  # type: ignore[no-untyped-def]
        raise AssertionError("WAL maintenance must not run before deadline validation")


def test_deadline_overflow_fails_before_wal_side_effect() -> None:
    runner = WalMaintenanceIntervalRunner(
        _NoSideEffectOrchestrator(),
        interval_seconds=sys.float_info.max,
    )

    with pytest.raises(
        WalMaintenanceError,
        match="next due monotonic time must remain finite",
    ):
        runner.run_due(now_monotonic=sys.float_info.max)

    assert runner.next_due_monotonic is None
