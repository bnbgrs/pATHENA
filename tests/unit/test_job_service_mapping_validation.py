from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.service import DurableJobService, InvalidJobPayloadError

JOB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TOKEN = b"x" * 32
TARGET_ID = str(uuid.UUID("22222222-2222-4222-8222-222222222222"))


@dataclass
class _Chat:
    calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.calls += 1
        return uuid.UUID("33333333-3333-4333-8333-333333333333")


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


def _backup_scope() -> dict[str, Any]:
    return {"schedule_slot_us": 1, "target_id": TARGET_ID}


def _backup_config() -> dict[str, Any]:
    return {"pipeline_version": "backup-scheduler-v1", "quiet_hour_utc": 3}


@pytest.mark.parametrize("value", [[], (), ["x"], "x", 1, True, b"x"])
def test_create_rejects_non_mapping_requested_scope_before_actor_or_repository(
    value: Any,
) -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type="backup.create",
            priority=JobPriority.DATA_SAFETY,
            requested_scope=value,  # type: ignore[arg-type]
            pinned_configuration=_backup_config(),
        )

    assert chat.calls == 0
    assert repository.calls == []


@pytest.mark.parametrize("value", [[], (), ["x"], "x", 1, True, b"x"])
def test_create_rejects_non_mapping_pinned_configuration_before_actor_or_repository(
    value: Any,
) -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type="backup.create",
            priority=JobPriority.DATA_SAFETY,
            requested_scope=_backup_scope(),
            pinned_configuration=value,  # type: ignore[arg-type]
        )

    assert chat.calls == 0
    assert repository.calls == []


@pytest.mark.parametrize(
    "field",
    [
        "progress_state",
        "last_confirmed_input",
        "last_confirmed_output",
        "resume_metadata",
    ],
)
@pytest.mark.parametrize("value", [[], (), ["x"], "x", 1, True, b"x"])
def test_checkpoint_rejects_non_mapping_json_fields_before_repository(
    field: str,
    value: Any,
) -> None:
    service, repository, _chat = _service()
    kwargs: dict[str, Any] = {
        "lease_token": TOKEN,
        "current_stage": "stage",
        field: value,
    }

    with pytest.raises(InvalidJobPayloadError):
        service.checkpoint(JOB_ID, **kwargs)

    assert repository.calls == []


def test_valid_checkpoint_mappings_persist_canonical_objects() -> None:
    service, repository, _chat = _service()

    service.checkpoint(
        JOB_ID,
        lease_token=TOKEN,
        current_stage="stage",
        progress_state={"b": 2, "a": 1},
        last_confirmed_input={"input": True},
        last_confirmed_output={"output": None},
        resume_metadata={"next": "stage-2"},
        now_us=0,
    )

    name, _args, kwargs = repository.calls[0]
    assert name == "add_checkpoint"
    assert json.loads(kwargs["progress_state_json"]) == {"a": 1, "b": 2}
    assert json.loads(kwargs["last_confirmed_input_json"]) == {"input": True}
    assert json.loads(kwargs["last_confirmed_output_json"]) == {"output": None}
    assert json.loads(kwargs["resume_metadata_json"]) == {"next": "stage-2"}
