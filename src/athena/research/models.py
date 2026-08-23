"""Persistent domain models for Exhaustive Research foundation state."""

from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ResearchMode(str, Enum):
    LOCAL_EXHAUSTIVE = "local_exhaustive"
    SCOPED_PROJECT = "scoped_project"
    LOCAL_PLUS_WEB = "local_plus_web"
    HISTORICAL_BACKFILL = "historical_backfill"
    DELTA = "delta"


class ResearchScopeState(str, Enum):
    DISCOVERING = "discovering"
    FROZEN = "frozen"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResearchCandidateSetState(str, Enum):
    BUILDING = "building"
    FROZEN = "frozen"


class ResearchCandidateEligibility(str, Enum):
    ELIGIBLE = "eligible"
    EXCLUDED_DUPLICATE = "excluded_duplicate"


class ResearchWorkState(str, Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    IRRELEVANT = "irrelevant"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"

    @property
    def terminal(self) -> bool:
        return self is not self.PENDING


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


def _positive_int(value: object, label: str) -> None:
    _nonnegative_int(value, label)
    if value < 1:
        raise ValueError(f"{label} must be positive.")


def _optional_nonnegative_int(value: object | None, label: str) -> None:
    if value is not None:
        _nonnegative_int(value, label)


def _optional_positive_int(value: object | None, label: str) -> None:
    if value is not None:
        _positive_int(value, label)


def _text(value: object, label: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value.strip():
        raise ValueError(f"{label} must not be empty.")


def _optional_text(value: object | None, label: str) -> None:
    if value is not None:
        _text(value, label)


def _sha256(value: object, label: str) -> None:
    if not isinstance(value, bytes):
        raise TypeError(f"{label} must be bytes.")
    if len(value) != 32:
        raise ValueError(f"{label} must be a 32-byte SHA-256 digest.")


def _optional_sha256(value: object | None, label: str) -> None:
    if value is not None:
        _sha256(value, label)


def _unit_interval(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be finite and between 0 and 1.") from exc
    if not math.isfinite(normalized) or not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{label} must be finite and between 0 and 1.")


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON constant {value!r} is not permitted.")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key {key!r} is not permitted.")
        result[key] = value
    return result


def _strict_json(value: object, label: str, *, require_object: bool = False) -> None:
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
    if require_object and not isinstance(parsed, dict):
        raise ValueError(f"{label} must contain a JSON object.")


@dataclass(frozen=True, slots=True)
class ResearchScopeRecord:
    scope_id: uuid.UUID
    job_id: uuid.UUID
    mode: ResearchMode
    query_text: str
    domains_json: str
    project_ids_json: str
    source_types_json: str
    explicit_source_ids_json: str
    time_start_us: int | None
    time_end_us: int | None
    internet_scope_json: str | None
    coverage_target: float
    snapshot_commit_seq: int
    model_id: str | None
    model_signature_id: uuid.UUID | None
    model_signature_sha256: bytes | None
    effective_context_limit: int | None
    output_reserve: int | None
    safety_margin: int | None
    token_estimator: str | None
    max_hierarchy_depth: int | None
    state: ResearchScopeState
    candidate_total: int
    processed_count: int
    successful_count: int
    irrelevant_count: int
    failed_count: int
    unavailable_count: int
    excluded_count: int
    coverage_ratio: float
    created_at_us: int
    updated_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.scope_id, "Research scope scope_id")
        _uuid_value(self.job_id, "Research scope job_id")
        if not isinstance(self.mode, ResearchMode):
            raise TypeError("Research scope mode must be a ResearchMode.")
        if not isinstance(self.state, ResearchScopeState):
            raise TypeError("Research scope state must be a ResearchScopeState.")
        _text(self.query_text, "Research scope query_text")
        for value, label in (
            (self.domains_json, "Research scope domains_json"),
            (self.project_ids_json, "Research scope project_ids_json"),
            (self.source_types_json, "Research scope source_types_json"),
            (self.explicit_source_ids_json, "Research scope explicit_source_ids_json"),
        ):
            _strict_json(value, label)
        if self.internet_scope_json is not None:
            _strict_json(
                self.internet_scope_json,
                "Research scope internet_scope_json",
                require_object=True,
            )
        _optional_nonnegative_int(self.time_start_us, "Research scope time_start_us")
        _optional_nonnegative_int(self.time_end_us, "Research scope time_end_us")
        if (
            self.time_start_us is not None
            and self.time_end_us is not None
            and self.time_end_us < self.time_start_us
        ):
            raise ValueError("Research scope time_end_us precedes time_start_us.")
        _unit_interval(self.coverage_target, "Research scope coverage_target")
        _unit_interval(self.coverage_ratio, "Research scope coverage_ratio")
        _nonnegative_int(self.snapshot_commit_seq, "Research scope snapshot_commit_seq")
        _optional_text(self.model_id, "Research scope model_id")
        _optional_uuid(self.model_signature_id, "Research scope model_signature_id")
        _optional_sha256(
            self.model_signature_sha256,
            "Research scope model_signature_sha256",
        )
        _optional_positive_int(
            self.effective_context_limit,
            "Research scope effective_context_limit",
        )
        _optional_positive_int(self.output_reserve, "Research scope output_reserve")
        _optional_nonnegative_int(self.safety_margin, "Research scope safety_margin")
        _optional_text(self.token_estimator, "Research scope token_estimator")
        _optional_positive_int(
            self.max_hierarchy_depth,
            "Research scope max_hierarchy_depth",
        )
        if (
            self.effective_context_limit is not None
            and self.output_reserve is not None
            and self.safety_margin is not None
            and self.output_reserve + self.safety_margin >= self.effective_context_limit
        ):
            raise ValueError("Research scope context budget leaves no input capacity.")
        for value, label in (
            (self.candidate_total, "Research scope candidate_total"),
            (self.processed_count, "Research scope processed_count"),
            (self.successful_count, "Research scope successful_count"),
            (self.irrelevant_count, "Research scope irrelevant_count"),
            (self.failed_count, "Research scope failed_count"),
            (self.unavailable_count, "Research scope unavailable_count"),
            (self.excluded_count, "Research scope excluded_count"),
            (self.created_at_us, "Research scope created_at_us"),
            (self.updated_at_us, "Research scope updated_at_us"),
        ):
            _nonnegative_int(value, label)
        if self.updated_at_us < self.created_at_us:
            raise ValueError("Research scope updated_at_us precedes created_at_us.")
        if self.processed_count > self.candidate_total:
            raise ValueError("Research scope processed_count exceeds candidate_total.")


@dataclass(frozen=True, slots=True)
class ResearchCandidateSetRecord:
    candidate_set_id: uuid.UUID
    scope_id: uuid.UUID
    snapshot_commit_seq: int
    state: ResearchCandidateSetState
    candidate_total: int
    eligible_count: int
    excluded_count: int
    created_at_us: int
    frozen_at_us: int | None

    def __post_init__(self) -> None:
        _uuid_value(self.candidate_set_id, "Research candidate set candidate_set_id")
        _uuid_value(self.scope_id, "Research candidate set scope_id")
        if not isinstance(self.state, ResearchCandidateSetState):
            raise TypeError("Research candidate set state must be a ResearchCandidateSetState.")
        for value, label in (
            (self.snapshot_commit_seq, "Research candidate set snapshot_commit_seq"),
            (self.candidate_total, "Research candidate set candidate_total"),
            (self.eligible_count, "Research candidate set eligible_count"),
            (self.excluded_count, "Research candidate set excluded_count"),
            (self.created_at_us, "Research candidate set created_at_us"),
        ):
            _nonnegative_int(value, label)
        _optional_nonnegative_int(self.frozen_at_us, "Research candidate set frozen_at_us")
        if self.eligible_count + self.excluded_count != self.candidate_total:
            raise ValueError("Research candidate set counts are internally inconsistent.")
        if self.frozen_at_us is not None and self.frozen_at_us < self.created_at_us:
            raise ValueError("Research candidate set frozen_at_us precedes created_at_us.")
        if self.state is ResearchCandidateSetState.FROZEN and self.frozen_at_us is None:
            raise ValueError("Frozen Research candidate set requires frozen_at_us.")


@dataclass(frozen=True, slots=True)
class ResearchCandidateRecord:
    candidate_id: uuid.UUID
    candidate_set_id: uuid.UUID
    source_id: uuid.UUID
    ordinal: int
    content_sha256: bytes
    eligibility: ResearchCandidateEligibility
    duplicate_of_candidate_id: uuid.UUID | None
    created_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.candidate_id, "Research candidate candidate_id")
        _uuid_value(self.candidate_set_id, "Research candidate candidate_set_id")
        _uuid_value(self.source_id, "Research candidate source_id")
        _nonnegative_int(self.ordinal, "Research candidate ordinal")
        _sha256(self.content_sha256, "Research candidate content_sha256")
        if not isinstance(self.eligibility, ResearchCandidateEligibility):
            raise TypeError("Research candidate eligibility is invalid.")
        _optional_uuid(
            self.duplicate_of_candidate_id,
            "Research candidate duplicate_of_candidate_id",
        )
        _nonnegative_int(self.created_at_us, "Research candidate created_at_us")
        if self.eligibility is ResearchCandidateEligibility.ELIGIBLE:
            if self.duplicate_of_candidate_id is not None:
                raise ValueError("Eligible Research candidate cannot reference a duplicate.")
        elif self.duplicate_of_candidate_id is None:
            raise ValueError("Excluded duplicate Research candidate requires duplicate reference.")
        if self.duplicate_of_candidate_id == self.candidate_id:
            raise ValueError("Research candidate cannot duplicate itself.")


@dataclass(frozen=True, slots=True)
class ResearchWorkItemRecord:
    work_item_id: uuid.UUID
    scope_id: uuid.UUID
    candidate_id: uuid.UUID
    state: ResearchWorkState
    idempotency_key: bytes
    source_processing_job_id: uuid.UUID | None
    source_analysis_job_id: uuid.UUID | None
    attempt_count: int
    created_at_us: int
    updated_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.work_item_id, "Research work item work_item_id")
        _uuid_value(self.scope_id, "Research work item scope_id")
        _uuid_value(self.candidate_id, "Research work item candidate_id")
        if not isinstance(self.state, ResearchWorkState):
            raise TypeError("Research work item state must be a ResearchWorkState.")
        _sha256(self.idempotency_key, "Research work item idempotency_key")
        _optional_uuid(
            self.source_processing_job_id,
            "Research work item source_processing_job_id",
        )
        _optional_uuid(
            self.source_analysis_job_id,
            "Research work item source_analysis_job_id",
        )
        _nonnegative_int(self.attempt_count, "Research work item attempt_count")
        _nonnegative_int(self.created_at_us, "Research work item created_at_us")
        _nonnegative_int(self.updated_at_us, "Research work item updated_at_us")
        if self.updated_at_us < self.created_at_us:
            raise ValueError("Research work item updated_at_us precedes created_at_us.")


@dataclass(frozen=True, slots=True)
class ResearchCoverage:
    candidate_total: int
    processed_count: int
    successful_count: int
    irrelevant_count: int
    failed_count: int
    unavailable_count: int
    excluded_count: int
    eligible_count: int
    coverage_ratio: float

    def __post_init__(self) -> None:
        for value, label in (
            (self.candidate_total, "Research coverage candidate_total"),
            (self.processed_count, "Research coverage processed_count"),
            (self.successful_count, "Research coverage successful_count"),
            (self.irrelevant_count, "Research coverage irrelevant_count"),
            (self.failed_count, "Research coverage failed_count"),
            (self.unavailable_count, "Research coverage unavailable_count"),
            (self.excluded_count, "Research coverage excluded_count"),
            (self.eligible_count, "Research coverage eligible_count"),
        ):
            _nonnegative_int(value, label)
        _unit_interval(self.coverage_ratio, "Research coverage coverage_ratio")
        if self.eligible_count + self.excluded_count != self.candidate_total:
            raise ValueError("Research coverage candidate counts are inconsistent.")
        if self.processed_count > self.eligible_count:
            raise ValueError("Research coverage processed_count exceeds eligible_count.")
        terminal_total = (
            self.successful_count
            + self.irrelevant_count
            + self.failed_count
            + self.unavailable_count
        )
        if terminal_total != self.processed_count:
            raise ValueError("Research coverage terminal counts are inconsistent.")


class ResearchSynthesisStage(str, Enum):
    REDUCE = "reduce"
    FINAL = "final"


class ResearchSynthesisWorkState(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    SPLIT = "split"

    @property
    def terminal(self) -> bool:
        return self is not self.PENDING


class ResearchSynthesisInputKind(str, Enum):
    SOURCE_ANALYSIS_ARTIFACT = "source_analysis_artifact"
    RESEARCH_SYNTHESIS_ARTIFACT = "research_synthesis_artifact"


@dataclass(frozen=True, slots=True)
class ResearchSynthesisWorkItemRecord:
    work_item_id: uuid.UUID
    scope_id: uuid.UUID
    stage: ResearchSynthesisStage
    level: int
    ordinal: int
    state: ResearchSynthesisWorkState
    idempotency_key: bytes
    pipeline_version: str
    prompt_template_id: str
    prompt_template_version: str
    attempt_count: int
    created_at_us: int
    updated_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.work_item_id, "Research synthesis work item work_item_id")
        _uuid_value(self.scope_id, "Research synthesis work item scope_id")
        if not isinstance(self.stage, ResearchSynthesisStage):
            raise TypeError("Research synthesis stage is invalid.")
        if not isinstance(self.state, ResearchSynthesisWorkState):
            raise TypeError("Research synthesis work state is invalid.")
        _nonnegative_int(self.level, "Research synthesis work item level")
        _nonnegative_int(self.ordinal, "Research synthesis work item ordinal")
        _sha256(self.idempotency_key, "Research synthesis work item idempotency_key")
        _text(self.pipeline_version, "Research synthesis work item pipeline_version")
        _text(self.prompt_template_id, "Research synthesis work item prompt_template_id")
        _text(
            self.prompt_template_version,
            "Research synthesis work item prompt_template_version",
        )
        _nonnegative_int(self.attempt_count, "Research synthesis work item attempt_count")
        _nonnegative_int(self.created_at_us, "Research synthesis work item created_at_us")
        _nonnegative_int(self.updated_at_us, "Research synthesis work item updated_at_us")
        if self.updated_at_us < self.created_at_us:
            raise ValueError("Research synthesis work item updated_at_us precedes created_at_us.")


@dataclass(frozen=True, slots=True)
class ResearchSynthesisWorkInputRecord:
    work_item_id: uuid.UUID
    ordinal: int
    input_kind: ResearchSynthesisInputKind
    source_analysis_artifact_id: uuid.UUID | None
    research_synthesis_artifact_id: uuid.UUID | None

    def __post_init__(self) -> None:
        _uuid_value(self.work_item_id, "Research synthesis input work_item_id")
        _nonnegative_int(self.ordinal, "Research synthesis input ordinal")
        if not isinstance(self.input_kind, ResearchSynthesisInputKind):
            raise TypeError("Research synthesis input kind is invalid.")
        _optional_uuid(
            self.source_analysis_artifact_id,
            "Research synthesis input source_analysis_artifact_id",
        )
        _optional_uuid(
            self.research_synthesis_artifact_id,
            "Research synthesis input research_synthesis_artifact_id",
        )
        if self.input_kind is ResearchSynthesisInputKind.SOURCE_ANALYSIS_ARTIFACT:
            valid = (
                self.source_analysis_artifact_id is not None
                and self.research_synthesis_artifact_id is None
            )
        else:
            valid = (
                self.source_analysis_artifact_id is None
                and self.research_synthesis_artifact_id is not None
            )
        if not valid:
            raise ValueError("Research synthesis input tagged reference is inconsistent.")


@dataclass(frozen=True, slots=True)
class ResearchSynthesisArtifactRecord:
    artifact_id: uuid.UUID
    scope_id: uuid.UUID
    work_item_id: uuid.UUID
    artifact_kind: ResearchSynthesisStage
    level: int
    ordinal: int
    content_json: str
    content_hash: bytes
    processing_run_id: uuid.UUID
    created_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.artifact_id, "Research synthesis artifact artifact_id")
        _uuid_value(self.scope_id, "Research synthesis artifact scope_id")
        _uuid_value(self.work_item_id, "Research synthesis artifact work_item_id")
        _uuid_value(
            self.processing_run_id,
            "Research synthesis artifact processing_run_id",
        )
        if not isinstance(self.artifact_kind, ResearchSynthesisStage):
            raise TypeError("Research synthesis artifact kind is invalid.")
        _nonnegative_int(self.level, "Research synthesis artifact level")
        _nonnegative_int(self.ordinal, "Research synthesis artifact ordinal")
        _strict_json(
            self.content_json,
            "Research synthesis artifact content_json",
            require_object=True,
        )
        _sha256(self.content_hash, "Research synthesis artifact content_hash")
        _nonnegative_int(self.created_at_us, "Research synthesis artifact created_at_us")


@dataclass(frozen=True, slots=True)
class ResearchSynthesisEvidenceRecord:
    artifact_id: uuid.UUID
    work_item_id: uuid.UUID
    output_kind: str
    output_ordinal: int
    input_ordinal: int

    def __post_init__(self) -> None:
        _uuid_value(self.artifact_id, "Research synthesis evidence artifact_id")
        _uuid_value(self.work_item_id, "Research synthesis evidence work_item_id")
        _text(self.output_kind, "Research synthesis evidence output_kind")
        _nonnegative_int(self.output_ordinal, "Research synthesis evidence output_ordinal")
        _nonnegative_int(self.input_ordinal, "Research synthesis evidence input_ordinal")


@dataclass(frozen=True, slots=True)
class ResearchResultRecord:
    result_id: uuid.UUID
    scope_id: uuid.UUID
    final_artifact_id: uuid.UUID | None
    content_json: str
    content_hash: bytes
    snapshot_commit_seq: int
    model_signature_id: uuid.UUID | None
    synthesis_pipeline_version: str
    candidate_total: int
    processed_count: int
    successful_count: int
    irrelevant_count: int
    failed_count: int
    unavailable_count: int
    excluded_count: int
    coverage_ratio: float
    problem_sources_json: str
    created_at_us: int

    def __post_init__(self) -> None:
        _uuid_value(self.result_id, "Research result result_id")
        _uuid_value(self.scope_id, "Research result scope_id")
        _optional_uuid(self.final_artifact_id, "Research result final_artifact_id")
        _strict_json(self.content_json, "Research result content_json", require_object=True)
        _sha256(self.content_hash, "Research result content_hash")
        _nonnegative_int(self.snapshot_commit_seq, "Research result snapshot_commit_seq")
        _optional_uuid(self.model_signature_id, "Research result model_signature_id")
        _text(
            self.synthesis_pipeline_version,
            "Research result synthesis_pipeline_version",
        )
        for value, label in (
            (self.candidate_total, "Research result candidate_total"),
            (self.processed_count, "Research result processed_count"),
            (self.successful_count, "Research result successful_count"),
            (self.irrelevant_count, "Research result irrelevant_count"),
            (self.failed_count, "Research result failed_count"),
            (self.unavailable_count, "Research result unavailable_count"),
            (self.excluded_count, "Research result excluded_count"),
            (self.created_at_us, "Research result created_at_us"),
        ):
            _nonnegative_int(value, label)
        _unit_interval(self.coverage_ratio, "Research result coverage_ratio")
        _strict_json(self.problem_sources_json, "Research result problem_sources_json")
        if self.processed_count > self.candidate_total:
            raise ValueError("Research result processed_count exceeds candidate_total.")
