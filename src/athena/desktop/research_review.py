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

@dataclass(frozen=True)
class ResearchDeltaReview:
    available: bool
    reason: str
    query: str
    baseline_result_id: str
    current_result_id: str
    baseline_snapshot_commit_seq: int | None
    current_snapshot_commit_seq: int | None
    baseline_model_signature_id: str
    current_model_signature_id: str
    baseline_coverage_ratio: float | None
    current_coverage_ratio: float | None
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


def _optional_text(value: object, label: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ResearchReviewError(f"Research comparison {label} is invalid.")
    return value


def _bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ResearchReviewError(f"Research comparison {label} is invalid.")
    return value


def _text_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ResearchReviewError(f"Research comparison {label} is invalid.")
    return tuple(value)


def parse_research_delta_review(output: str) -> ResearchDeltaReview:
    """Parse exact JSON emitted by the Research compare command."""
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ResearchReviewError("Research comparison output is not valid JSON.") from exc
    root = _object(payload, "comparison payload")
    available = root.get("available")
    if not isinstance(available, bool):
        raise ResearchReviewError("Research comparison availability is invalid.")
    if not available:
        reason = _text(root.get("reason"), "comparison reason")
        return ResearchDeltaReview(
            available=False,
            reason=reason,
            query="",
            baseline_result_id="",
            current_result_id="",
            baseline_snapshot_commit_seq=None,
            current_snapshot_commit_seq=None,
            baseline_model_signature_id="",
            current_model_signature_id="",
            baseline_coverage_ratio=None,
            current_coverage_ratio=None,
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

    if root.get("comparison_mode") != "exact_persisted_text_and_provenance":
        raise ResearchReviewError("Research comparison mode is unsupported.")
    baseline = _object(root.get("baseline"), "comparison baseline")
    current = _object(root.get("current"), "comparison current")
    changes = _object(root.get("changes"), "comparison changes")
    return ResearchDeltaReview(
        available=True,
        reason="",
        query=_text(root.get("query"), "comparison query"),
        baseline_result_id=_text(
            baseline.get("result_id"),
            "comparison baseline result_id",
        ),
        current_result_id=_text(
            current.get("result_id"),
            "comparison current result_id",
        ),
        baseline_snapshot_commit_seq=_optional_int(
            baseline.get("snapshot_commit_seq"),
            "comparison baseline snapshot commit",
        ),
        current_snapshot_commit_seq=_optional_int(
            current.get("snapshot_commit_seq"),
            "comparison current snapshot commit",
        ),
        baseline_model_signature_id=_optional_text(
            baseline.get("model_signature_id"),
            "baseline model signature",
        ),
        current_model_signature_id=_optional_text(
            current.get("model_signature_id"),
            "current model signature",
        ),
        baseline_coverage_ratio=_optional_ratio(baseline.get("coverage_ratio")),
        current_coverage_ratio=_optional_ratio(current.get("coverage_ratio")),
        baseline_summary=_text(
            baseline.get("summary"),
            "comparison baseline summary",
        ),
        current_summary=_text(
            current.get("summary"),
            "comparison current summary",
        ),
        baseline_uncertainty=_optional_text(
            baseline.get("uncertainty"),
            "baseline uncertainty",
        ),
        current_uncertainty=_optional_text(
            current.get("uncertainty"),
            "current uncertainty",
        ),
        summary_changed=_bool(changes.get("summary_changed"), "summary changed flag"),
        uncertainty_changed=_bool(
            changes.get("uncertainty_changed"),
            "uncertainty changed flag",
        ),
        model_signature_changed=_bool(
            changes.get("model_signature_changed"),
            "model signature changed flag",
        ),
        added_findings=_text_tuple(changes.get("added_findings"), "added findings"),
        removed_findings=_text_tuple(
            changes.get("removed_findings"),
            "removed findings",
        ),
        added_contradictions=_text_tuple(
            changes.get("added_contradictions"),
            "added contradictions",
        ),
        removed_contradictions=_text_tuple(
            changes.get("removed_contradictions"),
            "removed contradictions",
        ),
        added_source_ids=_text_tuple(
            changes.get("added_source_ids"),
            "added source IDs",
        ),
        removed_source_ids=_text_tuple(
            changes.get("removed_source_ids"),
            "removed source IDs",
        ),
    )


def _delta_section(
    title: str,
    *,
    added: tuple[str, ...],
    removed: tuple[str, ...],
    empty: str,
) -> list[str]:
    lines = ["", title]
    if not added and not removed:
        lines.append(empty)
        return lines
    lines.extend(f"+ {item}" for item in added)
    lines.extend(f"- {item}" for item in removed)
    return lines


def render_research_delta_review(review: ResearchDeltaReview) -> str:
    """Render an exact persisted result delta without semantic inference."""
    if not review.available:
        return f"RESEARCH CHANGES\n\n{review.reason}"

    baseline = f"Result {_short_id(review.baseline_result_id)}"
    current = f"Result {_short_id(review.current_result_id)}"
    if review.baseline_snapshot_commit_seq is not None:
        baseline += f" · Snapshot commit {review.baseline_snapshot_commit_seq}"
    if review.current_snapshot_commit_seq is not None:
        current += f" · Snapshot commit {review.current_snapshot_commit_seq}"

    lines = [
        "RESEARCH CHANGES",
        review.query,
        "",
        "BASELINE → CURRENT",
        baseline,
        current,
    ]
    if (
        review.baseline_coverage_ratio is not None
        and review.current_coverage_ratio is not None
    ):
        before = review.baseline_coverage_ratio * 100
        after = review.current_coverage_ratio * 100
        delta = after - before
        lines.extend(
            (
                "",
                "COVERAGE",
                f"{before:.1f}% → {after:.1f}% ({delta:+.1f} percentage points)",
            )
        )

    lines.extend(
        _delta_section(
            "FINDINGS",
            added=review.added_findings,
            removed=review.removed_findings,
            empty="No exact finding text changes.",
        )
    )
    lines.extend(
        _delta_section(
            "CONTRADICTIONS",
            added=review.added_contradictions,
            removed=review.removed_contradictions,
            empty="No exact contradiction text changes.",
        )
    )
    lines.extend(
        _delta_section(
            "EVIDENCE SOURCES",
            added=tuple(_short_id(item) for item in review.added_source_ids),
            removed=tuple(_short_id(item) for item in review.removed_source_ids),
            empty="No source identities changed in persisted finding-level provenance.",
        )
    )

    if review.summary_changed:
        lines.extend(
            (
                "",
                "SUMMARY CHANGED",
                "Before · " + review.baseline_summary,
                "Now · " + review.current_summary,
            )
        )
    else:
        lines.extend(("", "SUMMARY", "No exact summary text change."))

    if review.uncertainty_changed:
        lines.extend(
            (
                "",
                "UNCERTAINTY CHANGED",
                "Before · " + (review.baseline_uncertainty or "None recorded"),
                "Now · " + (review.current_uncertainty or "None recorded"),
            )
        )
    else:
        lines.extend(("", "UNCERTAINTY", "No exact uncertainty text change."))

    lines.extend(
        (
            "",
            "COMPARISON METHOD",
            "Exact persisted text and provenance only. Reworded text is reported "
            "as removed plus added; no model decides semantic equivalence.",
        )
    )
    if review.model_signature_changed:
        lines.append(
            "Model signature changed between runs; wording changes may reflect "
            "that model/configuration change."
        )
    return "\n".join(lines)

