from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.service import (
    DurableJobService,
    InvalidJobPayloadError,
    UnsupportedJobTypeError,
)


@dataclass
class _Chat:
    calls: int = 0

    def ensure_local_user(self) -> Any:
        self.calls += 1
        return object()


@dataclass
class _Repository:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)

    def __getattr__(self, name: str) -> Callable[..., object]:
        def call(*args: Any, **kwargs: Any) -> object:
            self.calls.append((name, args, kwargs))
            return object()

        return call


class _Graph:
    def __init__(self, repository: _Repository) -> None:
        self.repository = repository

    def require_runnable(self, _job_id: object) -> None:
        return None

    def reconcile(self, *, now_us: int | None = None) -> tuple[()]:
        del now_us
        return ()

    def eligible_queued(
        self,
        *,
        now_us: int,
        job_types: set[str] | frozenset[str] | None,
        limit: int,
    ) -> object:
        return self.repository.list_eligible_queued(
            now_us=now_us,
            job_types=job_types,
            limit=limit,
        )


def _service() -> tuple[DurableJobService, _Repository, _Chat]:
    repository = _Repository()
    chat = _Chat()
    return (
        DurableJobService(  # type: ignore[arg-type]
            repository,
            chat,
            graph=_Graph(repository),  # type: ignore[arg-type]
        ),
        repository,
        chat,
    )


@pytest.mark.parametrize(
    "value",
    [None, True, False, 1, 1.5, [], {}, "", " source.process "],
)
def test_create_rejects_malformed_job_type_before_actor_or_repository(value: Any) -> None:
    service, repository, chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.create(job_type=value)  # type: ignore[arg-type]

    assert chat.calls == 0
    assert repository.calls == []


def test_create_rejects_canonical_but_unregistered_job_type() -> None:
    service, repository, chat = _service()

    with pytest.raises(UnsupportedJobTypeError):
        service.create(job_type="not.registered")

    assert chat.calls == 0
    assert repository.calls == []


@pytest.mark.parametrize(
    "value",
    [None, True, False, 1, 1.5, [], {}, "", " source.process "],
)
def test_active_for_type_rejects_malformed_job_type_before_repository(value: Any) -> None:
    service, repository, _chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.active_for_type(value)  # type: ignore[arg-type]

    assert repository.calls == []


@pytest.mark.parametrize(
    "value",
    [[], (), ["source.process"], ("source.process",), "source.process", 1, True],
)
def test_eligible_queue_requires_set_or_frozenset_filter(value: Any) -> None:
    service, repository, _chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.eligible_queued(now_us=0, job_types=value)  # type: ignore[arg-type]

    assert repository.calls == []


@pytest.mark.parametrize(
    "value",
    [
        {1},
        {True},
        {None},
        {" source.process "},
        frozenset({""}),
    ],
)
def test_eligible_queue_rejects_malformed_filter_members(value: Any) -> None:
    service, repository, _chat = _service()

    with pytest.raises(InvalidJobPayloadError):
        service.eligible_queued(now_us=0, job_types=value)  # type: ignore[arg-type]

    assert repository.calls == []


def test_eligible_queue_rejects_unregistered_filter_member() -> None:
    service, repository, _chat = _service()

    with pytest.raises(UnsupportedJobTypeError):
        service.eligible_queued(now_us=0, job_types={"source.process", "not.registered"})

    assert repository.calls == []


def test_frozenset_filter_is_normalized_and_forwarded_as_registered_set() -> None:
    service, repository, _chat = _service()

    service.eligible_queued(
        now_us=0,
        job_types=frozenset({"source.process", "news.daily"}),
        limit=1,
    )

    name, _args, kwargs = repository.calls[0]
    assert name == "list_eligible_queued"
    assert kwargs["job_types"] == {"source.process", "news.daily"}
    assert kwargs["limit"] == 1
