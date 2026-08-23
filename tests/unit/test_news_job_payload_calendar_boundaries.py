from __future__ import annotations

import pytest

from athena.jobs.news_payload_validation import (
    NewsJobPayloadValidationError,
    validate_news_job_payload,
)
from athena.news.common import _default_profile_id
from athena.news.models import NEWS_PERIOD_JOB_TYPE, NEWS_PIPELINE_VERSION
from athena.news.schema import NEWS_SCHEMA_ID


def test_weekly_news_period_rejects_calendar_overflow_as_contract_error() -> None:
    with pytest.raises(NewsJobPayloadValidationError, match="calendar range"):
        validate_news_job_payload(
            NEWS_PERIOD_JOB_TYPE,
            requested_scope={
                "profile_id": str(_default_profile_id()),
                "period_kind": "weekly",
                "period_start": "9999-12-27",
                "period_end": "9999-12-31",
            },
            pinned_configuration={
                "pipeline_version": NEWS_PIPELINE_VERSION,
                "news_schema": NEWS_SCHEMA_ID,
            },
        )
