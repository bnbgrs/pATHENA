from __future__ import annotations

import pytest

from athena.common import time as time_module
from athena.common.time import utc_now_us


def test_utc_now_us_preserves_integer_microseconds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time_module.time, "time_ns", lambda: 1_787_508_000_123_456_789)

    assert utc_now_us() == 1_787_508_000_123_456


@pytest.mark.parametrize(
    "time_ns",
    [
        -1,
        (((1 << 63) - 1) + 1) * 1_000,
    ],
)
def test_utc_now_us_rejects_values_outside_persistent_sqlite_range(
    monkeypatch: pytest.MonkeyPatch,
    time_ns: int,
) -> None:
    monkeypatch.setattr(time_module.time, "time_ns", lambda: time_ns)

    with pytest.raises(RuntimeError, match="persistent SQLite timestamp range"):
        utc_now_us()
