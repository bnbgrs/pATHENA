from __future__ import annotations

import argparse
from pathlib import Path

from athena.__main__ import (
    _request_scheduler_child_stop,
    _scheduler_lane_command,
)
from athena.cli.parser import build_parser
from athena.jobs.scheduler import SchedulerLane


class _Input:
    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.flush_calls = 0

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data)

    def flush(self) -> None:
        self.flush_calls += 1


class _Child:
    def __init__(self) -> None:
        self.stdin = _Input()
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode


def test_internal_scheduler_control_flag_is_parseable() -> None:
    args = build_parser().parse_args(
        [
            "job",
            "scheduler-run",
            "--lane",
            "control",
            "--control-stdin",
        ]
    )

    assert args.control_stdin is True


def test_supervisor_lane_command_enables_control_and_parent_watchdog(tmp_path: Path) -> None:
    args = argparse.Namespace(worker="desktop", max_ticks=None)

    command = _scheduler_lane_command(
        args,
        SchedulerLane.CONTROL,
        supervised_child=False,
        started_file=tmp_path / "control.started",
        ready_file=tmp_path / "control.ready",
    )

    assert "--control-stdin" in command
    assert "--supervisor-watchdog" in command


def test_scheduler_child_stop_uses_existing_stdin_pipe() -> None:
    child = _Child()

    requested = _request_scheduler_child_stop(child)  # type: ignore[arg-type]

    assert requested is True
    assert child.stdin.writes == [b"stop\n"]
    assert child.stdin.flush_calls == 1
