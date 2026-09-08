from __future__ import annotations

from typing import Any, cast

import pytest

from athena.jobs.scheduler import DurableJobScheduler, SchedulerPolicy
from athena.storage.wal_job_hook import WalAwareDurableJobScheduler, WalJobSchedulerHook


class _CustomDurableJobScheduler(DurableJobScheduler):
    pass


class _CustomWalJobSchedulerHook(WalJobSchedulerHook):
    pass


def _scheduler_with_sentinels() -> tuple[DurableJobScheduler, object]:
    dependency = object()
    opaque = cast(Any, dependency)
    scheduler = DurableJobScheduler(
        jobs=opaque,
        source_worker=opaque,
        embedding_worker=opaque,
        analysis_worker=opaque,
        extraction_worker=opaque,
        research_worker=opaque,
        archive_replication_worker=opaque,
        backup_worker=opaque,
        resources=opaque,
        news_worker=opaque,
        policy=SchedulerPolicy(),
    )
    return scheduler, dependency


def test_from_scheduler_preserves_dependencies_policy_and_is_side_effect_free() -> None:
    scheduler, dependency = _scheduler_with_sentinels()
    hook = object.__new__(WalJobSchedulerHook)

    converted = WalAwareDurableJobScheduler.from_scheduler(scheduler, hook)

    assert converted.jobs is dependency
    assert converted.source_worker is dependency
    assert converted.embedding_worker is dependency
    assert converted.analysis_worker is dependency
    assert converted.extraction_worker is dependency
    assert converted.research_worker is dependency
    assert converted.archive_replication_worker is dependency
    assert converted.backup_worker is dependency
    assert converted.resources is dependency
    assert converted.news_worker is dependency
    assert converted.policy is scheduler.policy
    assert converted._wal_housekeeping_hook is hook
    assert converted.run_loop.__func__ is DurableJobScheduler.run_loop
    assert converted.drain.__func__ is DurableJobScheduler.drain


def test_from_scheduler_rejects_already_wal_aware_scheduler() -> None:
    scheduler, _ = _scheduler_with_sentinels()
    hook = object.__new__(WalJobSchedulerHook)
    converted = WalAwareDurableJobScheduler.from_scheduler(scheduler, hook)

    with pytest.raises(ValueError, match="already WAL-aware"):
        WalAwareDurableJobScheduler.from_scheduler(converted, hook)


def test_from_scheduler_rejects_noncanonical_scheduler_subclass() -> None:
    scheduler, _ = _scheduler_with_sentinels()
    custom = _CustomDurableJobScheduler(
        jobs=scheduler.jobs,
        source_worker=scheduler.source_worker,
        embedding_worker=scheduler.embedding_worker,
        analysis_worker=scheduler.analysis_worker,
        extraction_worker=scheduler.extraction_worker,
        research_worker=scheduler.research_worker,
        archive_replication_worker=scheduler.archive_replication_worker,
        backup_worker=scheduler.backup_worker,
        resources=scheduler.resources,
        news_worker=scheduler.news_worker,
        policy=scheduler.policy,
    )
    hook = object.__new__(WalJobSchedulerHook)

    with pytest.raises(TypeError, match="canonical DurableJobScheduler"):
        WalAwareDurableJobScheduler.from_scheduler(custom, hook)


def test_from_scheduler_rejects_noncanonical_hook_subclass_before_recomposition() -> None:
    scheduler, dependency = _scheduler_with_sentinels()
    hook = object.__new__(_CustomWalJobSchedulerHook)

    with pytest.raises(TypeError, match="canonical WalJobSchedulerHook"):
        WalAwareDurableJobScheduler.from_scheduler(scheduler, hook)

    assert scheduler.jobs is dependency


def test_from_scheduler_rejects_invalid_hook_before_recomposition() -> None:
    scheduler, _ = _scheduler_with_sentinels()

    with pytest.raises(TypeError, match="canonical WalJobSchedulerHook"):
        WalAwareDurableJobScheduler.from_scheduler(
            scheduler,
            cast(Any, object()),
        )