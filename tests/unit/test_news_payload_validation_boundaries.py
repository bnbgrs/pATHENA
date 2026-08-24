from __future__ import annotations

from datetime import date

import pytest

from athena.jobs.news_payload_validation import (
    NewsJobPayloadValidationError,
    _month_end,
    validate_news_job_payload,
)
from athena.news.models import NEWS_JOB_TYPE, NEWS_PIPELINE_VERSION
from athena.news.schema import NEWS_SCHEMA_ID


def _config() -> dict[str, str]:
    return {
        "pipeline_version": NEWS_PIPELINE_VERSION,
        "news_schema": NEWS_SCHEMA_ID,
    }


def test_daily_news_rejects_non_object_scope_with_domain_error() -> None:
    with pytest.raises(NewsJobPayloadValidationError, match="requested_scope must be an object"):
        validate_news_job_payload(
            NEWS_JOB_TYPE,
            requested_scope=[],  # type: ignore[arg-type]
            pinned_configuration=_config(),
        )


def test_daily_news_rejects_non_object_configuration_with_domain_error() -> None:
    with pytest.raises(
        NewsJobPayloadValidationError,
        match="pinned_configuration must be an object",
    ):
        validate_news_job_payload(
            NEWS_JOB_TYPE,
            requested_scope={},
            pinned_configuration=[],  # type: ignore[arg-type]
        )


def test_month_end_supports_maximum_iso_calendar_year() -> None:
    assert _month_end(date(9999, 12, 1)) == date(9999, 12, 31)


def test_month_end_keeps_normal_leap_february_behavior() -> None:
    assert _month_end(date(2028, 2, 1)) == date(2028, 2, 29)
