"""Deterministic comparison of comparable persisted ResearchResults.

The comparison is deliberately read-only and lexical/provenance based. It never asks a
model to decide whether two differently worded findings are semantically equivalent.
That keeps the "what changed" view auditable and prevents UI-only synthetic state.
"""

from __future__ import annotations

import json
import uuid
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.storage.database import SQLiteDatabase


class ResearchComparisonError(ValueError):
    """Raised when two persisted ResearchResults are not safely comparable."""


@dataclass(frozen=True, slots=True)
class ResearchResultDelta:
    """Exact persisted text/provenance delta between two comparable results."""

    query: str
    baseline_result_id: uuid.UUID
    current_result_id: uuid.UUID
    baseline_job_id: uuid.UUID
    current_job_id: uuid.UUID
    baseline_snapshot_commit_seq: int
    current_snapshot_commit_seq: int
    baseline_model_signature_id: uuid.UUID | None
    current_model_signature_id: uuid.UUID | None
    baseline_coverage_ratio: float
    current_coverage_ratio: float
    baseline_summary: str
    current_summary: str
    baseline_uncertainty: str
    current_uncertainty: str
    added_findings: tuple[str, ...]
    removed_findings: tuple[str, ...]
    added_contradictions: tuple[str, ...]
    removed_contradictions: tuple[str, ...]
    added_source_ids: tuple[uuid.UUID, ...]
    removed_source_ids: tuple[uuid.UUID, ...]

    @property
    def summary_changed(self) -> bool:
        return self.baseline_summary != self.current_summary

    @property
    def uncertainty_changed(self) -> bool:
        return self.baseline_uncertainty != self.current_uncertainty

    @property
    def model_signature_changed(self) -> bool:
        return self.baseline_model_signature_id != self.current_model_signature_id

    def as_dict(self) -> dict[str, object]:
        """Return the transport-neutral desktop payload without inferred semantics."""
        return {
            "available": True,
            "comparison_mode": "exact_persisted_text_and_provenance",
            "query": self.query,
            "baseline": {
                "result_id": str(self.baseline_result_id),
                "job_id": str(self.baseline_job_id),
                "snapshot_commit_seq": self.baseline_snapshot_commit_seq,
                "model_signature_id": (
                    None
                    if self.baseline_model_signature_id is None
                    else str(self.baseline_model_signature_id)
                ),
                "coverage_ratio": self.baseline_coverage_ratio,
                "summary": self.baseline_summary,
                "uncertainty": self.baseline_uncertainty,
            },
            "current": {
                "result_id": str(self.current_result_id),
                "job_id": str(self.current_job_id),
                "snapshot_commit_seq": self.current_snapshot_commit_seq,
                "model_signature_id": (
                    None
                    if self.current_model_signature_id is None
                    else str(self.current_model_signature_id)
                ),
                "coverage_ratio": self.current_coverage_ratio,
                "summary": self.current_summary,
                "uncertainty": self.current_uncertainty,
            },
            "changes": {
                "summary_changed": self.summary_changed,
                "uncertainty_changed": self.uncertainty_changed,
                "model_signature_changed": self.model_signature_changed,
                "added_findings": list(self.added_findings),
                "removed_findings": list(self.removed_findings),
                "added_contradictions": list(self.added_contradictions),
                "removed_contradictions": list(self.removed_contradictions),
                "added_source_ids": [str(item) for item in self.added_source_ids],
                "removed_source_ids": [str(item) for item in self.removed_source_ids],
            },
        }


@dataclass(frozen=True, slots=True)
class _ResultRow:
    result_id: uuid.UUID
    job_id: uuid.UUID
    query: str
    mode: str
    domains: tuple[str, ...]
    project_ids: tuple[str, ...]
    source_types: tuple[str, ...]
    time_start_us: int | None
    time_end_us: int | None
    coverage_target: float
    scope_state: str
    snapshot_commit_seq: int
    synthesis_pipeline_version: str
    model_signature_id: uuid.UUID | None
    scope_created_at_us: int


class ResearchComparisonService:
    """Compare immutable ResearchResults without creating another search/index layer."""

    def __init__(
        self,
        *,
        database: SQLiteDatabase,
        result_view: Callable[[uuid.UUID], Mapping[str, Any]],
    ) -> None:
        self.database = database
        self.result_view = result_view

    def compare_previous(
        self,
        current_identifier: uuid.UUID,
    ) -> ResearchResultDelta | None:
        """Compare with the newest earlier completed run having the same stable scope."""
        current = self._result_row(current_identifier)
        self._require_completed(current, label="current")

        rows = self.database.connection.execute(
            """
            SELECT
                rr.result_id,
                rs.created_at_us AS scope_created_at_us,
                rr.snapshot_commit_seq,
                rr.model_signature_id,
                rr.synthesis_pipeline_version,
                rs.job_id,
                rs.query_text,
                rs.mode,
                rs.domains_json,
                rs.project_ids_json,
                rs.source_types_json,
                rs.time_start_us,
                rs.time_end_us,
                rs.coverage_target,
                rs.state AS scope_state
            FROM research_results AS rr
            JOIN research_scopes AS rs ON rs.scope_id = rr.scope_id
            WHERE rs.state = 'completed'
              AND (
                    rs.created_at_us < ?
                    OR (
                        rs.created_at_us = ?
                        AND rr.result_id < ?
                    )
                  )
            ORDER BY rs.created_at_us DESC, rr.result_id DESC
            """,
            (
                current.scope_created_at_us,
                current.scope_created_at_us,
                uuid_to_blob(current.result_id),
            ),
        ).fetchall()
        for row in rows:
            candidate = _result_row_from_sql(row)
            if _comparison_key(candidate) == _comparison_key(current):
                return self._compare_rows(
                    baseline=candidate,
                    current=current,
                )
        return None

    def compare(
        self,
        current_identifier: uuid.UUID,
        *,
        baseline_identifier: uuid.UUID,
    ) -> ResearchResultDelta:
        """Compare an explicit baseline/current pair after fail-closed scope checks."""
        current = self._result_row(current_identifier)
        baseline = self._result_row(baseline_identifier)
        self._require_completed(current, label="current")
        self._require_completed(baseline, label="baseline")
        if baseline.result_id == current.result_id:
            raise ResearchComparisonError(
                "Research comparison requires two different persisted results."
            )
        if _comparison_key(baseline) != _comparison_key(current):
            raise ResearchComparisonError(
                "Research results are not comparable: query, mode, stable scope filters, "
                "coverage target, or synthesis pipeline differ."
            )
        if (
            baseline.scope_created_at_us > current.scope_created_at_us
            or (
                baseline.scope_created_at_us == current.scope_created_at_us
                and baseline.result_id.bytes >= current.result_id.bytes
            )
        ):
            raise ResearchComparisonError(
                "Research comparison baseline must precede the current result."
            )
        return self._compare_rows(
            baseline=baseline,
            current=current,
        )

    def _result_row(self, identifier: uuid.UUID) -> _ResultRow:
        if not isinstance(identifier, uuid.UUID):
            raise TypeError("Research comparison identifier must be a UUID.")
        identifier_blob = uuid_to_blob(identifier)
        row = self.database.connection.execute(
            """
            SELECT
                rr.result_id,
                rs.created_at_us AS scope_created_at_us,
                rr.snapshot_commit_seq,
                rr.model_signature_id,
                rr.synthesis_pipeline_version,
                rs.job_id,
                rs.query_text,
                rs.mode,
                rs.domains_json,
                rs.project_ids_json,
                rs.source_types_json,
                rs.time_start_us,
                rs.time_end_us,
                rs.coverage_target,
                rs.state AS scope_state
            FROM research_results AS rr
            JOIN research_scopes AS rs ON rs.scope_id = rr.scope_id
            WHERE rr.result_id = ?
               OR rr.scope_id = ?
               OR rs.job_id = ?
            """,
            (identifier_blob, identifier_blob, identifier_blob),
        ).fetchone()
        if row is None:
            raise ResearchComparisonError(
                f"No persisted ResearchResult matches {identifier}."
            )
        return _result_row_from_sql(row)

    @staticmethod
    def _require_completed(row: _ResultRow, *, label: str) -> None:
        if row.scope_state != "completed":
            raise ResearchComparisonError(
                f"Research comparison {label} result is not completed."
            )

    def _compare_rows(
        self,
        *,
        baseline: _ResultRow,
        current: _ResultRow,
    ) -> ResearchResultDelta:
        baseline_view = self.result_view(baseline.result_id)
        current_view = self.result_view(current.result_id)

        baseline_content = _content_view(baseline_view, label="baseline")
        current_content = _content_view(current_view, label="current")
        baseline_sources = _evidence_source_ids(
            baseline_view,
            label="baseline",
        )
        current_sources = _evidence_source_ids(
            current_view,
            label="current",
        )
        baseline_coverage = _coverage_ratio(
            baseline_view,
            label="baseline",
        )
        current_coverage = _coverage_ratio(
            current_view,
            label="current",
        )

        added_findings, removed_findings = _sequence_delta(
            baseline_content["findings"],
            current_content["findings"],
        )
        added_contradictions, removed_contradictions = _sequence_delta(
            baseline_content["contradictions"],
            current_content["contradictions"],
        )

        return ResearchResultDelta(
            query=current.query,
            baseline_result_id=baseline.result_id,
            current_result_id=current.result_id,
            baseline_job_id=baseline.job_id,
            current_job_id=current.job_id,
            baseline_snapshot_commit_seq=baseline.snapshot_commit_seq,
            current_snapshot_commit_seq=current.snapshot_commit_seq,
            baseline_model_signature_id=baseline.model_signature_id,
            current_model_signature_id=current.model_signature_id,
            baseline_coverage_ratio=baseline_coverage,
            current_coverage_ratio=current_coverage,
            baseline_summary=baseline_content["summary"],
            current_summary=current_content["summary"],
            baseline_uncertainty=baseline_content["uncertainty"],
            current_uncertainty=current_content["uncertainty"],
            added_findings=added_findings,
            removed_findings=removed_findings,
            added_contradictions=added_contradictions,
            removed_contradictions=removed_contradictions,
            added_source_ids=tuple(
                sorted(current_sources - baseline_sources, key=lambda item: item.bytes)
            ),
            removed_source_ids=tuple(
                sorted(baseline_sources - current_sources, key=lambda item: item.bytes)
            ),
        )


def _result_row_from_sql(row: Any) -> _ResultRow:
    return _ResultRow(
        result_id=uuid_from_blob(bytes(row["result_id"])),
        job_id=uuid_from_blob(bytes(row["job_id"])),
        query=str(row["query_text"]),
        mode=str(row["mode"]),
        domains=_json_text_array(row["domains_json"], "domains_json"),
        project_ids=_json_text_array(row["project_ids_json"], "project_ids_json"),
        source_types=_json_text_array(row["source_types_json"], "source_types_json"),
        time_start_us=(
            None if row["time_start_us"] is None else int(row["time_start_us"])
        ),
        time_end_us=(
            None if row["time_end_us"] is None else int(row["time_end_us"])
        ),
        coverage_target=float(row["coverage_target"]),
        scope_state=str(row["scope_state"]),
        snapshot_commit_seq=int(row["snapshot_commit_seq"]),
        synthesis_pipeline_version=str(row["synthesis_pipeline_version"]),
        model_signature_id=(
            None
            if row["model_signature_id"] is None
            else uuid_from_blob(bytes(row["model_signature_id"]))
        ),
        scope_created_at_us=int(row["scope_created_at_us"]),
    )


def _comparison_key(row: _ResultRow) -> tuple[object, ...]:
    # Explicit Source IDs are intentionally not part of this key: a later run is
    # useful precisely because its captured evidence set may have changed.
    return (
        " ".join(row.query.split()),
        row.mode,
        row.domains,
        row.project_ids,
        row.source_types,
        row.time_start_us,
        row.time_end_us,
        row.coverage_target,
        row.synthesis_pipeline_version,
    )


def _json_text_array(raw: object, label: str) -> tuple[str, ...]:
    if not isinstance(raw, str):
        raise ResearchComparisonError(f"Research comparison {label} is not JSON text.")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ResearchComparisonError(
            f"Research comparison {label} is invalid JSON."
        ) from exc
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ResearchComparisonError(
            f"Research comparison {label} must contain a string array."
        )
    return tuple(value)


def _content_view(
    view: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    raw = view.get("content")
    if not isinstance(raw, Mapping):
        raise ResearchComparisonError(
            f"Research comparison {label} result content is invalid."
        )
    summary = raw.get("summary")
    uncertainty = raw.get("uncertainty", "")
    if not isinstance(summary, str) or not summary.strip():
        raise ResearchComparisonError(
            f"Research comparison {label} summary is missing."
        )
    if not isinstance(uncertainty, str):
        raise ResearchComparisonError(
            f"Research comparison {label} uncertainty is invalid."
        )
    return {
        "summary": summary,
        "uncertainty": uncertainty,
        "findings": _text_sequence(raw.get("findings", []), f"{label} findings"),
        "contradictions": _text_sequence(
            raw.get("contradictions", []),
            f"{label} contradictions",
        ),
    }


def _text_sequence(value: object, label: str) -> tuple[str, ...]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ResearchComparisonError(
            f"Research comparison {label} must contain non-empty text values."
        )
    return tuple(value)


def _coverage_ratio(
    view: Mapping[str, Any],
    *,
    label: str,
) -> float:
    raw = view.get("coverage")
    if not isinstance(raw, Mapping):
        raise ResearchComparisonError(
            f"Research comparison {label} coverage is invalid."
        )
    ratio = raw.get("coverage_ratio")
    if (
        isinstance(ratio, bool)
        or not isinstance(ratio, (int, float))
        or not 0.0 <= float(ratio) <= 1.0
    ):
        raise ResearchComparisonError(
            f"Research comparison {label} coverage ratio is invalid."
        )
    return float(ratio)


def _evidence_source_ids(
    view: Mapping[str, Any],
    *,
    label: str,
) -> set[uuid.UUID]:
    raw = view.get("evidence")
    if not isinstance(raw, Mapping):
        raise ResearchComparisonError(
            f"Research comparison {label} evidence is invalid."
        )
    result: set[uuid.UUID] = set()
    for plural in ("findings", "contradictions"):
        rows = raw.get(plural, [])
        if not isinstance(rows, list):
            raise ResearchComparisonError(
                f"Research comparison {label} evidence {plural} is invalid."
            )
        for item in rows:
            if not isinstance(item, Mapping):
                raise ResearchComparisonError(
                    f"Research comparison {label} evidence item is invalid."
                )
            source_ids = item.get("source_ids", [])
            if not isinstance(source_ids, list) or any(
                not isinstance(source_id, str) for source_id in source_ids
            ):
                raise ResearchComparisonError(
                    f"Research comparison {label} evidence source IDs are invalid."
                )
            try:
                result.update(uuid.UUID(source_id) for source_id in source_ids)
            except ValueError as exc:
                raise ResearchComparisonError(
                    f"Research comparison {label} evidence source ID is invalid."
                ) from exc
    return result


def _sequence_delta(
    baseline: tuple[str, ...],
    current: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return additions/removals while preserving order and duplicate counts."""
    remaining_baseline = Counter(baseline)
    added: list[str] = []
    for item in current:
        if remaining_baseline[item] > 0:
            remaining_baseline[item] -= 1
        else:
            added.append(item)

    remaining_current = Counter(current)
    removed: list[str] = []
    for item in baseline:
        if remaining_current[item] > 0:
            remaining_current[item] -= 1
        else:
            removed.append(item)
    return tuple(added), tuple(removed)
