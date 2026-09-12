"""Deterministic missed-run policy for durable scheduled jobs."""

from __future__ import annotations

from enum import Enum
from typing import Iterable


class MissedRunPolicy(str, Enum):
    """Supported policies for schedule occurrences missed while ATHENA was offline."""

    SKIP = "skip"
    RUN_ONCE = "run_once"
    BACKFILL_ALL = "backfill_all"
    BACKFILL_BOUNDED = "backfill_bounded"


def _timestamp_us(value: object, *, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer microsecond timestamp.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")
    return value


def _canonical_occurrences(values: Iterable[int]) -> tuple[int, ...]:
    occurrences = tuple(
        _timestamp_us(value, field_name="scheduled occurrence") for value in values
    )
    if any(left >= right for left, right in zip(occurrences, occurrences[1:])):
        raise ValueError("Scheduled occurrences must be strictly increasing and unique.")
    return occurrences


def select_missed_occurrences(
    occurrences_us: Iterable[int],
    *,
    now_us: int,
    policy: MissedRunPolicy,
    max_backfill: int | None = None,
) -> tuple[int, ...]:
    """Select due occurrences that should become durable job instances.

    The caller supplies canonical UTC occurrence timestamps that have not yet produced
    a job instance. This function is intentionally persistence-agnostic: it decides
    only which missed occurrences a durable scheduler should materialize.
    """

    now = _timestamp_us(now_us, field_name="now_us")
    try:
        normalized_policy = MissedRunPolicy(policy)
    except (TypeError, ValueError) as exc:
        raise ValueError("Unsupported missed-run policy.") from exc

    occurrences = _canonical_occurrences(occurrences_us)
    due = tuple(occurrence for occurrence in occurrences if occurrence <= now)

    if normalized_policy is MissedRunPolicy.BACKFILL_BOUNDED:
        if isinstance(max_backfill, bool) or not isinstance(max_backfill, int):
            raise TypeError("backfill_bounded requires an integer max_backfill.")
        if max_backfill < 1:
            raise ValueError("backfill_bounded max_backfill must be >= 1.")
        return due[:max_backfill]

    if max_backfill is not None:
        raise ValueError("max_backfill is only valid for backfill_bounded.")

    if normalized_policy is MissedRunPolicy.SKIP:
        return ()
    if normalized_policy is MissedRunPolicy.RUN_ONCE:
        return due[-1:] if due else ()
    return due
