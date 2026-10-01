from __future__ import annotations

import pytest

from scripts.render_pathena_ui_snapshot_sequential import (
    _PALLAS_VISUAL_CAPTURE_TICKS,
    _advance_pallas_living_capture,
    _pause_pallas_living_capture,
)


class _TimerProbe:
    def __init__(self) -> None:
        self.stop_calls = 0

    def stop(self) -> None:
        self.stop_calls += 1


class _LivingProbe:
    def __init__(self) -> None:
        self._timer = _TimerProbe()
        self.ticks = 0

    def _tick(self) -> None:
        self.ticks += 1


def test_visual_pallas_capture_stops_wall_clock_and_uses_exact_tick_count() -> None:
    living = _LivingProbe()

    _pause_pallas_living_capture(living)
    _advance_pallas_living_capture(living)

    assert living._timer.stop_calls == 1
    assert living.ticks == _PALLAS_VISUAL_CAPTURE_TICKS == 12


def test_visual_pallas_capture_rejects_zero_tick_fixture() -> None:
    living = _LivingProbe()

    with pytest.raises(ValueError, match="at least one deterministic tick"):
        _advance_pallas_living_capture(living, ticks=0)

    assert living.ticks == 0


def test_visual_pallas_capture_fails_closed_without_timer_or_tick() -> None:
    with pytest.raises(RuntimeError, match="cannot control"):
        _pause_pallas_living_capture(object())

    class _TimerOnly:
        _timer = _TimerProbe()

    with pytest.raises(RuntimeError, match="cannot advance"):
        _advance_pallas_living_capture(_TimerOnly())
