from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.news.runner import NewsRunner


@dataclass
class _News:
    starts: int = 0

    def start(self) -> None:
        self.starts += 1


@dataclass
class _TickResult:
    idle: bool = False
    action: str = "completed"


@dataclass
class _Scheduler:
    calls: list[str] = field(default_factory=list)

    def tick(self, *, worker_id: str) -> _TickResult:
        self.calls.append(worker_id)
        return _TickResult()


@dataclass
class _App:
    job_scheduler: _Scheduler = field(default_factory=_Scheduler)


def _runner() -> tuple[NewsRunner, _App]:
    app = _App()
    news = _News()
    runner = NewsRunner(app, service=news)  # type: ignore[arg-type]
    assert news.starts == 1
    return runner, app


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "1"])
def test_run_rejects_invalid_max_ticks_before_scheduler(value: Any) -> None:
    runner, app = _runner()

    with pytest.raises(ValueError):
        runner.run(max_ticks=value)  # type: ignore[arg-type]

    assert app.job_scheduler.calls == []


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, float("nan"), float("inf"), float("-inf"), "1"],
)
def test_run_rejects_invalid_idle_sleep_before_scheduler(value: Any) -> None:
    runner, app = _runner()

    with pytest.raises(ValueError):
        runner.run(max_ticks=1, idle_sleep_seconds=value)  # type: ignore[arg-type]

    assert app.job_scheduler.calls == []


@pytest.mark.parametrize("value", [None, True, False, 1, "", " worker "])
def test_tick_rejects_invalid_worker_identity_before_scheduler(value: Any) -> None:
    runner, app = _runner()

    with pytest.raises(ValueError):
        runner.tick(worker_id=value)  # type: ignore[arg-type]

    assert app.job_scheduler.calls == []


def test_run_accepts_positive_integer_tick_bound() -> None:
    runner, app = _runner()

    assert runner.run(max_ticks=2, idle_sleep_seconds=0.25) == 2
    assert app.job_scheduler.calls == ["news-runner", "news-runner"]


def test_tick_accepts_canonical_worker_identity() -> None:
    runner, app = _runner()

    assert runner.tick(worker_id="news-worker-1") == "completed"
    assert app.job_scheduler.calls == ["news-worker-1"]
