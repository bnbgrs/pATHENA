from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import WaitingReason
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

JOB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
CHECKPOINT_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
TOKEN = b"x" * 32


@dataclass
class _Chat:
    def ensure_local_user(self) -> uuid.UUID:
        return uuid.UUID("33333333-3333-4333-8333-333333333333")


@dataclass
class _Repository:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)

    def __getattr__(self, name: str) -> Callable[..., object]:
        def call(*args: Any, **kwargs: Any) -> object:
            self.calls.append((name, args, kwargs))
            return object()

        return call


def _service() -> tuple[DurableJobService, _Repository]:
    repository = _Repository()
    service = DurableJobService(repository, _Chat())  # type: ignore[arg-type]
    return service, repository


INVALID_IDS: tuple[Any, ...] = (
    None,
    True,
    False,
    0,
    1,
    1.5,
    "11111111-1111-4111-8111-111111111111",
    b"x" * 16,
    object(),
)


@pytest.mark.parametrize("value", INVALID_IDS)
def test_get_rejects_non_uuid_before_repository(value: Any) -> None:
    service, repository = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.get(value)  # type: ignore[arg-type]

    assert repository.calls == []


@pytest.mark.parametrize(
    "invoke",
    [
        lambda service, value: service.acquire(value, worker_id="worker"),
        lambda service, value: service.heartbeat(value, lease_token=TOKEN),
        lambda service, value: service.canonical_write_fence(value, lease_token=TOKEN),
        lambda service, value: service.checkpoint(
            value,
            lease_token=TOKEN,
            current_stage="stage",
        ),
        lambda service, value: service.schedule_retry(
            value,
            next_run_at_us=1,
            max_retries=1,
        ),
        lambda service, value: service.yield_job(value, lease_token=TOKEN),
        lambda service, value: service.checkpoints(value),
        lambda service, value: service.fail(
            value,
            lease_token=TOKEN,
            blocked_reason="failure",
        ),
        lambda service, value: service.wait(
            value,
            lease_token=TOKEN,
            reason=WaitingReason.RESOURCE,
        ),
        lambda service, value: service.wake(value),
        lambda service, value: service.request_cancel(value),
        lambda service, value: service.pause(value),
        lambda service, value: service.resume(value),
        lambda service, value: service.complete(value, lease_token=TOKEN),
        lambda service, value: service.acknowledge_cancel(value, lease_token=TOKEN),
    ],
)
@pytest.mark.parametrize("value", INVALID_IDS)
def test_job_state_operations_reject_non_uuid_before_repository(
    invoke: Callable[[DurableJobService, Any], object],
    value: Any,
) -> None:
    service, repository = _service()

    with pytest.raises(InvalidJobPayloadError):
        invoke(service, value)

    assert repository.calls == []


@pytest.mark.parametrize("value", INVALID_IDS)
def test_get_checkpoint_rejects_non_uuid_before_repository(value: Any) -> None:
    service, repository = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.get_checkpoint(value)  # type: ignore[arg-type]

    assert repository.calls == []


@pytest.mark.parametrize("field", ["processing_stage_id", "commit_id"])
@pytest.mark.parametrize("value", INVALID_IDS)
def test_checkpoint_rejects_non_uuid_optional_identity_before_repository(
    field: str,
    value: Any,
) -> None:
    service, repository = _service()
    kwargs: dict[str, Any] = {
        "lease_token": TOKEN,
        "current_stage": "stage",
        field: value,
    }

    with pytest.raises(InvalidJobPayloadError):
        service.checkpoint(JOB_ID, **kwargs)

    assert repository.calls == []


def test_valid_uuid_identities_reach_repository_unchanged() -> None:
    service, repository = _service()

    service.checkpoint(
        JOB_ID,
        lease_token=TOKEN,
        current_stage="stage",
        processing_stage_id=CHECKPOINT_ID,
        commit_id=CHECKPOINT_ID,
        now_us=0,
    )

    name, _args, kwargs = repository.calls[0]
    assert name == "add_checkpoint"
    assert kwargs["job_id"] is JOB_ID
    assert kwargs["processing_stage_id"] is CHECKPOINT_ID
    assert kwargs["commit_id"] is CHECKPOINT_ID
