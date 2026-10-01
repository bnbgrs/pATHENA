from __future__ import annotations

import argparse
from pathlib import Path
from threading import Event

from athena.__main__ import (
    _request_scheduler_child_stop,
    _scheduler_lane_command,
    _wait_scheduler_child_ready,
)
from athena.cli.parser import build_parser
from athena.jobs.scheduler import SchedulerLane


class _Input:
    def __init__(self, *, write_result: int | None = None) -> None:
        self.writes: list[bytes] = []
        self.flush_calls = 0
        self.write_result = write_result

    def write(self, data: bytes) -> int:
        self.writes.append(data)
        return len(data) if self.write_result is None else self.write_result

    def flush(self) -> None:
        self.flush_calls += 1


class _Child:
    def __init__(self, *, write_result: int | None = None) -> None:
        self.stdin = _Input(write_result=write_result)
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


def test_scheduler_child_stop_rejects_partial_control_write() -> None:
    child = _Child(write_result=2)

    requested = _request_scheduler_child_stop(child)  # type: ignore[arg-type]

    assert requested is False
    assert child.stdin.writes == [b"stop\n"]
    assert child.stdin.flush_calls == 0


def test_scheduler_readiness_wait_honors_owned_stop_before_timeout(
    tmp_path: Path,
) -> None:
    child = _Child()
    stop_event = Event()
    stop_event.set()

    ready = _wait_scheduler_child_ready(
        SchedulerLane.PROVIDER,
        child,  # type: ignore[arg-type]
        tmp_path / "provider.ready",
        timeout_seconds=60.0,
        stop_event=stop_event,
    )

    assert ready is False
