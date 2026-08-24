"""Time primitives used by persistent ATHENA state."""

from __future__ import annotations

import time

_SQLITE_SIGNED_INT64_MAX = (1 << 63) - 1


def utc_now_us() -> int:
    """Return persistence-safe Unix epoch time in integer microseconds."""
    value = time.time_ns() // 1_000
    if not 0 <= value <= _SQLITE_SIGNED_INT64_MAX:
        raise RuntimeError(
            "System clock is outside ATHENA's persistent SQLite timestamp range."
        )
    return value
