from __future__ import annotations

import copy
import json
import uuid
from dataclasses import dataclass, field
from typing import Any

import pytest

from athena.jobs.models import JobPriority
from athena.jobs.news_payload_validation import (
    NewsJobPayloadValidationError,
    validate_news_job_payload,
)
from athena.jobs.service import DurableJobService, InvalidJobPayloadError
from athena.news.models import NEWS_JOB_TYPE, NEWS_PERIOD_JOB_TYPE, NEWS_PIPELINE_VERSION
from athena.news.schema import NEWS_SCHEMA_ID

PROFILE_ID = str(uuid.UUID("aaaaaaaa-1111-4111-8111-111111111111"))


def _daily() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {"profile_id": PROFILE_ID, "target_date": "2026-08-23"},
        {"pipeline_version": NEWS_PIPELINE_VERSION, "news_schema": NEWS_SCHEMA_ID},
    )


def _period() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "profile_id": PROFILE_ID,
            "period_kind": "weekly",
            "period_start": "2026-08-17",
            "period_end": "2026-08-23",
        },
        {"pipeline_version": NEWS_PIPELINE_VERSION, "news_schema": NEWS_SCHEMA_ID},
    )


@pytest.mark.parametrize(
    "job_type,factory",
    [
        pytest.param(NEWS_JOB_TYPE, _daily, id="daily"),
        pytest.param(NEWS_PERIOD_JOB_TYPE, _period, id="period"),
    ],
)
def test_current_news_contracts_validate(job_type: str, factory: Any) -> None:
    scope, config = factory()
    validate_news_job_payload(
        job_type,
        requested_scope=scope,
        pinned_configuration=config,
    )


@pytest.mark.parametrize(
    "scope,config",
    [
        pytest.param({"profile_id": PROFILE_ID}, _daily()[1], id="missing-date"),
        pytest.param(
            {"profile_id": PROFILE_ID, "target_date": "2026-8-3"},
            _daily()[1],
            id="noncanonical-date",
        ),
        pytest.param(
            {"profile_id": "bad", "target_date": "2026-08-23"},
            _daily()[1],
            id="bad-profile-id",
        ),
        pytest.param(
            {**_daily()[0], "extra": True},
            _daily()[1],
            id="extra-scope-field",
        ),
        pytest.param(
            _daily()[0],
            {"pipeline_version": "old", "news_schema": NEWS_SCHEMA_ID},
            id="pipeline-drift",
        ),
        pytest.param(
            _daily()[0],
            {"pipeline_version": NEWS_PIPELINE_VERSION, "news_schema": "old"},
            id="schema-drift",
        ),
    ],
)
def test_daily_news_rejects_malformed_contract(
    scope: dict[str, Any],
    config: dict[str, Any],
) -> None:
    with pytest.raises(NewsJobPayloadValidationError):
        validate_news_job_payload(
            NEWS_JOB_TYPE,
            requested_scope=scope,
            pinned_configuration=config,
        )


@pytest.mark.parametrize(
    "scope,config",
    [
        pytest.param(
            {**_period()[0], "period_kind": "yearly"},
            _period()[1],
            id="period-kind",
        ),
        pytest.param(
            {**_period()[0], "period_start": "2026-08-24"},
            _period()[1],
            id="period-order",
        ),
        pytest.param(
            {**_period()[0], "period_end": "2026-02-30"},
            _period()[1],
            id="invalid-date",
        ),
        pytest.param(
            {**_period()[0], "profile_id": PROFILE_ID.upper()},
            _period()[1],
            id="profile-canonical",
        ),
        pytest.param(
            {**_period()[0], "extra": 1},
            _period()[1],
            id="extra-scope-field",
        ),
    ],
)
def test_period_news_rejects_malformed_contract(
    scope: dict[str, Any],
    config: dict[str, Any],
) -> None:
    with pytest.raises(NewsJobPayloadValidationError):
        validate_news_job_payload(
            NEWS_PERIOD_JOB_TYPE,
            requested_scope=scope,
            pinned_configuration=config,
        )


@dataclass
class _FakeChat:
    actor_calls: int = 0

    def ensure_local_user(self) -> uuid.UUID:
        self.actor_calls += 1
        return uuid.UUID("22222222-2222-4222-8222-222222222222")


@dataclass
class _FakeRepository:
    create_calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> object:
        self.create_calls.append(copy.deepcopy(kwargs))
        return object()


def test_invalid_news_job_fails_before_actor_or_repository_write() -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = _daily()
    scope["target_date"] = "not-a-date"

    with pytest.raises(InvalidJobPayloadError):
        service.create(
            job_type=NEWS_JOB_TYPE,
            priority=JobPriority.BACKGROUND,
            requested_scope=scope,
            pinned_configuration=config,
        )

    assert chat.actor_calls == 0
    assert repository.create_calls == []


@pytest.mark.parametrize(
    "job_type,factory",
    [
        pytest.param(NEWS_JOB_TYPE, _daily, id="daily"),
        pytest.param(NEWS_PERIOD_JOB_TYPE, _period, id="period"),
    ],
)
def test_valid_news_job_uses_central_service_and_persists_canonical_json(
    job_type: str,
    factory: Any,
) -> None:
    chat = _FakeChat()
    repository = _FakeRepository()
    service = DurableJobService(repository, chat)  # type: ignore[arg-type]
    scope, config = factory()

    service.create(
        job_type=job_type,
        priority=JobPriority.BACKGROUND,
        requested_scope=scope,
        pinned_configuration=config,
    )

    assert chat.actor_calls == 1
    assert len(repository.create_calls) == 1
    persisted = repository.create_calls[0]
    assert json.loads(persisted["requested_scope_json"]) == scope
    assert json.loads(persisted["pinned_configuration_json"]) == config
