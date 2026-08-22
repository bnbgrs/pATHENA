from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import pytest

from athena.desktop import app as desktop_app
from athena.desktop.api_controller import DesktopApiController


class _Controller:
    def __init__(self) -> None:
        self.refresh_calls = 0

    def refresh(self) -> None:
        self.refresh_calls += 1


class _Supervisor:
    def __init__(self) -> None:
        self.ensure_running_calls = 0

    def ensure_running(self) -> None:
        self.ensure_running_calls += 1


def test_initial_core_refreshes_cover_slow_windows_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scheduled: list[tuple[int, Callable[[], None]]] = []

    class _Timer:
        @staticmethod
        def singleShot(delay_ms: int, callback: Callable[[], None]) -> None:  # noqa: N802
            scheduled.append((delay_ms, callback))

    monkeypatch.setattr(desktop_app, "QTimer", _Timer)
    controller = _Controller()

    desktop_app._schedule_initial_core_refreshes(
        cast(DesktopApiController, cast(Any, controller))
    )

    assert [delay_ms for delay_ms, _callback in scheduled] == [
        250,
        750,
        1_500,
        3_000,
        5_000,
        10_000,
        20_000,
    ]
    assert len(scheduled) == 7

    for _delay_ms, callback in scheduled:
        callback()
    assert controller.refresh_calls == 7


def test_core_refresh_heartbeat_survives_startup_retry_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Timeout:
        def __init__(self) -> None:
            self.callback: Callable[[], None] | None = None

        def connect(self, callback: Callable[[], None]) -> None:
            self.callback = callback

    class _Timer:
        def __init__(self, parent: object) -> None:
            self.parent = parent
            self.timeout = _Timeout()
            self.interval_ms: int | None = None
            self.started = False
            self.stopped = False

        def setInterval(self, interval_ms: int) -> None:  # noqa: N802
            self.interval_ms = interval_ms

        def start(self) -> None:
            self.started = True

        def stop(self) -> None:
            self.stopped = True

    monkeypatch.setattr(desktop_app, "QTimer", _Timer)
    controller = _Controller()

    timer = desktop_app._start_core_refresh_heartbeat(
        cast(DesktopApiController, cast(Any, controller))
    )

    assert timer.parent is controller
    assert timer.interval_ms == 30_000
    assert timer.started is True
    assert timer.timeout.callback is not None

    timer.timeout.callback()
    assert controller.refresh_calls == 1


def test_core_refresh_heartbeat_recovers_child_before_refresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    class _OrderedController(_Controller):
        def refresh(self) -> None:
            events.append("refresh")
            super().refresh()

    class _OrderedSupervisor(_Supervisor):
        def ensure_running(self) -> None:
            events.append("recover")
            super().ensure_running()

    class _Timeout:
        def __init__(self) -> None:
            self.callback: Callable[[], None] | None = None

        def connect(self, callback: Callable[[], None]) -> None:
            self.callback = callback

    class _Timer:
        def __init__(self, parent: object) -> None:
            self.parent = parent
            self.timeout = _Timeout()
            self.interval_ms: int | None = None
            self.started = False

        def setInterval(self, interval_ms: int) -> None:  # noqa: N802
            self.interval_ms = interval_ms

        def start(self) -> None:
            self.started = True

    monkeypatch.setattr(desktop_app, "QTimer", _Timer)
    controller = _OrderedController()
    supervisor = _OrderedSupervisor()

    timer = desktop_app._start_core_refresh_heartbeat(
        cast(DesktopApiController, cast(Any, controller)),
        cast(Any, supervisor),
    )

    assert timer.timeout.callback is not None
    timer.timeout.callback()

    assert events == ["recover", "refresh"]
    assert supervisor.ensure_running_calls == 1
    assert controller.refresh_calls == 1
