"""News subsystem value objects, identifiers, and domain errors."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

NEWS_JOB_TYPE = "news.daily"
NEWS_PERIOD_JOB_TYPE = "news.period"
NEWS_PIPELINE_VERSION = "news-daily-v1"


class NewsError(RuntimeError):
    """Base News subsystem error."""


class NewsConsentRequired(NewsError):
    """Raised when configured network hosts differ from standing user consent."""


def _uuid_value(value: object, label: str) -> None:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")


def _optional_uuid(value: object | None, label: str) -> None:
    if value is not None:
        _uuid_value(value, label)


def _nonnegative_int(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")


def _canonical_date(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO calendar date.") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{label} must use canonical ISO date text.")


@dataclass(frozen=True, slots=True)
class NewsRunView:
    run_id: uuid.UUID
    target_date: str
    state: str
    discovered_count: int
    captured_count: int
    failed_count: int
    research_job_id: uuid.UUID | None
    research_result_id: uuid.UUID | None
    digest_id: uuid.UUID | None

    def __post_init__(self) -> None:
        _uuid_value(self.run_id, "News run run_id")
        _canonical_date(self.target_date, "News run target_date")
        if not isinstance(self.state, str):
            raise TypeError("News run state must be text.")
        if not self.state or self.state != self.state.strip():
            raise ValueError("News run state must be canonical non-empty text.")
        for value, label in (
            (self.discovered_count, "News run discovered_count"),
            (self.captured_count, "News run captured_count"),
            (self.failed_count, "News run failed_count"),
        ):
            _nonnegative_int(value, label)
        if self.captured_count + self.failed_count > self.discovered_count:
            raise ValueError("News run captured/failed counts exceed discovered_count.")
        _optional_uuid(self.research_job_id, "News run research_job_id")
        _optional_uuid(self.research_result_id, "News run research_result_id")
        _optional_uuid(self.digest_id, "News run digest_id")
