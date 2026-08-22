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
