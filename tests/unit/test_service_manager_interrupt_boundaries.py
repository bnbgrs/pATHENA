from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.core.errors import ShutdownError
from athena.core.services import ServiceManager


@dataclass
class _Service:
    name: str
    events: list[str]
    start_error: BaseException | None = None
    stop_error: BaseException | None = None

    def start(self) -> None:
        self.events.append(f"start:{self.name}")
        if self.start_error is not None:
            raise self.start_error

    def stop(self) -> None:
        self.events.append(f"stop:{self.name}")
        if self.stop_error is not None:
            raise self.stop_error


def test_start_interrupt_rolls_back_already_started_services() -> None:
    events: list[str] = []
    first = _Service("first", events)
    interrupted = _Service("interrupted", events, start_error=KeyboardInterrupt())
    manager = ServiceManager((first, interrupted))

    with pytest.raises(KeyboardInterrupt):
        manager.start_all()

    assert events == ["start:first", "start:interrupted", "stop:first"]
    assert manager.started_service_names == ()


def test_shutdown_interrupt_still_attempts_all_remaining_services() -> None:
    events: list[str] = []
    first = _Service("first", events)
    interrupted = _Service("interrupted", events, stop_error=KeyboardInterrupt())
    manager = ServiceManager((first, interrupted))
    manager.start_all()
    events.clear()

    with pytest.raises(KeyboardInterrupt):
        manager.stop_all()

    assert events == ["stop:interrupted", "stop:first"]
    assert manager.started_service_names == ()


def test_normal_shutdown_failures_remain_aggregated() -> None:
    events: list[str] = []
    first = _Service("first", events, stop_error=RuntimeError("first failed"))
    second = _Service("second", events, stop_error=RuntimeError("second failed"))
    manager = ServiceManager((first, second))
    manager.start_all()
    events.clear()

    with pytest.raises(ShutdownError, match="second, first"):
        manager.stop_all()

    assert events == ["stop:second", "stop:first"]
    assert manager.started_service_names == ()
