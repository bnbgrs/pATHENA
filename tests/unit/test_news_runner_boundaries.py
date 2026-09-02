from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import pytest

from athena.news.runner import NewsRunner


@dataclass
class _Scheduler:
    actions: list[str]
    calls: list[str] = field(default_factory=list)

    def tick(self, *, worker_id: str) -> Any:
        self.calls.append(worker_id)
        action = self.actions.pop(0)
        return SimpleNamespace(idle=action == "idle", action=action)


@dataclass
class _News:
    starts: int = 0

    def start(self) -> None:
        self.starts += 1


def _runner(actions: list[str]) -> tuple[NewsRunner, _Scheduler, _News]:
    scheduler = _Scheduler(actions=list(actions))
    app = SimpleNamespace(job_scheduler=scheduler)
    news = _News()
    runner = NewsRunner(app, service=news)  # type: ignore[arg-type]
    return runner, scheduler, news


def test_bounded_idle_run_does_not_sleep_after_final_tick(monkeypatch: pytest.MonkeyPatch) -> None:
    runner, scheduler, news = _runner(["idle"])
    sleeps: list[float] = []
    monkeypatch.setattr("athena.news.runner.time.sleep", sleeps.append)

    assert runner.run(max_ticks=1, idle_sleep_seconds=0.25) == 1
    assert scheduler.calls == ["news-runner"]
    assert news.starts == 1
    assert sleeps == []


def test_bounded_idle_run_sleeps_only_between_remaining_ticks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner, scheduler, _ = _runner(["idle", "idle", "idle"])
    sleeps: list[float] = []
    monkeypatch.setattr("athena.news.runner.time.sleep", sleeps.append)

    assert runner.run(max_ticks=3, idle_sleep_seconds=0.5) == 3
    assert scheduler.calls == ["news-runner", "news-runner", "news-runner"]
    assert sleeps == [0.5, 0.5]


def test_non_idle_bounded_run_never_sleeps(monkeypatch: pytest.MonkeyPatch) -> None:
    runner, _, _ = _runner(["completed", "waiting"])
    sleeps: list[float] = []
    monkeypatch.setattr("athena.news.runner.time.sleep", sleeps.append)

    assert runner.run(max_ticks=2, idle_sleep_seconds=0.5) == 2
    assert sleeps == []
