from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import WaitingReason
from athena.jobs.service import (
    DurableJobService,
    InvalidJobPayloadError,
    UnsupportedJobTypeError,
)

JOB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TOKEN = b"x" * 32


@dataclass
class _Chat:
    calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.calls += 1
        return uuid.UUID("22222222-2222-4222-8222-222222222222")


@dataclass
class _Repository:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)

    def __getattr__(self, name: str) -> Callable[..., object]:
        def call(*args: Any, **kwargs: Any) -> object:
            self.calls.append((name, args, kwargs))
            return object()

        return call


def _service() -> tuple[DurableJobService, _Repository, _Chat]:
    repository = _Repository()
    chat = _Chat()
    return DurableJobService(repository, chat), repository, chat  # type: ignore[arg-type]


INVALID_CALLS: tuple[tuple[str, Callable[[DurableJobService], object]], ...] = (
    ("create-next-negative", lambda service: service.create(job_type="search.rebuild", next_run_at_us=-1)),
    ("create-next-bool", lambda service: service.create(job_type="search.rebuild", next_run_at_us=True)),
    ("active-limit-zero", lambda service: service.active_for_type("search.rebuild", limit=0)),
    ("active-limit-bool", lambda service: service.active_for_type("search.rebuild", limit=True)),
    ("acquire-worker-empty", lambda service: service.acquire(JOB_ID, worker_id="")),
    ("acquire-worker-padded", lambda service: service.acquire(JOB_ID, worker_id=" worker ")),
    ("acquire-lease-zero", lambda service: service.acquire(JOB_ID, worker_id="worker", lease_seconds=0)),
    ("acquire-lease-bool", lambda service: service.acquire(JOB_ID, worker_id="worker", lease_seconds=True)),
    ("acquire-now-negative", lambda service: service.acquire(JOB_ID, worker_id="worker", now_us=-1)),
    ("heartbeat-token-short", lambda service: service.heartbeat(JOB_ID, lease_token=b"x" * 31)),
    ("heartbeat-token-type", lambda service: service.heartbeat(JOB_ID, lease_token=bytearray(32))),  # type: ignore[arg-type]
    ("heartbeat-extend-zero", lambda service: service.heartbeat(JOB_ID, lease_token=TOKEN, extend_seconds=0)),
    ("heartbeat-extend-bool", lambda service: service.heartbeat(JOB_ID, lease_token=TOKEN, extend_seconds=True)),
    ("heartbeat-now-negative", lambda service: service.heartbeat(JOB_ID, lease_token=TOKEN, now_us=-1)),
    ("fence-token-short", lambda service: service.canonical_write_fence(JOB_ID, lease_token=b"x")),
    ("checkpoint-token-short", lambda service: service.checkpoint(JOB_ID, lease_token=b"x", current_stage="stage")),
    ("checkpoint-stage-empty", lambda service: service.checkpoint(JOB_ID, lease_token=TOKEN, current_stage="")),
    ("checkpoint-stage-padded", lambda service: service.checkpoint(JOB_ID, lease_token=TOKEN, current_stage=" stage ")),
    ("checkpoint-now-negative", lambda service: service.checkpoint(JOB_ID, lease_token=TOKEN, current_stage="stage", now_us=-1)),
    ("recover-now-negative", lambda service: service.recover_startup(now_us=-1)),
    ("recover-now-bool", lambda service: service.recover_startup(now_us=True)),
    ("list-limit-zero", lambda service: service.list(limit=0)),
    ("list-limit-bool", lambda service: service.list(limit=True)),
    ("eligible-now-negative", lambda service: service.eligible_queued(now_us=-1)),
    ("eligible-now-bool", lambda service: service.eligible_queued(now_us=True)),
    ("eligible-limit-zero", lambda service: service.eligible_queued(now_us=0, limit=0)),
    ("waiting-limit-zero", lambda service: service.waiting(limit=0)),
    ("waiting-limit-bool", lambda service: service.waiting(limit=True)),
    ("wake-due-now-negative", lambda service: service.wake_due_waiting(now_us=-1)),
    ("retry-next-negative", lambda service: service.schedule_retry(JOB_ID, next_run_at_us=-1, max_retries=1)),
    ("retry-next-bool", lambda service: service.schedule_retry(JOB_ID, next_run_at_us=True, max_retries=1)),
    ("retry-count-negative", lambda service: service.schedule_retry(JOB_ID, next_run_at_us=0, max_retries=-1)),
    ("retry-count-bool", lambda service: service.schedule_retry(JOB_ID, next_run_at_us=0, max_retries=True)),
    ("retry-now-negative", lambda service: service.schedule_retry(JOB_ID, next_run_at_us=0, max_retries=1, now_us=-1)),
    ("yield-token-short", lambda service: service.yield_job(JOB_ID, lease_token=b"x")),
    ("yield-next-negative", lambda service: service.yield_job(JOB_ID, lease_token=TOKEN, next_run_at_us=-1)),
    ("yield-now-negative", lambda service: service.yield_job(JOB_ID, lease_token=TOKEN, now_us=-1)),
    ("fail-token-short", lambda service: service.fail(JOB_ID, lease_token=b"x", blocked_reason="failure")),
    ("fail-reason-empty", lambda service: service.fail(JOB_ID, lease_token=TOKEN, blocked_reason="")),
    ("fail-reason-padded", lambda service: service.fail(JOB_ID, lease_token=TOKEN, blocked_reason=" failure ")),
    ("fail-now-negative", lambda service: service.fail(JOB_ID, lease_token=TOKEN, blocked_reason="failure", now_us=-1)),
    ("wait-token-short", lambda service: service.wait(JOB_ID, lease_token=b"x", reason=WaitingReason.RESOURCE)),
    ("wait-reason-string", lambda service: service.wait(JOB_ID, lease_token=TOKEN, reason="waiting_resource")),  # type: ignore[arg-type]
    ("wait-reason-none", lambda service: service.wait(JOB_ID, lease_token=TOKEN, reason=None)),  # type: ignore[arg-type]
    ("wait-reason-bool", lambda service: service.wait(JOB_ID, lease_token=TOKEN, reason=True)),  # type: ignore[arg-type]
    ("wait-next-negative", lambda service: service.wait(JOB_ID, lease_token=TOKEN, reason=WaitingReason.RESOURCE, next_run_at_us=-1)),
    ("wait-now-negative", lambda service: service.wait(JOB_ID, lease_token=TOKEN, reason=WaitingReason.RESOURCE, now_us=-1)),
    ("complete-token-short", lambda service: service.complete(JOB_ID, lease_token=b"x")),
    ("complete-now-negative", lambda service: service.complete(JOB_ID, lease_token=TOKEN, now_us=-1)),
    ("cancel-token-short", lambda service: service.acknowledge_cancel(JOB_ID, lease_token=b"x")),
    ("cancel-now-negative", lambda service: service.acknowledge_cancel(JOB_ID, lease_token=TOKEN, now_us=-1)),
)


@pytest.mark.parametrize("_label,invoke", INVALID_CALLS, ids=[item[0] for item in INVALID_CALLS])
def test_invalid_scalar_never_reaches_repository(
    _label: str,
    invoke: Callable[[DurableJobService], object],
) -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        invoke(service)

    assert repository.calls == []
    assert chat.calls == 0


def test_eligible_queue_rejects_unregistered_type_before_repository() -> None:
    service, repository, _chat = _service()

    with pytest.raises(UnsupportedJobTypeError):
        service.eligible_queued(now_us=0, job_types={"not.registered"})

    assert repository.calls == []


def test_valid_zero_timestamps_and_retry_zero_reach_repository() -> None:
    service, repository, _chat = _service()

    service.schedule_retry(JOB_ID, next_run_at_us=0, max_retries=0, now_us=0)

    assert repository.calls[0][0] == "schedule_retry"
    assert repository.calls[0][2]["next_run_at_us"] == 0
    assert repository.calls[0][2]["max_retries"] == 0
    assert repository.calls[0][2]["now_us"] == 0


def test_valid_lease_boundary_converts_seconds_to_microseconds() -> None:
    service, repository, _chat = _service()

    service.acquire(JOB_ID, worker_id="worker-1", lease_seconds=2, now_us=0)

    name, _args, kwargs = repository.calls[0]
    assert name == "acquire_lease"
    assert kwargs["worker_id"] == "worker-1"
    assert kwargs["lease_duration_us"] == 2_000_000
    assert kwargs["now_us"] == 0
    assert isinstance(kwargs["lease_token"], bytes)
    assert len(kwargs["lease_token"]) == 32


def test_valid_waiting_reason_reaches_repository_unchanged() -> None:
    service, repository, _chat = _service()

    service.wait(
        JOB_ID,
        lease_token=TOKEN,
        reason=WaitingReason.DEPENDENCY,
        next_run_at_us=0,
        now_us=0,
    )

    name, _args, kwargs = repository.calls[0]
    assert name == "wait"
    assert kwargs["reason"] is WaitingReason.DEPENDENCY
    assert kwargs["next_run_at_us"] == 0
    assert kwargs["now_us"] == 0


def test_valid_queue_type_filter_reaches_repository_unchanged() -> None:
    service, repository, _chat = _service()

    service.eligible_queued(now_us=0, job_types={"source.process", "source.analyze"}, limit=1)

    name, _args, kwargs = repository.calls[0]
    assert name == "list_eligible_queued"
    assert kwargs["job_types"] == {"source.process", "source.analyze"}
    assert kwargs["limit"] == 1
