"""Persistent value objects for hierarchical large-source analysis."""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SourceAnalysisState(str, Enum):
    """Durable state of one source analysis."""

    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"


class AnalysisStage(str, Enum):
    """Hierarchical work stages."""

    MAP = "map"
    REDUCE = "reduce"
    FINAL = "final"


class AnalysisWorkState(str, Enum):
    """Durable state of one idempotent semantic work unit."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SPLIT = "split"


class AnalysisInputKind(str, Enum):
    """Kinds of immutable inputs accepted by an analysis work unit."""

    SOURCE_ANCHOR = "source_anchor"
    ARTIFACT = "artifact"


def _require_uuid(value: object, label: str) -> None:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")


def _require_int(value: object, label: str, *, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < minimum:
        raise ValueError(f"{label} must be >= {minimum}.")


def _require_nonempty_text(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value.strip():
        raise ValueError(f"{label} must not be empty.")


def _require_sha256(value: object, label: str) -> None:
    if not isinstance(value, bytes):
        raise TypeError(f"{label} must be bytes.")
    if len(value) != 32:
        raise ValueError(f"{label} must be a 32-byte SHA-256 digest.")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant {value!r} is not permitted.")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key {key!r} is not permitted.")
        result[key] = value
    return result


def _require_json_object(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be JSON text.")
    try:
        parsed = json.loads(
            value,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_unique_json_object,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} must contain strict JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must contain a JSON object.")


def _require_unit_interval(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a finite number.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be between 0.0 and 1.0.") from exc
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0.")
    return normalized


@dataclass(frozen=True, slots=True)
class SourceAnalysisRecord:
    analysis_id: uuid.UUID
    job_id: uuid.UUID
    source_id: uuid.UUID
    representation_id: uuid.UUID
    question: str
    state: SourceAnalysisState
    model_signature_id: uuid.UUID
    pipeline_version: str
    effective_context_limit: int
    output_reserve: int
    safety_margin: int
    token_estimator: str
    max_hierarchy_depth: int
    total_map_units: int
    completed_map_units: int
    failed_map_units: int
    coverage: float
    final_artifact_id: uuid.UUID | None
    created_at_us: int
    updated_at_us: int

    def __post_init__(self) -> None:
        for value, label in (
            (self.analysis_id, "Source analysis analysis_id"),
            (self.job_id, "Source analysis job_id"),
            (self.source_id, "Source analysis source_id"),
            (self.representation_id, "Source analysis representation_id"),
            (self.model_signature_id, "Source analysis model_signature_id"),
        ):
            _require_uuid(value, label)
        if self.final_artifact_id is not None:
            _require_uuid(self.final_artifact_id, "Source analysis final_artifact_id")
        _require_nonempty_text(self.question, "Source analysis question")
        _require_nonempty_text(self.pipeline_version, "Source analysis pipeline_version")
        _require_nonempty_text(self.token_estimator, "Source analysis token_estimator")
        if not isinstance(self.state, SourceAnalysisState):
            raise TypeError("Source analysis state must be a SourceAnalysisState.")
        _require_int(
            self.effective_context_limit,
            "Source analysis effective_context_limit",
            minimum=1,
        )
        _require_int(self.output_reserve, "Source analysis output_reserve", minimum=1)
        _require_int(self.safety_margin, "Source analysis safety_margin")
        if self.output_reserve + self.safety_margin >= self.effective_context_limit:
            raise ValueError("Source analysis context budget leaves no input capacity.")
        _require_int(self.max_hierarchy_depth, "Source analysis max_hierarchy_depth", minimum=1)
        _require_int(self.total_map_units, "Source analysis total_map_units")
        _require_int(self.completed_map_units, "Source analysis completed_map_units")
        _require_int(self.failed_map_units, "Source analysis failed_map_units")
        if self.completed_map_units + self.failed_map_units > self.total_map_units:
            raise ValueError("Source analysis completed/failed map units exceed total_map_units.")
        _require_unit_interval(self.coverage, "Source analysis coverage")
        _require_int(self.created_at_us, "Source analysis created_at_us")
        _require_int(self.updated_at_us, "Source analysis updated_at_us")
        if self.updated_at_us < self.created_at_us:
            raise ValueError("Source analysis updated_at_us precedes created_at_us.")


@dataclass(frozen=True, slots=True)
class SourceAnalysisWorkItem:
    work_item_id: uuid.UUID
    analysis_id: uuid.UUID
    stage: AnalysisStage
    level: int
    ordinal: int
    state: AnalysisWorkState
    idempotency_key: bytes
    attempt_count: int
    created_at_us: int
    updated_at_us: int

    def __post_init__(self) -> None:
        _require_uuid(self.work_item_id, "Source analysis work_item_id")
        _require_uuid(self.analysis_id, "Source analysis work analysis_id")
        if not isinstance(self.stage, AnalysisStage):
            raise TypeError("Source analysis work stage must be an AnalysisStage.")
        if not isinstance(self.state, AnalysisWorkState):
            raise TypeError("Source analysis work state must be an AnalysisWorkState.")
        _require_int(self.level, "Source analysis work level")
        _require_int(self.ordinal, "Source analysis work ordinal")
        _require_int(self.attempt_count, "Source analysis work attempt_count")
        if not isinstance(self.idempotency_key, bytes):
            raise TypeError("Source analysis work idempotency_key must be bytes.")
        if not self.idempotency_key:
            raise ValueError("Source analysis work idempotency_key must not be empty.")
        _require_int(self.created_at_us, "Source analysis work created_at_us")
        _require_int(self.updated_at_us, "Source analysis work updated_at_us")
        if self.updated_at_us < self.created_at_us:
            raise ValueError("Source analysis work updated_at_us precedes created_at_us.")


@dataclass(frozen=True, slots=True)
class SourceAnalysisArtifact:
    artifact_id: uuid.UUID
    analysis_id: uuid.UUID
    work_item_id: uuid.UUID
    artifact_kind: AnalysisStage
    level: int
    ordinal: int
    content_json: str
    content_hash: bytes
    processing_run_id: uuid.UUID
    created_at_us: int

    def __post_init__(self) -> None:
        _require_uuid(self.artifact_id, "Source analysis artifact_id")
        _require_uuid(self.analysis_id, "Source analysis artifact analysis_id")
        _require_uuid(self.work_item_id, "Source analysis artifact work_item_id")
        _require_uuid(self.processing_run_id, "Source analysis artifact processing_run_id")
        if not isinstance(self.artifact_kind, AnalysisStage):
            raise TypeError("Source analysis artifact_kind must be an AnalysisStage.")
        _require_int(self.level, "Source analysis artifact level")
        _require_int(self.ordinal, "Source analysis artifact ordinal")
        _require_nonempty_text(self.content_json, "Source analysis artifact content_json")
        _require_json_object(self.content_json, "Source analysis artifact content_json")
        _require_sha256(self.content_hash, "Source analysis artifact content_hash")
        _require_int(self.created_at_us, "Source analysis artifact created_at_us")


@dataclass(frozen=True, slots=True)
class SourceAnalysisWorkInput:
    work_item_id: uuid.UUID
    ordinal: int
    input_kind: AnalysisInputKind
    source_anchor_id: uuid.UUID | None
    artifact_id: uuid.UUID | None

    def __post_init__(self) -> None:
        """Keep the tagged input reference structurally unambiguous."""
        _require_uuid(self.work_item_id, "Source analysis input work_item_id")
        _require_int(self.ordinal, "Source analysis input ordinal")
        if not isinstance(self.input_kind, AnalysisInputKind):
            raise TypeError("Source analysis input_kind must be an AnalysisInputKind.")

        if self.input_kind is AnalysisInputKind.SOURCE_ANCHOR:
            if (
                not isinstance(self.source_anchor_id, uuid.UUID)
                or self.artifact_id is not None
            ):
                raise ValueError(
                    "Source-anchor analysis input must reference exactly one UUID source_anchor_id."
                )
            return

        if self.input_kind is AnalysisInputKind.ARTIFACT:
            if (
                not isinstance(self.artifact_id, uuid.UUID)
                or self.source_anchor_id is not None
            ):
                raise ValueError(
                    "Artifact analysis input must reference exactly one UUID artifact_id."
                )
            return

        raise AssertionError("Unhandled Source analysis input kind.")
