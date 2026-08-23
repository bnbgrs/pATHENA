from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.service import DurableJobService, InvalidJobPayloadError

JOB_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
TOKEN = b"x" * 32


@dataclass
class _Repository:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)

    def __getattr__(self, name: str) -> Callable[..., object]:
        def call(*args: Any, **kwargs: Any) -> object:
            self.calls.append((name, args, kwargs))
            return object()

        return call


@dataclass
class _Chat:
    def ensure_local_user(self) -> uuid.UUID:
        return uuid.UUID("22222222-2222-4222-8222-222222222222")


def _service() -> tuple[DurableJobService, _Repository]:
    repository = _Repository()
    return DurableJobService(repository, _Chat()), repository  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "payload",
    [
        {1: "integer-key"},
        {True: "boolean-key"},
        {"nested": {1: "integer-key"}},
        {"tuple": (1, 2)},
        {"set": {1, 2}},
        {"bytes": b"payload"},
        {"uuid": JOB_ID},
        {"nan": float("nan")},
        {"positive_inf": float("inf")},
        {"negative_inf": float("-inf")},
        {"nested": [1, {"bad": float("nan")}]},
    ],
)
def test_checkpoint_rejects_noncanonical_json_before_repository(
    payload: dict[Any, Any],
) -> None:
    service, repository = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.checkpoint(
            JOB_ID,
            lease_token=TOKEN,
            current_stage="stage",
            progress_state=payload,  # type: ignore[arg-type]
        )

    assert repository.calls == []


def test_checkpoint_accepts_nested_native_json_values() -> None:
    service, repository = _service()

    service.checkpoint(
        JOB_ID,
        lease_token=TOKEN,
        current_stage="stage",
        progress_state={
            "null": None,
            "bool": True,
            "int": 1,
            "float": 1.25,
            "text": "value",
            "list": [1, False, None, {"nested": "value"}],
            "object": {"child": [1, 2, 3]},
        },
        now_us=0,
    )

    assert repository.calls[0][0] == "add_checkpoint"
