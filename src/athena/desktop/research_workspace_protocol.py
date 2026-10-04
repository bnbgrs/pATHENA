"""Validated process-boundary responses for the native Research workspace."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

_RESEARCH_JOB_STATES = frozenset(
    {
        "queued",
        "running",
        "waiting",
        "paused",
        "cancel_requested",
        "cancelled",
        "failed",
        "completed",
    }
)
_CANCEL_RECEIPT_STATES = frozenset({"cancel_requested", "cancelled"})


class ResearchWorkspaceProtocolError(ValueError):
    """Raised when a Research helper response cannot be trusted."""


@dataclass(frozen=True, slots=True)
class ResearchJobListEntry:
    job_id: str
    state: str
    stage: str
    coverage: float | None
    query: str


@dataclass(frozen=True, slots=True)
class ResearchCancelReceipt:
    job_id: str
    state: str


def _canonical_uuid(value: str, *, field: str) -> str:
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError) as exc:
        raise ResearchWorkspaceProtocolError(
            f"The Research response has an invalid {field}."
        ) from exc


def parse_research_job_list(output: str) -> tuple[ResearchJobListEntry, ...]:
    """Validate a complete research list response before UI projection."""
    entries: list[ResearchJobListEntry] = []
    for line_number, raw_line in enumerate(output.splitlines(), start=1):
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) != 5:
            raise ResearchWorkspaceProtocolError(
                f"The Research list response is malformed at line {line_number}."
            )
        raw_job_id, raw_state, stage, raw_coverage, query = parts
        try:
            job_id = str(uuid.UUID(raw_job_id))
        except (ValueError, AttributeError) as exc:
            raise ResearchWorkspaceProtocolError(
                f"The Research list response has an invalid job ID at line {line_number}."
            ) from exc

        state = raw_state.casefold().strip()
        if state not in _RESEARCH_JOB_STATES:
            raise ResearchWorkspaceProtocolError(
                f"The Research list response has an unrecognized state at line {line_number}."
            )
        if not stage.strip():
            raise ResearchWorkspaceProtocolError(
                f"The Research list response is missing a stage at line {line_number}."
            )

        if raw_coverage == "-":
            coverage = None
        else:
            try:
                coverage = float(raw_coverage)
            except ValueError as exc:
                raise ResearchWorkspaceProtocolError(
                    f"The Research list response has invalid coverage at line {line_number}."
                ) from exc
            if not math.isfinite(coverage) or not 0.0 <= coverage <= 1.0:
                raise ResearchWorkspaceProtocolError(
                    f"The Research list response has invalid coverage at line {line_number}."
                )

        entries.append(
            ResearchJobListEntry(
                job_id=job_id,
                state=state,
                stage=stage,
                coverage=coverage,
                query=query,
            )
        )
    return tuple(entries)


def parse_research_enqueue_receipt(output: str) -> str:
    """Return the exact queued job ID from a successful enqueue helper response."""
    job_ids: list[str] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line.startswith("JOB_QUEUED"):
            continue
        parts = line.split()
        if len(parts) != 2 or parts[0] != "JOB_QUEUED":
            raise ResearchWorkspaceProtocolError(
                "The Research enqueue response could not be verified."
            )
        job_ids.append(_canonical_uuid(parts[1], field="queued job ID"))

    if len(job_ids) != 1:
        raise ResearchWorkspaceProtocolError(
            "The Research enqueue response could not be verified."
        )
    return job_ids[0]


def parse_research_cancel_receipt(
    output: str,
    *,
    expected_job_id: str,
) -> ResearchCancelReceipt:
    """Bind a cancellation response to the exact requested Research run."""
    parts = output.strip().split()
    if len(parts) != 3 or parts[0] != "JOB_CANCEL":
        raise ResearchWorkspaceProtocolError(
            "The Research cancellation response could not be verified."
        )

    job_id = _canonical_uuid(parts[1], field="cancelled job ID")
    expected = _canonical_uuid(expected_job_id, field="requested job ID")
    if job_id != expected:
        raise ResearchWorkspaceProtocolError(
            "The Research cancellation response belongs to another run."
        )

    state = parts[2].casefold().strip()
    if state not in _CANCEL_RECEIPT_STATES:
        raise ResearchWorkspaceProtocolError(
            "The Research cancellation response returned an unexpected state."
        )
    return ResearchCancelReceipt(job_id=job_id, state=state)
