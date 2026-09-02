from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

TARGET_ID = str(uuid.UUID("77777777-7777-4777-8777-777777777777"))


@dataclass
class _FakeChat:
    actor_calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.actor_calls += 1
        return uuid.UUID("66666666-6666-4666-8666-666666666666")


@dataclass
class _FakeRepository:
    create_calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> object:
        self.create_calls.append(kwargs)
        return object()


def _backup_payload() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"schedule_slot_us": 0, "target_id": TARGET_ID},
        {"pipeline_version": "backup-scheduler-v1", "quiet_hour_utc": 3},
    )


@pytest.mark.parametrize(
    "priority",
    [
        pytest.param(True, id="bool-true"),
        pytest.param(False, id="bool-false"),
        pytest.param(0, id="raw-zero"),
        pytest.param(3, id="raw-normal"),
        pytest.param("3", id="text"),
        pytest.param(None, id="none"),
    ],
)
def test_create_rejects_untyped_priority_before_actor_or_repository_write(
    priority: Any,
) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = _backup_payload()

    with pytest.raises(InvalidJobPayloadError, match="JobPriority"):
        service.create(
            job_type="backup.create",
            priority=priority,
            requested_scope=scope,
            pinned_configuration=config,
        )

    assert chat.actor_calls == 0
    assert repository.create_calls == []


@pytest.mark.parametrize("priority", list(JobPriority))
def test_create_accepts_every_registered_job_priority(priority: JobPriority) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = _backup_payload()

    service.create(
        job_type="backup.create",
        priority=priority,
        requested_scope=scope,
        pinned_configuration=config,
    )

    assert chat.actor_calls == 1
    assert len(repository.create_calls) == 1
    assert repository.create_calls[0]["priority"] is priority
