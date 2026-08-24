from __future__ import annotations

from typing import Any

import pytest

from athena.jobs.capabilities import CONTROL_LANE_JOB_TYPES, requires_provider_isolation


@pytest.mark.parametrize("job_type", sorted(CONTROL_LANE_JOB_TYPES))
def test_reviewed_control_jobs_do_not_require_provider_isolation(job_type: str) -> None:
    assert requires_provider_isolation(job_type) is False


@pytest.mark.parametrize(
    "job_type",
    [
        "source.analyze",
        "research.exhaustive",
        "news.daily",
        "not.registered",
    ],
)
def test_unknown_or_provider_jobs_remain_isolated(job_type: str) -> None:
    assert requires_provider_isolation(job_type) is True


@pytest.mark.parametrize(
    "value",
    [None, True, False, 0, 1, 1.5, [], {}, set(), (), "", " source.process "],
)
def test_malformed_job_identity_fails_closed_to_provider_isolation(value: Any) -> None:
    assert requires_provider_isolation(value) is True
