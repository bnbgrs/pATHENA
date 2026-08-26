"""Structured, read-only presentation of persisted ResearchResult payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


class ResearchReviewError(ValueError):
    """Raised when a CLI payload cannot be represented without inventing data."""


@dataclass(frozen=True)
class EvidenceReview:
    kind: str
    ordinal: int
    text: str
    source_ids: tuple[str, ...]
    anchor_ids: tuple[str, ...]
    artifact_ids: tuple[str, ...]


@dataclass(frozen=True)
class ResearchResultReview:
    result_id: str
    job_id: str
    query: str
    scope_state: str
    snapshot_commit_seq: int | None
    summary: str
    uncertainty: str
    candidate_total: int | None
    processed_count: int | None
    successful_count: int | None
    coverage_ratio: float | None
    evidence: tuple[EvidenceReview, ...]


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ResearchReviewError(f"ResearchResult {label} is not an object.")
    return value


def _text(value: object, label: str, *, optional: bool = False) -> str:
    if optional and value is None:
        return ""
    if not isinstance(value, str) or not value.strip():
        raise ResearchReviewError(f"ResearchResult {label} is missing.")
    return value.strip()


def _optional_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ResearchReviewError(f"ResearchResult {label} is invalid.")
    return value


def _optional_ratio(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResearchReviewError("ResearchResult coverage ratio is invalid.")
    ratio = float(value)
    if not 0.0 <= ratio <= 1.0:
        raise ResearchReviewError("ResearchResult coverage ratio is outside 0..1.")
    return ratio


def _ids(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ResearchReviewError(f"ResearchResult {label} is invalid.")
    return tuple(value)


def parse_research_result_review(output: str) -> ResearchResultReview:
    """Parse the exact JSON emitted by ``research_results_cli result``."""
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ResearchReviewError("ResearchResult output is not valid JSON.") from exc
    root = _object(payload, "payload")
    content = _object(root.get("content"), "content")
    coverage = _object(root.get("coverage", {}), "coverage")
    evidence_root = _object(root.get("evidence", {}), "evidence")

    evidence: list[EvidenceReview] = []
    for plural, kind in (("findings", "finding"), ("contradictions", "contradiction")):
        rows = evidence_root.get(plural, [])
        if not isinstance(rows, list):
            raise ResearchReviewError(f"ResearchResult evidence {plural} is invalid.")
        for row in rows:
            item = _object(row, f"evidence {kind}")
            ordinal = _optional_int(item.get("ordinal"), f"{kind} ordinal")
            if ordinal is None:
                raise ResearchReviewError(f"ResearchResult {kind} ordinal is missing.")
            evidence.append(
                EvidenceReview(
                    kind=kind,
                    ordinal=ordinal,
                    text=_text(item.get("text"), f"{kind} text"),
                    source_ids=_ids(item.get("source_ids", []), f"{kind} sources"),
                    anchor_ids=_ids(item.get("source_anchor_ids", []), f"{kind} anchors"),
                    artifact_ids=_ids(
                        item.get("source_analysis_artifact_ids", []),
                        f"{kind} artifacts",
                    ),
                )
            )

    evidence.sort(key=lambda item: (item.kind, item.ordinal))
    return ResearchResultReview(
        result_id=_text(root.get("result_id"), "result_id"),
        job_id=_text(root.get("job_id"), "job_id"),
        query=_text(root.get("query"), "query"),
        scope_state=_text(root.get("scope_state"), "scope_state"),
        snapshot_commit_seq=_optional_int(
            root.get("snapshot_commit_seq"), "snapshot commit"
        ),
        summary=_text(content.get("summary"), "summary"),
        uncertainty=_text(content.get("uncertainty"), "uncertainty", optional=True),
        candidate_total=_optional_int(coverage.get("candidate_total"), "candidate total"),
        processed_count=_optional_int(coverage.get("processed_count"), "processed count"),
        successful_count=_optional_int(
            coverage.get("successful_count"), "successful count"
        ),
        coverage_ratio=_optional_ratio(coverage.get("coverage_ratio")),
        evidence=tuple(evidence),
    )


def _short_id(value: str) -> str:
    return value[:8].upper()


def render_research_result_review(review: ResearchResultReview) -> str:
    """Render real result fields as a quiet, provenance-forward review."""
    lines = [
        "RESEARCH RESULT",
        review.query,
        "",
        "SYNTHESIS",
        review.summary,
    ]
    if review.uncertainty:
        lines.extend(("", "UNCERTAINTY", review.uncertainty))

    coverage_parts: list[str] = []
    if review.coverage_ratio is not None:
        coverage_parts.append(f"{review.coverage_ratio * 100:.1f}% covered")
    if review.processed_count is not None and review.candidate_total is not None:
        coverage_parts.append(
            f"{review.processed_count}/{review.candidate_total} sources processed"
        )
    if review.successful_count is not None:
        coverage_parts.append(f"{review.successful_count} successful")
    if coverage_parts:
        lines.extend(("", "COVERAGE", " · ".join(coverage_parts)))

    lines.extend(("", "EVIDENCE & PROVENANCE"))
    if not review.evidence:
        lines.append("No finding-level provenance was persisted for this result.")
    for item in review.evidence:
        label = "FINDING" if item.kind == "finding" else "CONTRADICTION"
        lines.extend(
            (
                "",
                f"{label} {item.ordinal + 1}",
                item.text,
                (
                    f"{len(item.source_ids)} sources · {len(item.anchor_ids)} anchors · "
                    f"{len(item.artifact_ids)} analysis artifacts"
                ),
            )
        )
        if item.source_ids:
            lines.append("Sources · " + ", ".join(_short_id(value) for value in item.source_ids))

    identity = f"Result {_short_id(review.result_id)} · Run {_short_id(review.job_id)}"
    if review.snapshot_commit_seq is not None:
        identity += f" · Snapshot commit {review.snapshot_commit_seq}"
    lines.extend(("", identity, f"State · {review.scope_state}"))
    return "\n".join(lines)
