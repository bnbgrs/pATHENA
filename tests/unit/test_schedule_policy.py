from __future__ import annotations

import pytest

from athena.jobs.schedule_policy import MissedRunPolicy, select_missed_occurrences


def test_skip_drops_all_missed_occurrences() -> None:
    assert select_missed_occurrences(
        [10, 20, 30], now_us=30, policy=MissedRunPolicy.SKIP
    ) == ()


def test_run_once_uses_latest_due_occurrence_only() -> None:
    assert select_missed_occurrences(
        [10, 20, 30, 40], now_us=35, policy=MissedRunPolicy.RUN_ONCE
    ) == (30,)


def test_backfill_all_keeps_due_order_and_excludes_future() -> None:
    assert select_missed_occurrences(
        [10, 20, 30, 40], now_us=30, policy=MissedRunPolicy.BACKFILL_ALL
    ) == (10, 20, 30)


def test_backfill_bounded_uses_oldest_due_occurrences_first() -> None:
    assert select_missed_occurrences(
        [10, 20, 30, 40],
        now_us=40,
        policy=MissedRunPolicy.BACKFILL_BOUNDED,
        max_backfill=2,
    ) == (10, 20)


@pytest.mark.parametrize("occurrences", ([20, 10], [10, 10]))
def test_occurrences_must_be_strictly_increasing(occurrences: list[int]) -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        select_missed_occurrences(
            occurrences, now_us=30, policy=MissedRunPolicy.BACKFILL_ALL
        )


@pytest.mark.parametrize("bad_value", [True, -1])
def test_occurrence_timestamp_validation_fails_closed(bad_value: object) -> None:
    error = TypeError if bad_value is True else ValueError
    with pytest.raises(error):
        select_missed_occurrences(
            [bad_value], now_us=30, policy=MissedRunPolicy.BACKFILL_ALL
        )


def test_bounded_policy_requires_positive_genuine_integer_limit() -> None:
    with pytest.raises(TypeError, match="integer max_backfill"):
        select_missed_occurrences(
            [10],
            now_us=10,
            policy=MissedRunPolicy.BACKFILL_BOUNDED,
            max_backfill=True,
        )
    with pytest.raises(ValueError, match=">= 1"):
        select_missed_occurrences(
            [10],
            now_us=10,
            policy=MissedRunPolicy.BACKFILL_BOUNDED,
            max_backfill=0,
        )


def test_nonbounded_policy_rejects_stray_backfill_limit() -> None:
    with pytest.raises(ValueError, match="only valid"):
        select_missed_occurrences(
            [10],
            now_us=10,
            policy=MissedRunPolicy.RUN_ONCE,
            max_backfill=1,
        )


def test_empty_or_future_only_occurrences_produce_no_jobs() -> None:
    assert select_missed_occurrences(
        [], now_us=10, policy=MissedRunPolicy.RUN_ONCE
    ) == ()
    assert select_missed_occurrences(
        [20, 30], now_us=10, policy=MissedRunPolicy.BACKFILL_ALL
    ) == ()
