from __future__ import annotations

import uuid

import pytest

from athena.news.models import NewsRunView


def _run(**overrides: object) -> NewsRunView:
    values: dict[str, object] = {
        "run_id": uuid.uuid4(),
        "target_date": "2026-08-23",
        "state": "running",
        "discovered_count": 3,
        "captured_count": 1,
        "failed_count": 1,
        "research_job_id": None,
        "research_result_id": None,
        "digest_id": None,
    }
    values.update(overrides)
    return NewsRunView(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("target_date", ["2026-8-23", "not-a-date", " 2026-08-23"])
def test_news_run_view_requires_canonical_date(target_date: str) -> None:
    with pytest.raises(ValueError):
        _run(target_date=target_date)


@pytest.mark.parametrize("field", ["discovered_count", "captured_count", "failed_count"])
@pytest.mark.parametrize("value", [True, -1, 1.5])
def test_news_run_view_rejects_invalid_counts(field: str, value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _run(**{field: value})


def test_news_run_view_rejects_completed_counts_above_discovery() -> None:
    with pytest.raises(ValueError, match="exceed discovered_count"):
        _run(discovered_count=1, captured_count=1, failed_count=1)
