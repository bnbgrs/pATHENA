"""Validated process-boundary responses for the native Research workspace."""

from __future__ import annotations

import json
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


@dataclass(frozen=True, slots=True)
class ResearchComparisonReceipt:
    available: bool
    comparison_mode: str
    current_job_id: str
    baseline_job_id: str | None
    query: str
    baseline_result_id: str | None
    current_result_id: str | None
    baseline_snapshot_commit_seq: int | None
    current_snapshot_commit_seq: int | None
    baseline_model_signature_id: str | None
    current_model_signature_id: str | None
    baseline_coverage: float | None
    current_coverage: float | None
    baseline_summary: str
    current_summary: str
    baseline_uncertainty: str
    current_uncertainty: str
    summary_changed: bool
    uncertainty_changed: bool
    model_signature_changed: bool
    added_findings: tuple[str, ...]
    removed_findings: tuple[str, ...]
    added_contradictions: tuple[str, ...]
    removed_contradictions: tuple[str, ...]
    added_source_ids: tuple[str, ...]
    removed_source_ids: tuple[str, ...]


_COMPARISON_MODE = "exact_persisted_text_and_provenance"


def _canonical_uuid(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise ResearchWorkspaceProtocolError(
            f"The Research response has an invalid {field}."
        )
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

def _comparison_string_list(
    value: object,
    *,
    field: str,
    uuid_items: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ResearchWorkspaceProtocolError(
            f"The Research comparison response has invalid {field}."
        )
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ResearchWorkspaceProtocolError(
                f"The Research comparison response has invalid {field}."
            )
        if uuid_items:
            item = _canonical_uuid(item, field=field)
        items.append(item)
    return tuple(items)


def _comparison_coverage(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResearchWorkspaceProtocolError(
            f"The Research comparison response has invalid {field}."
        )
    coverage = float(value)
    if not math.isfinite(coverage) or not 0.0 <= coverage <= 1.0:
        raise ResearchWorkspaceProtocolError(
            f"The Research comparison response has invalid {field}."
        )
    return coverage


def parse_research_comparison_receipt(
    output: str,
    *,
    expected_job_id: str,
) -> ResearchComparisonReceipt:
    """Validate one exact persisted Research comparison response."""
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].startswith("RESEARCH_COMPARE "):
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response could not be verified."
        )
    try:
        payload = json.loads(lines[0][len("RESEARCH_COMPARE ") :])
    except json.JSONDecodeError as exc:
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response is not valid JSON."
        ) from exc
    if not isinstance(payload, dict):
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response must be an object."
        )

    available = payload.get("available")
    if not isinstance(available, bool):
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response has invalid availability."
        )
    mode = payload.get("comparison_mode")
    if mode != _COMPARISON_MODE:
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response has an unexpected comparison mode."
        )
    expected = _canonical_uuid(expected_job_id, field="requested job ID")

    if not available:
        current_job_id = _canonical_uuid(
            payload.get("current_job_id"),
            field="current job ID",
        )
        if current_job_id != expected:
            raise ResearchWorkspaceProtocolError(
                "The Research comparison response belongs to another run."
            )
        return ResearchComparisonReceipt(
            available=False,
            comparison_mode=mode,
            current_job_id=current_job_id,
            baseline_job_id=None,
            query="",
            baseline_result_id=None,
            current_result_id=None,
            baseline_snapshot_commit_seq=None,
            current_snapshot_commit_seq=None,
            baseline_model_signature_id=None,
            current_model_signature_id=None,
            baseline_coverage=None,
            current_coverage=None,
            baseline_summary="",
            current_summary="",
            baseline_uncertainty="",
            current_uncertainty="",
            summary_changed=False,
            uncertainty_changed=False,
            model_signature_changed=False,
            added_findings=(),
            removed_findings=(),
            added_contradictions=(),
            removed_contradictions=(),
            added_source_ids=(),
            removed_source_ids=(),
        )

    baseline = payload.get("baseline")
    current = payload.get("current")
    changes = payload.get("changes")
    query = payload.get("query")
    if (
        not isinstance(baseline, dict)
        or not isinstance(current, dict)
        or not isinstance(changes, dict)
        or not isinstance(query, str)
    ):
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response is missing persisted comparison fields."
        )

    baseline_job_id = _canonical_uuid(
        baseline.get("job_id"),
        field="baseline job ID",
    )
    current_job_id = _canonical_uuid(
        current.get("job_id"),
        field="current job ID",
    )
    if current_job_id != expected:
        raise ResearchWorkspaceProtocolError(
            "The Research comparison response belongs to another run."
        )

    normalized_results: dict[str, str] = {}
    normalized_snapshots: dict[str, int] = {}
    normalized_models: dict[str, str | None] = {}
    for container, label in ((baseline, "baseline"), (current, "current")):
        normalized_results[label] = _canonical_uuid(
            container.get("result_id"),
            field=f"{label} result ID",
        )
        snapshot = container.get("snapshot_commit_seq")
        if isinstance(snapshot, bool) or not isinstance(snapshot, int) or snapshot < 0:
            raise ResearchWorkspaceProtocolError(
                f"The Research comparison response has invalid {label} snapshot."
            )
        normalized_snapshots[label] = snapshot
        model_signature = container.get("model_signature_id")
        if model_signature is None:
            normalized_models[label] = None
        else:
            normalized_models[label] = _canonical_uuid(
                model_signature,
                field=f"{label} model signature ID",
            )
        if not isinstance(container.get("summary"), str) or not isinstance(
            container.get("uncertainty"),
            str,
        ):
            raise ResearchWorkspaceProtocolError(
                f"The Research comparison response has invalid {label} text."
            )

    flags: dict[str, bool] = {}
    for field in (
        "summary_changed",
        "uncertainty_changed",
        "model_signature_changed",
    ):
        value = changes.get(field)
        if not isinstance(value, bool):
            raise ResearchWorkspaceProtocolError(
                f"The Research comparison response has invalid {field}."
            )
        flags[field] = value

    return ResearchComparisonReceipt(
        available=True,
        comparison_mode=mode,
        current_job_id=current_job_id,
        baseline_job_id=baseline_job_id,
        query=query,
        baseline_result_id=normalized_results["baseline"],
        current_result_id=normalized_results["current"],
        baseline_snapshot_commit_seq=normalized_snapshots["baseline"],
        current_snapshot_commit_seq=normalized_snapshots["current"],
        baseline_model_signature_id=normalized_models["baseline"],
        current_model_signature_id=normalized_models["current"],
        baseline_coverage=_comparison_coverage(
            baseline.get("coverage_ratio"),
            field="baseline coverage",
        ),
        current_coverage=_comparison_coverage(
            current.get("coverage_ratio"),
            field="current coverage",
        ),
        baseline_summary=baseline["summary"],
        current_summary=current["summary"],
        baseline_uncertainty=baseline["uncertainty"],
        current_uncertainty=current["uncertainty"],
        summary_changed=flags["summary_changed"],
        uncertainty_changed=flags["uncertainty_changed"],
        model_signature_changed=flags["model_signature_changed"],
        added_findings=_comparison_string_list(
            changes.get("added_findings"),
            field="added findings",
        ),
        removed_findings=_comparison_string_list(
            changes.get("removed_findings"),
            field="removed findings",
        ),
        added_contradictions=_comparison_string_list(
            changes.get("added_contradictions"),
            field="added contradictions",
        ),
        removed_contradictions=_comparison_string_list(
            changes.get("removed_contradictions"),
            field="removed contradictions",
        ),
        added_source_ids=_comparison_string_list(
            changes.get("added_source_ids"),
            field="added source IDs",
            uuid_items=True,
        ),
        removed_source_ids=_comparison_string_list(
            changes.get("removed_source_ids"),
            field="removed source IDs",
            uuid_items=True,
        ),
    )

