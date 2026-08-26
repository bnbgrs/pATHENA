"""Deterministic SourceChunk generation from retained text representations."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass

from athena.chat.service import ChatService
from athena.common.ids import new_uuid7
from athena.common.time import utc_now_us
from athena.model.provenance import ModelRunRepository, ProcessingRun
from athena.source.chunk_store import (
    SourceChunkNotFoundError,
    SourceChunkPlanRecord,
    SourceChunkRecord,
    SourceChunkStore,
    StagedSourceChunkRecord,
)
from athena.source.chunking_repository import ChunkingProfile, ChunkingProfileRepository
from athena.source.models import (
    SourceRepresentationStructureRecord,
    SourceRepresentationType,
)
from athena.source.representation_service import SourceTextRepresentationService

_PIPELINE_VERSION = "source-chunking-v1"


class SourceChunkIntegrityError(RuntimeError):
    """Raised when a derived chunk no longer matches its retained representation."""


class SourceChunkStagingLostError(SourceChunkIntegrityError):
    """Raised when reconstructible unpublished large-source staging disappeared."""


@dataclass(frozen=True, slots=True)
class SourceChunkBuildResult:
    profile: ChunkingProfile
    processing_run: ProcessingRun
    build_signature: bytes
    chunks: tuple[SourceChunkRecord, ...]


@dataclass(frozen=True, slots=True)
class SourceChunkStagingPlanResult:
    """Deterministic unpublished plan for a potentially large representation."""

    profile: ChunkingProfile
    build_signature: bytes
    chunk_count: int


@dataclass(frozen=True, slots=True)
class SourceChunkStagingBatchResult:
    """One atomically staged, but still unpublished, chunk batch."""

    build_signature: bytes
    start_index: int
    next_index: int
    total_chunks: int
    batch_count: int


@dataclass(frozen=True, slots=True)
class SourceChunkPublishResult:
    """Published result of a complete staged SourceChunk build."""

    profile: ChunkingProfile
    processing_run: ProcessingRun
    build_signature: bytes
    chunk_count: int


class SourceChunkingService:
    """Build reconstructible paragraph-aware chunks without mutating Raw Archive state."""

    def __init__(
        self,
        *,
        source_text: SourceTextRepresentationService,
        profiles: ChunkingProfileRepository,
        store: SourceChunkStore,
        runs: ModelRunRepository,
        chat: ChatService,
    ) -> None:
        self.source_text = source_text
        self.profiles = profiles
        self.store = store
        self.runs = runs
        self.chat = chat

    def build_default(self, representation_id: uuid.UUID) -> SourceChunkBuildResult:
        representation, blob = self.source_text.get(representation_id)
        if representation.representation_type not in {
            SourceRepresentationType.NORMALIZED_TEXT,
            SourceRepresentationType.EXTRACTED_TEXT,
        }:
            raise ValueError(
                "Source chunking requires a retained normalized_text or extracted_text representation."
            )
        path = self.source_text.verify(representation_id)
        structures = self.source_text.list_structures(representation_id)
        if representation.parser_id in {"athena.native_docx", "athena.native_html"} and not structures:
            format_name = "DOCX" if representation.parser_id == "athena.native_docx" else "HTML"
            raise SourceChunkIntegrityError(
                f"Native {format_name} representation is missing its retained structure map."
            )
        profile = (
            self.profiles.get_or_create_document_default()
            if structures
            else self.profiles.get_or_create_default()
        )
        build_signature = _build_signature(
            representation_id=representation_id,
            representation_hash=representation.content_hash,
            profile=profile,
        )
        actor_id = self.chat.ensure_local_user()
        run = self.runs.start_run(
            run_type="source_chunk_build",
            trigger_actor_id=actor_id,
            pipeline_version=_PIPELINE_VERSION,
            input_snapshot={
                "source_id": str(representation.source_id),
                "representation_id": str(representation.representation_id),
                "representation_sha256": representation.content_hash.hex(),
                "representation_byte_length": blob.byte_length,
            },
            configuration={
                "chunking_profile_id": str(profile.chunking_profile_id),
                "algorithm": profile.algorithm,
                "tokenizer": profile.tokenizer,
                "target_size": profile.target_size,
                "overlap_size": profile.overlap_size,
                "structure_rules": json.loads(profile.structure_rules_json),
                "profile_version": profile.profile_version,
                "build_signature": build_signature.hex(),
            },
            model_signature_id=None,
            prompt_template_id=None,
            prompt_template_version=None,
        )

        try:
            text = path.read_text(encoding="utf-8")
            if structures:
                _verify_structure_spans(text, structures)
                units, structure_boundaries = _document_structure_units(text, structures)
                spans = _chunk_spans(
                    text,
                    target_size=profile.target_size or 1200,
                    units=units,
                    preferred_boundaries=structure_boundaries,
                )
            else:
                spans = _chunk_spans(text, target_size=profile.target_size or 1200)
            created_at_us = utc_now_us()
            chunks = tuple(
                SourceChunkRecord(
                    chunk_id=new_uuid7(),
                    source_id=representation.source_id,
                    representation_id=representation.representation_id,
                    chunk_index=index,
                    chunking_profile_id=profile.chunking_profile_id,
                    start_anchor_value=start,
                    end_anchor_value=end,
                    content_hash=hashlib.sha256(text[start:end].encode("utf-8")).digest(),
                    processing_run_id=run.processing_run_id,
                    build_signature=build_signature,
                    chunk_text=text[start:end],
                    created_at_us=created_at_us,
                )
                for index, (start, end) in enumerate(spans)
            )
            self.store.replace_build(
                representation_id=representation.representation_id,
                chunking_profile_id=profile.chunking_profile_id,
                build_signature=build_signature,
                processing_run_id=run.processing_run_id,
                created_at_us=created_at_us,
                chunks=chunks,
            )
            finished = self.runs.finish_run(run.processing_run_id, status="succeeded")
            return SourceChunkBuildResult(
                profile=profile,
                processing_run=finished,
                build_signature=build_signature,
                chunks=chunks,
            )
        except Exception as exc:
            current = self.runs.load_run(run.processing_run_id)
            if current.status == "running":
                self.runs.finish_run(
                    run.processing_run_id,
                    status="failed",
                    error_detail=type(exc).__name__,
                )
            raise

    def prepare_staged_default(
        self,
        representation_id: uuid.UUID,
    ) -> SourceChunkStagingPlanResult:
        """Prepare a deterministic offset plan without changing the visible chunk build."""
        representation, _blob = self.source_text.get(representation_id)
        profile, text, spans = self._profile_text_and_spans(representation_id)
        build_signature = _build_signature(
            representation_id=representation_id,
            representation_hash=representation.content_hash,
            profile=profile,
        )
        plan: list[SourceChunkPlanRecord] = []
        previous_char_end = 0
        byte_cursor = 0
        for index, (start, end) in enumerate(spans):
            if start != previous_char_end:
                raise SourceChunkIntegrityError(
                    "Large-source plan is not contiguous in representation coordinates."
                )
            fragment_bytes = text[start:end].encode("utf-8")
            plan.append(
                SourceChunkPlanRecord(
                    chunk_index=index,
                    start_anchor_value=start,
                    end_anchor_value=end,
                    start_byte_offset=byte_cursor,
                    end_byte_offset=byte_cursor + len(fragment_bytes),
                    content_hash=hashlib.sha256(fragment_bytes).digest(),
                )
            )
            byte_cursor += len(fragment_bytes)
            previous_char_end = end
        if byte_cursor != len(text.encode("utf-8")):
            raise SourceChunkIntegrityError(
                "Large-source plan byte coverage disagrees with retained representation."
            )
        self.store.prepare_staged_build(
            source_id=representation.source_id,
            representation_id=representation.representation_id,
            chunking_profile_id=profile.chunking_profile_id,
            build_signature=build_signature,
            representation_hash=representation.content_hash,
            plan=tuple(plan),
            created_at_us=utc_now_us(),
        )
        return SourceChunkStagingPlanResult(
            profile=profile,
            build_signature=build_signature,
            chunk_count=len(plan),
        )

    def stage_staged_default_batch(
        self,
        representation_id: uuid.UUID,
        *,
        build_signature: bytes,
        start_index: int,
        batch_size: int,
    ) -> SourceChunkStagingBatchResult:
        """Stage one bounded batch using persisted UTF-8 byte offsets from the plan."""
        if start_index < 0:
            raise ValueError("Large-source batch start_index must not be negative.")
        if not 1 <= batch_size <= 4096:
            raise ValueError("Large-source batch_size must be between 1 and 4096.")
        representation, _blob = self.source_text.get(representation_id)
        path = self.source_text.verify(representation_id)
        try:
            staged = self.store.get_staged_build(build_signature)
        except SourceChunkNotFoundError as exc:
            raise SourceChunkStagingLostError(
                "Unpublished large-source staging is missing and must restart from its plan boundary."
            ) from exc
        if staged.representation_id != representation_id:
            raise SourceChunkIntegrityError(
                "Staged large-source build belongs to a different representation."
            )
        if staged.representation_hash != representation.content_hash:
            raise SourceChunkIntegrityError(
                "Staged large-source build references a different representation hash."
            )
        if start_index > staged.total_chunks:
            raise SourceChunkIntegrityError(
                "Large-source resume index exceeds the deterministic chunk plan."
            )
        if self.store.staged_prefix_count(build_signature, start_index) != start_index:
            raise SourceChunkStagingLostError(
                "Previously confirmed unpublished chunk staging is missing."
            )
        plan = self.store.list_staged_plan(
            build_signature,
            start_index=start_index,
            limit=batch_size,
        )
        expected_indexes = tuple(range(start_index, start_index + len(plan)))
        if tuple(item.chunk_index for item in plan) != expected_indexes:
            raise SourceChunkIntegrityError(
                "Large-source staged plan is missing a contiguous batch range."
            )
        profile = self.profiles.get(staged.chunking_profile_id)
        created_at_us = utc_now_us()
        chunks: list[StagedSourceChunkRecord] = []
        with path.open("rb") as handle:
            for item in plan:
                handle.seek(item.start_byte_offset)
                raw = handle.read(item.end_byte_offset - item.start_byte_offset)
                if len(raw) != item.end_byte_offset - item.start_byte_offset:
                    raise SourceChunkIntegrityError(
                        "Retained representation ended before a planned chunk byte range."
                    )
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise SourceChunkIntegrityError(
                        "Planned chunk byte range is not valid retained UTF-8 text."
                    ) from exc
                if len(text) != item.end_anchor_value - item.start_anchor_value:
                    raise SourceChunkIntegrityError(
                        "Planned byte range disagrees with codepoint anchor length."
                    )
                actual_hash = hashlib.sha256(raw).digest()
                if actual_hash != item.content_hash:
                    raise SourceChunkIntegrityError(
                        "Planned chunk hash disagrees with retained representation bytes."
                    )
                chunks.append(
                    StagedSourceChunkRecord(
                        chunk_id=new_uuid7(),
                        source_id=representation.source_id,
                        representation_id=representation.representation_id,
                        chunk_index=item.chunk_index,
                        chunking_profile_id=profile.chunking_profile_id,
                        start_anchor_value=item.start_anchor_value,
                        end_anchor_value=item.end_anchor_value,
                        content_hash=item.content_hash,
                        build_signature=build_signature,
                        chunk_text=text,
                        created_at_us=created_at_us,
                    )
                )
        next_index = self.store.stage_chunk_batch(
            build_signature=build_signature,
            start_index=start_index,
            chunks=tuple(chunks),
        )
        return SourceChunkStagingBatchResult(
            build_signature=build_signature,
            start_index=start_index,
            next_index=next_index,
            total_chunks=staged.total_chunks,
            batch_count=len(chunks),
        )

    def discard_staged_default(self, build_signature: bytes) -> None:
        """Discard reconstructible unpublished staging, for example after cancellation."""
        self.store.discard_staged_build(build_signature)

    def publish_staged_default(
        self,
        representation_id: uuid.UUID,
        *,
        build_signature: bytes,
        expected_chunk_count: int,
    ) -> SourceChunkPublishResult:
        """Publish a fully staged build atomically; partial staging never becomes searchable."""
        representation, blob = self.source_text.get(representation_id)
        profile = self._default_profile_for_representation(representation_id)
        current = self.store.current_build(representation_id, profile.chunking_profile_id)
        if current is not None and current.build_signature == build_signature:
            run = self.runs.load_run(current.processing_run_id)
            if run.status != "succeeded" or current.chunk_count != expected_chunk_count:
                raise SourceChunkIntegrityError(
                    "Published large-source build metadata is inconsistent."
                )
            return SourceChunkPublishResult(
                profile=profile,
                processing_run=run,
                build_signature=build_signature,
                chunk_count=current.chunk_count,
            )
        try:
            staged = self.store.get_staged_build(build_signature)
        except SourceChunkNotFoundError as exc:
            raise SourceChunkStagingLostError(
                "Unpublished large-source staging disappeared before publication."
            ) from exc
        if staged.representation_id != representation_id:
            raise SourceChunkIntegrityError(
                "Staged build belongs to a different retained representation."
            )
        if staged.total_chunks != expected_chunk_count:
            raise SourceChunkIntegrityError(
                "Staged build chunk count disagrees with the durable resume cursor."
            )
        if self.store.staged_chunk_count(build_signature) != expected_chunk_count:
            raise SourceChunkIntegrityError(
                "Cannot publish an incomplete large-source staged build."
            )
        digest = hashlib.sha256()
        expected_index = 0
        expected_start = 0
        for chunk in self.store.iter_staged_chunks(build_signature):
            if chunk.chunk_index != expected_index or chunk.start_anchor_value != expected_start:
                raise SourceChunkIntegrityError(
                    "Staged large-source chunks contain an index/range gap or overlap."
                )
            raw = chunk.chunk_text.encode("utf-8")
            if len(chunk.chunk_text) != chunk.end_anchor_value - chunk.start_anchor_value:
                raise SourceChunkIntegrityError(
                    "Staged large-source chunk anchor length is invalid."
                )
            if hashlib.sha256(raw).digest() != chunk.content_hash:
                raise SourceChunkIntegrityError(
                    "Staged large-source chunk hash is invalid."
                )
            digest.update(raw)
            expected_index += 1
            expected_start = chunk.end_anchor_value
        if expected_index != expected_chunk_count or digest.digest() != representation.content_hash:
            raise SourceChunkIntegrityError(
                "Staged large-source chunks do not reproduce the retained representation hash."
            )
        actor_id = self.chat.ensure_local_user()
        run = self.runs.start_run(
            run_type="source_chunk_build",
            trigger_actor_id=actor_id,
            pipeline_version="source-chunking-v2-batched",
            input_snapshot={
                "source_id": str(representation.source_id),
                "representation_id": str(representation.representation_id),
                "representation_sha256": representation.content_hash.hex(),
                "representation_byte_length": blob.byte_length,
            },
            configuration={
                "chunking_profile_id": str(profile.chunking_profile_id),
                "algorithm": profile.algorithm,
                "tokenizer": profile.tokenizer,
                "target_size": profile.target_size,
                "overlap_size": profile.overlap_size,
                "structure_rules": json.loads(profile.structure_rules_json),
                "profile_version": profile.profile_version,
                "build_signature": build_signature.hex(),
                "publication": "atomic_staged_publish",
            },
            model_signature_id=None,
            prompt_template_id=None,
            prompt_template_version=None,
        )
        try:
            published_count = self.store.publish_staged_build(
                build_signature=build_signature,
                processing_run_id=run.processing_run_id,
                created_at_us=utc_now_us(),
            )
            if published_count != expected_chunk_count:
                raise SourceChunkIntegrityError(
                    "Published chunk count disagrees with deterministic staged plan."
                )
            self.verify_current_profile_build(
                representation_id,
                chunking_profile_id=profile.chunking_profile_id,
                expected_build_signature=build_signature,
                expected_chunk_count=expected_chunk_count,
                expected_inflight_run_id=run.processing_run_id,
            )
            finished = self.runs.finish_run(run.processing_run_id, status="succeeded")
        except Exception as exc:
            current_run = self.runs.load_run(run.processing_run_id)
            if current_run.status == "running":
                self.runs.finish_run(
                    run.processing_run_id,
                    status="failed",
                    error_detail=type(exc).__name__,
                )
            raise
        return SourceChunkPublishResult(
            profile=profile,
            processing_run=finished,
            build_signature=build_signature,
            chunk_count=published_count,
        )

    def verify_current_build(
        self,
        representation_id: uuid.UUID,
        *,
        expected_build_signature: bytes,
        expected_chunk_count: int,
    ) -> int:
        """Stream-verify an arbitrarily large visible build against retained SHA-256."""
        profile = self._default_profile_for_representation(representation_id)
        return self.verify_current_profile_build(
            representation_id,
            chunking_profile_id=profile.chunking_profile_id,
            expected_build_signature=expected_build_signature,
            expected_chunk_count=expected_chunk_count,
        )

    def verify_current_profile_build(
        self,
        representation_id: uuid.UUID,
        *,
        chunking_profile_id: uuid.UUID,
        expected_build_signature: bytes,
        expected_chunk_count: int,
        expected_inflight_run_id: uuid.UUID | None = None,
    ) -> int:
        """Stream-verify one exact current profile build against retained evidence."""
        representation, _blob = self.source_text.get(representation_id)
        self.source_text.verify(representation_id)
        profile = self.profiles.get(chunking_profile_id)
        derived_signature = _build_signature(
            representation_id=representation.representation_id,
            representation_hash=representation.content_hash,
            profile=profile,
        )
        if derived_signature != expected_build_signature:
            raise SourceChunkIntegrityError(
                "Expected SourceChunk build signature disagrees with retained inputs."
            )
        current = self.store.current_build(representation_id, chunking_profile_id)
        if current is None:
            raise SourceChunkIntegrityError("Current SourceChunk build is missing.")
        if current.build_signature != expected_build_signature:
            raise SourceChunkIntegrityError("Current SourceChunk build signature is stale.")
        if current.chunk_count != expected_chunk_count:
            raise SourceChunkIntegrityError("Current SourceChunk count is incomplete.")
        run = self.runs.load_run(current.processing_run_id)
        if run.status != "succeeded" and not (
            expected_inflight_run_id is not None
            and current.processing_run_id == expected_inflight_run_id
            and run.status == "running"
        ):
            raise SourceChunkIntegrityError(
                "Current SourceChunk build references a non-succeeded ProcessingRun."
            )

        digest = hashlib.sha256()
        expected_index = 0
        expected_start = 0
        for chunk in self.store.iter_for_representation(
            representation_id,
            chunking_profile_id=chunking_profile_id,
        ):
            if chunk.chunk_index != expected_index:
                raise SourceChunkIntegrityError(
                    "Current SourceChunk indexes are not contiguous."
                )
            if chunk.source_id != representation.source_id:
                raise SourceChunkIntegrityError("Current SourceChunk source_id is invalid.")
            if chunk.processing_run_id != current.processing_run_id:
                raise SourceChunkIntegrityError(
                    "Current SourceChunk processing_run_id disagrees with its build."
                )
            if chunk.start_anchor_value != expected_start:
                raise SourceChunkIntegrityError(
                    "Current SourceChunk ranges contain a gap or overlap."
                )
            if (
                chunk.end_anchor_value - chunk.start_anchor_value
                != len(chunk.chunk_text)
            ):
                raise SourceChunkIntegrityError(
                    "Current SourceChunk codepoint range disagrees with its text."
                )
            raw = chunk.chunk_text.encode("utf-8")
            if hashlib.sha256(raw).digest() != chunk.content_hash:
                raise SourceChunkIntegrityError(
                    "Current SourceChunk content hash is invalid."
                )
            if chunk.build_signature != expected_build_signature:
                raise SourceChunkIntegrityError(
                    "Current SourceChunk has a stale build signature."
                )
            digest.update(raw)
            expected_start = chunk.end_anchor_value
            expected_index += 1

        if expected_index != expected_chunk_count:
            raise SourceChunkIntegrityError("Current SourceChunk stream ended early.")
        if digest.digest() != representation.content_hash:
            raise SourceChunkIntegrityError(
                "Concatenated SourceChunks do not reproduce the retained representation hash."
            )
        return expected_index

    def _default_profile_for_representation(
        self,
        representation_id: uuid.UUID,
    ) -> ChunkingProfile:
        representation, _blob = self.source_text.get(representation_id)
        structures = self.source_text.list_structures(representation_id)
        if representation.parser_id in {"athena.native_docx", "athena.native_html"} and not structures:
            format_name = "DOCX" if representation.parser_id == "athena.native_docx" else "HTML"
            raise SourceChunkIntegrityError(
                f"Native {format_name} representation is missing its retained structure map."
            )
        return (
            self.profiles.get_or_create_document_default()
            if structures
            else self.profiles.get_or_create_default()
        )

    def _profile_text_and_spans(
        self,
        representation_id: uuid.UUID,
    ) -> tuple[ChunkingProfile, str, tuple[tuple[int, int], ...]]:
        representation, _blob = self.source_text.get(representation_id)
        if representation.representation_type not in {
            SourceRepresentationType.NORMALIZED_TEXT,
            SourceRepresentationType.EXTRACTED_TEXT,
        }:
            raise ValueError(
                "Source chunking requires a retained normalized_text or extracted_text representation."
            )
        path = self.source_text.verify(representation_id)
        structures = self.source_text.list_structures(representation_id)
        profile = self._default_profile_for_representation(representation_id)
        text = path.read_text(encoding="utf-8")
        if structures:
            _verify_structure_spans(text, structures)
            units, structure_boundaries = _document_structure_units(text, structures)
            spans = _chunk_spans(
                text,
                target_size=profile.target_size or 1200,
                units=units,
                preferred_boundaries=structure_boundaries,
            )
        else:
            spans = _chunk_spans(text, target_size=profile.target_size or 1200)
        return profile, text, spans

    def get(self, chunk_id: uuid.UUID) -> SourceChunkRecord:
        return self.store.get(chunk_id)

    def count_for_representation(self, representation_id: uuid.UUID) -> int:
        """Return the exact visible chunk count without materializing large builds."""
        self.source_text.get(representation_id)
        return self.store.count_for_representation(representation_id)

    def list_for_representation(
        self,
        representation_id: uuid.UUID,
        *,
        limit: int = 500,
    ) -> tuple[SourceChunkRecord, ...]:
        self.source_text.get(representation_id)
        chunks = self.store.list_for_representation(representation_id, limit=limit)
        if chunks:
            run = self.runs.load_run(chunks[0].processing_run_id)
            if run.status != "succeeded":
                raise SourceChunkIntegrityError(
                    "Current SourceChunk build references a non-succeeded ProcessingRun."
                )
        return chunks

    def verify(self, chunk_id: uuid.UUID) -> SourceChunkRecord:
        chunk = self.store.get(chunk_id)
        representation, _ = self.source_text.get(chunk.representation_id)
        if representation.source_id != chunk.source_id:
            raise SourceChunkIntegrityError("SourceChunk source_id disagrees with its representation.")
        profile = self.profiles.get(chunk.chunking_profile_id)
        expected_build_signature = _build_signature(
            representation_id=representation.representation_id,
            representation_hash=representation.content_hash,
            profile=profile,
        )
        if chunk.build_signature != expected_build_signature:
            raise SourceChunkIntegrityError("SourceChunk build signature is invalid.")
        run = self.runs.load_run(chunk.processing_run_id)
        if run.status != "succeeded":
            raise SourceChunkIntegrityError("SourceChunk references a non-succeeded ProcessingRun.")

        text = self.source_text.read_text(chunk.representation_id)
        if not 0 <= chunk.start_anchor_value <= chunk.end_anchor_value <= len(text):
            raise SourceChunkIntegrityError("SourceChunk anchor range is outside the representation.")
        expected_text = text[chunk.start_anchor_value : chunk.end_anchor_value]
        if chunk.chunk_text != expected_text:
            raise SourceChunkIntegrityError("SourceChunk text disagrees with its representation slice.")
        expected_hash = hashlib.sha256(expected_text.encode("utf-8")).digest()
        if chunk.content_hash != expected_hash:
            raise SourceChunkIntegrityError("SourceChunk content hash verification failed.")
        return chunk


def _build_signature(
    *,
    representation_id: uuid.UUID,
    representation_hash: bytes,
    profile: ChunkingProfile,
) -> bytes:
    payload = {
        "pipeline_version": _PIPELINE_VERSION,
        "representation_id": str(representation_id),
        "representation_sha256": representation_hash.hex(),
        "chunking_profile_id": str(profile.chunking_profile_id),
        "configuration_hash": profile.configuration_hash.hex(),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).digest()


def _chunk_spans(
    text: str,
    *,
    target_size: int,
    units: tuple[tuple[int, int], ...] | None = None,
    preferred_boundaries: frozenset[int] = frozenset(),
) -> tuple[tuple[int, int], ...]:
    if not text:
        return ((0, 0),)
    if target_size <= 0:
        raise ValueError("Chunk target_size must be positive.")
    if units is None:
        units = _paragraph_units(text)
    if not units:
        return ((0, len(text)),)

    spans: list[tuple[int, int]] = []
    chunk_start = units[0][0]
    chunk_end = units[0][1]

    for unit_start, unit_end in units[1:]:
        if unit_start != chunk_end:
            raise SourceChunkIntegrityError("Chunking units are not contiguous.")
        proposed_length = unit_end - chunk_start
        if proposed_length <= target_size:
            chunk_end = unit_end
            continue
        if chunk_start < chunk_end:
            spans.append((chunk_start, chunk_end))
        chunk_start = unit_start
        chunk_end = unit_end

        while chunk_end - chunk_start > target_size:
            split = _bounded_split_point(
                text,
                chunk_start,
                min(chunk_start + target_size, chunk_end),
                preferred_boundaries=preferred_boundaries,
            )
            if split <= chunk_start:
                split = min(chunk_start + target_size, chunk_end)
            spans.append((chunk_start, split))
            chunk_start = split

    if chunk_start < chunk_end:
        spans.append((chunk_start, chunk_end))

    if not spans:
        spans.append((0, len(text)))

    # Cover empty trailing/leading separators and guarantee exact concatenation.
    normalized: list[tuple[int, int]] = []
    expected_start = 0
    for start, end in spans:
        start = expected_start
        if end < start:
            raise SourceChunkIntegrityError("Chunk span end precedes its start.")
        normalized.append((start, end))
        expected_start = end
    if normalized[-1][1] < len(text):
        normalized[-1] = (normalized[-1][0], len(text))
    return tuple(normalized)


def _paragraph_units(text: str) -> tuple[tuple[int, int], ...]:
    if not text:
        return ()
    units: list[tuple[int, int]] = []
    cursor = 0
    index = 0
    while index < len(text):
        separator = text.find("\n\n", index)
        if separator < 0:
            units.append((cursor, len(text)))
            break
        unit_end = separator + 2
        units.append((cursor, unit_end))
        cursor = unit_end
        index = unit_end
    if not units:
        units.append((0, len(text)))
    return tuple(units)


def _document_structure_units(
    text: str,
    structures: tuple[SourceRepresentationStructureRecord, ...],
) -> tuple[tuple[tuple[int, int], ...], frozenset[int]]:
    structural_boundaries = sorted(
        {
            item.end_offset
            for item in structures
            if 0 < item.end_offset < len(text)
        }
    )
    split_points = [0, *structural_boundaries, len(text)]
    units = tuple(
        (start, end)
        for start, end in zip(split_points, split_points[1:], strict=False)
        if start < end
    )
    if not units and text:
        units = ((0, len(text)),)
    return units, frozenset(structural_boundaries)


def _verify_structure_spans(
    text: str,
    structures: tuple[SourceRepresentationStructureRecord, ...],
) -> None:
    previous_index = -1
    for structure in structures:
        if structure.structure_index <= previous_index:
            raise SourceChunkIntegrityError("Representation structures are not index-ordered.")
        previous_index = structure.structure_index
        if not 0 <= structure.start_offset <= structure.end_offset <= len(text):
            raise SourceChunkIntegrityError(
                "Representation structure range is outside retained text."
            )


def _bounded_split_point(
    text: str,
    start: int,
    hard_end: int,
    *,
    preferred_boundaries: frozenset[int] = frozenset(),
) -> int:
    if hard_end >= len(text):
        return len(text)
    candidates = [
        boundary
        for boundary in preferred_boundaries
        if start < boundary <= hard_end
    ]
    if candidates:
        return max(candidates)
    for marker in ("\n\n", "\n", ". ", "; ", ", ", " "):
        position = text.rfind(marker, start + 1, hard_end + 1)
        if position >= start + 1:
            return position + len(marker)
    return hard_end
