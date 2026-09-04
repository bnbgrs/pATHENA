from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.dependency_graph import (
    ChildCancellationPolicy,
    JobGraphCorruptionError,
    JobGraphError,
    JobParentCompletionBlockedError,
    ParentCompletionPolicy,
)
from athena.jobs.models import JobPriority, JobRecord, JobState, WaitingReason
from athena.jobs.repository import JobNotFoundError
from athena.storage.schema_contract import JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start()
    return app


def _payload(source_id: uuid.UUID) -> dict[str, dict[str, object]]:
    return {
        "requested_scope": {"source_id": str(source_id)},
        "pinned_configuration": {
            "pipeline_version": "source-process-v2",
            "text_parser": "athena.native_text@1",
            "pdf_parser": "athena.pdf@1",
            "docx_parser": "athena.docx@1",
            "html_parser": "athena.html@1",
            "chunking_profile": "default",
            "chunk_batch_size": 32,
            "embedding_policy": "deferred",
        },
    }


def _job(
    app: AthenaApplication,
    *,
    priority: JobPriority = JobPriority.NORMAL,
    **kwargs: Any,
) -> JobRecord:
    return app.jobs.create(
        job_type="source.process",
        priority=priority,
        **_payload(uuid.uuid4()),
        **kwargs,
    )


def _complete(app: AthenaApplication, job_id: uuid.UUID) -> None:
    job = app.jobs.get(job_id)
    now = job.created_at_us + 10_000
    leased = app.jobs.acquire(job_id, worker_id="graph-test", now_us=now)
    assert leased.lease_token is not None
    app.jobs.complete(job_id, lease_token=leased.lease_token, now_us=now + 1)


def test_schema_v41_contains_durable_job_graph_tables(tmp_path: Path) -> None:
    app = _app(tmp_path)
    connection = app.database.connection

    assert int(connection.execute("PRAGMA user_version").fetchone()[0]) == (
        JOB_DEPENDENCY_GRAPH_SCHEMA_VERSION
    )
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert {"job_dependencies", "job_parent_links"}.issubset(tables)
    app.stop()


def test_dependency_is_durable_blocks_lease_and_wakes_after_completion(
    tmp_path: Path,
) -> None:
    first = _app(tmp_path)
    dependency = _job(first, priority=JobPriority.BACKGROUND)
    blocked = _job(first, depends_on_job_ids=(dependency.job_id,))

    assert blocked.state is JobState.WAITING
    assert blocked.blocked_reason == WaitingReason.DEPENDENCY.value
    assert first.jobs.graph_snapshot(blocked.job_id).depends_on_job_ids == (
        dependency.job_id,
    )
    first.stop()

    second = _app(tmp_path)
    restarted = second.jobs.get(blocked.job_id)
    assert restarted.state is JobState.WAITING
    assert second.jobs.graph_snapshot(blocked.job_id).depends_on_job_ids == (
        dependency.job_id,
    )

    _complete(second, dependency.job_id)
    assert second.jobs.get(blocked.job_id).state is JobState.QUEUED
    second.stop()


def test_create_rolls_back_job_when_graph_validation_fails(tmp_path: Path) -> None:
    app = _app(tmp_path)
    before = tuple(job.job_id for job in app.jobs.list(limit=100))

    with pytest.raises(JobNotFoundError):
        _job(app, depends_on_job_ids=(uuid.uuid4(),))

    after = tuple(job.job_id for job in app.jobs.list(limit=100))
    assert after == before
    app.stop()


def test_parent_completion_policy_requires_successful_explicit_children(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    parent = _job(app)
    child = _job(
        app,
        parent_job_id=parent.job_id,
        parent_completion_policy=ParentCompletionPolicy.REQUIRE_SUCCESS,
    )

    parent_lease = app.jobs.acquire(
        parent.job_id,
        worker_id="parent",
        now_us=parent.created_at_us + 10_000,
    )
    assert parent_lease.lease_token is not None
    with pytest.raises(JobParentCompletionBlockedError):
        app.jobs.complete(
            parent.job_id,
            lease_token=parent_lease.lease_token,
            now_us=parent.created_at_us + 10_001,
        )

    _complete(app, child.job_id)
    completed_parent = app.jobs.complete(
        parent.job_id,
        lease_token=parent_lease.lease_token,
        now_us=parent.created_at_us + 10_002,
    )
    assert completed_parent.state is JobState.COMPLETED
    app.stop()


def test_parent_cancellation_cascades_only_across_explicit_cascade_edges(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    parent = _job(app)
    cascading_child = _job(
        app,
        parent_job_id=parent.job_id,
        child_cancellation_policy=ChildCancellationPolicy.CASCADE,
    )
    grandchild = _job(
        app,
        parent_job_id=cascading_child.job_id,
        child_cancellation_policy=ChildCancellationPolicy.CASCADE,
    )
    independent_child = _job(
        app,
        parent_job_id=parent.job_id,
        child_cancellation_policy=ChildCancellationPolicy.INDEPENDENT,
    )

    cancelled = app.jobs.request_cancel(parent.job_id)

    assert cancelled.state is JobState.CANCELLED
    assert app.jobs.get(cascading_child.job_id).state is JobState.CANCELLED
    assert app.jobs.get(grandchild.job_id).state is JobState.CANCELLED
    assert app.jobs.get(independent_child.job_id).state is JobState.QUEUED
    app.stop()


def test_cancellation_cascade_rolls_back_as_one_transaction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _app(tmp_path)
    parent = _job(app)
    child = _job(
        app,
        parent_job_id=parent.job_id,
        child_cancellation_policy=ChildCancellationPolicy.CASCADE,
    )
    original = app.job_repository._request_cancel_row
    calls = 0

    def fail_second_call(*args: Any, **kwargs: Any) -> JobState:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected cascade failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(app.job_repository, "_request_cancel_row", fail_second_call)

    with pytest.raises(RuntimeError, match="injected cascade failure"):
        app.jobs.request_cancel(parent.job_id)

    assert app.jobs.get(parent.job_id).state is JobState.QUEUED
    assert app.jobs.get(child.job_id).state is JobState.QUEUED
    app.stop()


def test_dependency_updates_reject_cycles(tmp_path: Path) -> None:
    app = _app(tmp_path)
    first = _job(app)
    second = _job(app)
    third = _job(app)

    app.jobs.replace_dependencies(first.job_id, (second.job_id,))
    app.jobs.replace_dependencies(second.job_id, (third.job_id,))

    with pytest.raises(JobGraphError, match="cycle"):
        app.jobs.replace_dependencies(third.job_id, (first.job_id,))

    assert app.jobs.graph_snapshot(third.job_id).depends_on_job_ids == ()
    app.stop()


def test_priority_inheritance_is_bounded_and_does_not_mutate_base_priority(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    dependency = _job(app, priority=JobPriority.MAINTENANCE)
    blocked_p0 = _job(
        app,
        priority=JobPriority.DATA_SAFETY,
        depends_on_job_ids=(dependency.job_id,),
    )
    now = max(dependency.created_at_us, blocked_p0.created_at_us) + 100

    assert blocked_p0.state is JobState.WAITING
    assert app.jobs.effective_priority(dependency.job_id, now_us=now) is (
        JobPriority.INTERACTIVE
    )
    assert app.jobs.get(dependency.job_id).priority is JobPriority.MAINTENANCE

    candidates = app.jobs.eligible_queued(now_us=now)
    candidate = next(item for item in candidates if item.job_id == dependency.job_id)
    assert candidate.priority is JobPriority.INTERACTIVE
    leased = app.jobs.acquire(
        dependency.job_id,
        worker_id="priority-test",
        now_us=now + 1,
    )
    assert leased.priority is JobPriority.MAINTENANCE
    app.stop()


def test_priority_inheritance_survives_small_candidate_limit(tmp_path: Path) -> None:
    app = _app(tmp_path)
    decoy = _job(app, priority=JobPriority.NORMAL)
    dependency = _job(app, priority=JobPriority.MAINTENANCE)
    blocked = _job(
        app,
        priority=JobPriority.INTERACTIVE,
        depends_on_job_ids=(dependency.job_id,),
    )
    now = max(decoy.created_at_us, dependency.created_at_us, blocked.created_at_us) + 100

    candidates = app.jobs.eligible_queued(now_us=now, limit=1)

    assert len(candidates) == 1
    assert candidates[0].job_id == dependency.job_id
    assert candidates[0].priority is JobPriority.INTERACTIVE
    assert app.jobs.get(dependency.job_id).priority is JobPriority.MAINTENANCE
    app.stop()


def test_transitive_priority_inheritance_reaches_dependency_chain(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path)
    leaf = _job(app, priority=JobPriority.MAINTENANCE)
    middle = _job(
        app,
        priority=JobPriority.BACKGROUND,
        depends_on_job_ids=(leaf.job_id,),
    )
    top = _job(
        app,
        priority=JobPriority.INTERACTIVE,
        depends_on_job_ids=(middle.job_id,),
    )
    now = max(leaf.created_at_us, middle.created_at_us, top.created_at_us) + 100

    assert app.jobs.effective_priority(leaf.job_id, now_us=now) is JobPriority.INTERACTIVE
    assert app.jobs.get(leaf.job_id).priority is JobPriority.MAINTENANCE
    app.stop()


def test_direct_dependency_limit_fails_closed(tmp_path: Path) -> None:
    app = _app(tmp_path)
    target = _job(app)
    dependencies = tuple(_job(app).job_id for _ in range(65))

    with pytest.raises(JobGraphError, match="at most 64"):
        app.jobs.replace_dependencies(target.job_id, dependencies)

    assert app.jobs.graph_snapshot(target.job_id).depends_on_job_ids == ()
    app.stop()


def test_dangling_dependency_state_fails_closed(tmp_path: Path) -> None:
    app = _app(tmp_path)
    target = _job(app)
    connection = app.database.connection
    connection.execute("PRAGMA foreign_keys = OFF")
    connection.execute(
        """
        INSERT INTO job_dependencies(job_id, depends_on_job_id, created_at_us)
        VALUES (?, ?, ?)
        """,
        (target.job_id.bytes, uuid.uuid4().bytes, target.created_at_us),
    )
    connection.execute("PRAGMA foreign_keys = ON")

    with pytest.raises(JobGraphCorruptionError, match="dangling"):
        app.jobs.graph_snapshot(target.job_id)
    app.stop()
