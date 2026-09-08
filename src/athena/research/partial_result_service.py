"""Explicit post-cancel partial reports for Exhaustive Research."""

from __future__ import annotations

import hashlib
import json
import uuid

from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.jobs.models import JobState
from athena.jobs.service import DurableJobService
from athena.research.models import (
    ResearchResultRecord,
    ResearchScopeState,
    ResearchSynthesisWorkState,
)
from athena.research.repository import ResearchRepository, ResearchStateError
from athena.research.source_coverage_composition import (
    research_result_content_with_source_coverage_from_connection,
)
from athena.research.validation import (
    _canonical_json_object,
    _canonical_json_value,
)

PARTIAL_REPORT_PIPELINE_VERSION = "exhaustive-research-partial-v1"


class ResearchPartialResultService:
    """Persist an explicitly partial report from confirmed immutable artifacts only."""

    def __init__(
        self,
        *,
        repository: ResearchRepository,
        jobs: DurableJobService,
    ) -> None:
        self.repository = repository
        self.jobs = jobs

    def create(self, job_id: uuid.UUID) -> ResearchResultRecord:
        """Create or return the durable partial report for one cancelled Research job."""
        job = self.jobs.get(job_id)
        if job.job_type != "research.exhaustive":
            raise ResearchStateError("Partial report requires a research.exhaustive job.")
        if job.state is not JobState.CANCELLED:
            raise ResearchStateError("Partial report is available only after cancellation.")

        scope = self.repository.get_scope_for_job(job_id)
        if scope is None:
            raise ResearchStateError("Cancelled Research job has no durable scope.")
        if scope.state is not ResearchScopeState.PARTIAL:
            raise ResearchStateError("Partial report requires a PARTIAL Research scope.")

        existing = self.repository.get_result_for_scope(scope.scope_id)
        if existing is not None:
            try:
                payload = json.loads(existing.content_json)
            except json.JSONDecodeError as exc:
                raise ResearchStateError(
                    "Existing ResearchResult contains invalid JSON."
                ) from exc
            if (
                existing.final_artifact_id is None
                and existing.synthesis_pipeline_version
                == PARTIAL_REPORT_PIPELINE_VERSION
                and isinstance(payload, dict)
                and payload.get("partial") is True
            ):
                return existing
            raise ResearchStateError(
                "Research scope already has a non-partial or incompatible result."
            )

        confirmed: list[dict[str, object]] = []
        for work in self.repository.list_synthesis_work_items(scope.scope_id):
            if work.state is not ResearchSynthesisWorkState.COMPLETED:
                continue
            artifact = self.repository.synthesis_artifact_for_work_item(work.work_item_id)
            if artifact is None:
                raise ResearchStateError(
                    "Completed Research synthesis work lost its immutable artifact."
                )
            try:
                content = json.loads(artifact.content_json)
            except json.JSONDecodeError as exc:
                raise ResearchStateError(
                    "Confirmed Research synthesis artifact contains invalid JSON."
                ) from exc
            source_artifact_ids = (
                self.repository.source_analysis_artifact_ids_for_synthesis_artifact(
                    artifact.artifact_id
                )
            )
            confirmed.append(
                {
                    "artifact_id": str(artifact.artifact_id),
                    "artifact_kind": artifact.artifact_kind.value,
                    "level": artifact.level,
                    "ordinal": artifact.ordinal,
                    "content_hash": artifact.content_hash.hex(),
                    "content": content,
                    "source_analysis_artifact_ids": [
                        str(item) for item in source_artifact_ids
                    ],
                }
            )

        confirmed.sort(
            key=lambda item: (
                int(item["level"]),
                int(item["ordinal"]),
                str(item["artifact_id"]),
            )
        )
        semantic_content = {
            "partial": True,
            "result_status": "partial",
            "completion_reason": "cancelled",
            "confirmed_intermediates": confirmed,
        }

        with self.repository.database.write_transaction() as connection:
            job_row = connection.execute(
                "SELECT state FROM jobs WHERE job_id = ?",
                (uuid_to_blob(job_id),),
            ).fetchone()
            scope_row = connection.execute(
                "SELECT * FROM research_scopes WHERE scope_id = ?",
                (uuid_to_blob(scope.scope_id),),
            ).fetchone()
            if job_row is None or str(job_row["state"]) != JobState.CANCELLED.value:
                raise ResearchStateError("Research job is no longer cancelled.")
            if (
                scope_row is None
                or str(scope_row["state"]) != ResearchScopeState.PARTIAL.value
            ):
                raise ResearchStateError("Research scope is no longer partial.")

            duplicate = connection.execute(
                "SELECT 1 FROM research_results WHERE scope_id = ?",
                (uuid_to_blob(scope.scope_id),),
            ).fetchone()
            if duplicate is not None:
                raise ResearchStateError(
                    "Research result appeared concurrently during partial composition."
                )

            eligible_count = scope.candidate_total - scope.excluded_count
            problem_rows = connection.execute(
                """
                SELECT rc.ordinal, rc.source_id, rw.state
                FROM research_work_items AS rw
                JOIN research_candidates AS rc ON rc.candidate_id = rw.candidate_id
                WHERE rw.scope_id = ?
                  AND rw.state IN ('failed', 'unavailable')
                ORDER BY rc.ordinal ASC, rc.source_id ASC
                """,
                (uuid_to_blob(scope.scope_id),),
            ).fetchall()
            problems = [
                {
                    "candidate_ordinal": int(row["ordinal"]),
                    "source_id": str(uuid_from_blob(bytes(row["source_id"]))),
                    "state": str(row["state"]),
                }
                for row in problem_rows
            ]
            payload = research_result_content_with_source_coverage_from_connection(
                semantic_content,
                connection,
                scope.scope_id,
            )
            payload["coverage"] = {
                "candidate_total": scope.candidate_total,
                "processed_count": scope.processed_count,
                "successful_count": scope.successful_count,
                "irrelevant_count": scope.irrelevant_count,
                "failed_count": scope.failed_count,
                "unavailable_count": scope.unavailable_count,
                "excluded_count": scope.excluded_count,
                "eligible_count": eligible_count,
                "coverage_ratio": scope.coverage_ratio,
            }
            payload["problem_sources"] = problems
            payload["snapshot_commit_seq"] = scope.snapshot_commit_seq
            content_json = _canonical_json_object(payload)
            content_hash = hashlib.sha256(content_json.encode("utf-8")).digest()
            now_us = utc_now_us()
            result_id = new_uuid7()
            connection.execute(
                """
                INSERT INTO research_results (
                    result_id, scope_id, final_artifact_id,
                    content_json, content_hash, snapshot_commit_seq,
                    model_signature_id, synthesis_pipeline_version,
                    candidate_total, processed_count, successful_count,
                    irrelevant_count, failed_count, unavailable_count,
                    excluded_count, coverage_ratio, problem_sources_json,
                    created_at_us
                ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(result_id),
                    uuid_to_blob(scope.scope_id),
                    content_json,
                    content_hash,
                    scope.snapshot_commit_seq,
                    (
                        uuid_to_blob(scope.model_signature_id)
                        if scope.model_signature_id is not None
                        else None
                    ),
                    PARTIAL_REPORT_PIPELINE_VERSION,
                    scope.candidate_total,
                    scope.processed_count,
                    scope.successful_count,
                    scope.irrelevant_count,
                    scope.failed_count,
                    scope.unavailable_count,
                    scope.excluded_count,
                    scope.coverage_ratio,
                    _canonical_json_value(problems),
                    now_us,
                ),
            )

        result = self.repository.get_result_for_scope(scope.scope_id)
        if result is None:
            raise ResearchStateError("Partial ResearchResult was not durably persisted.")
        return result
