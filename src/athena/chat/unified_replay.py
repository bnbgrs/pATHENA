"""Versioned exact-replay projection for durable Unified Local chat."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, cast

from athena.knowledge.models import EpistemicStatus
from athena.model.domain import ModelInfo
from athena.retrieval.context import ContextBundle, ContextItem, MemoryContextItem
from athena.retrieval.context_package import ContextPackage
from athena.retrieval.evidence import (
    EvidenceClass,
    MemoryEvidenceClassification,
    MemoryEvidenceSelection,
)
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType
from athena.retrieval.source_context import SourceContextBundle, SourceContextItem

UNIFIED_REPLAY_PROJECTION_VERSION = 1


class UnifiedReplayProjectionError(RuntimeError):
    """Persisted Unified replay data is missing, malformed, or misbound."""


@dataclass(frozen=True, slots=True)
class UnifiedReplayProjection:
    """Structured non-canonical values needed to replay one Unified result."""

    primary_model: ModelInfo
    embedding_model: ModelInfo | None
    memory_context: ContextBundle
    source_context: SourceContextBundle
    evidence_selection: MemoryEvidenceSelection


def build_unified_replay_projection(
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    context_package: ContextPackage,
    primary_model: ModelInfo,
    embedding_model: ModelInfo | None,
    memory_context: ContextBundle,
    source_context: SourceContextBundle,
    evidence_selection: MemoryEvidenceSelection,
) -> dict[str, Any]:
    """Encode one explicit, migratable Unified exact-replay projection."""
    _validate_projection_bindings(
        context_package=context_package,
        primary_model=primary_model,
        embedding_model=embedding_model,
        memory_context=memory_context,
        source_context=source_context,
        evidence_selection=evidence_selection,
    )
    return {
        "version": UNIFIED_REPLAY_PROJECTION_VERSION,
        "operation_id": str(operation_id),
        "chat_id": str(chat_id),
        "processing_run_id": str(processing_run_id),
        "context_package_request_id": str(context_package.request_id),
        "primary_model": _encode_model(primary_model),
        "embedding_model": (
            None if embedding_model is None else _encode_model(embedding_model)
        ),
        "memory_context": _encode_memory_context(memory_context),
        "source_context": _encode_source_context(source_context),
        "evidence_selection": _encode_evidence_selection(evidence_selection),
    }


def load_unified_replay_projection(
    *,
    receipt_payload_json: str,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    context_package: ContextPackage,
    provider_id: str,
    model_id: str,
) -> UnifiedReplayProjection:
    """Decode and strongly bind a persisted replay projection to durable state."""
    try:
        raw = json.loads(receipt_payload_json)
    except json.JSONDecodeError as exc:
        raise UnifiedReplayProjectionError(
            "Unified durable receipt is invalid JSON."
        ) from exc
    root = _object(raw, "Unified durable receipt")
    projection = _object(
        root.get("unified_replay_projection"),
        "unified_replay_projection",
    )
    if projection.get("version") != UNIFIED_REPLAY_PROJECTION_VERSION:
        raise UnifiedReplayProjectionError(
            "Unsupported Unified replay projection version."
        )
    _require_uuid(projection, "operation_id", operation_id)
    _require_uuid(projection, "chat_id", chat_id)
    _require_uuid(projection, "processing_run_id", processing_run_id)
    _require_uuid(
        projection,
        "context_package_request_id",
        context_package.request_id,
    )

    primary_model = _decode_model(
        _object(projection.get("primary_model"), "primary_model")
    )
    raw_embedding = projection.get("embedding_model")
    embedding_model = (
        None
        if raw_embedding is None
        else _decode_model(_object(raw_embedding, "embedding_model"))
    )
    memory_context = _decode_memory_context(
        _object(projection.get("memory_context"), "memory_context")
    )
    source_context = _decode_source_context(
        _object(projection.get("source_context"), "source_context")
    )
    evidence_selection = _decode_evidence_selection(
        _object(projection.get("evidence_selection"), "evidence_selection")
    )

    if primary_model.provider != provider_id or primary_model.backend_model_id != model_id:
        raise UnifiedReplayProjectionError(
            "Unified replay primary-model identity conflicts with provider result."
        )
    _validate_projection_bindings(
        context_package=context_package,
        primary_model=primary_model,
        embedding_model=embedding_model,
        memory_context=memory_context,
        source_context=source_context,
        evidence_selection=evidence_selection,
    )
    return UnifiedReplayProjection(
        primary_model=primary_model,
        embedding_model=embedding_model,
        memory_context=memory_context,
        source_context=source_context,
        evidence_selection=evidence_selection,
    )


def _validate_projection_bindings(
    *,
    context_package: ContextPackage,
    primary_model: ModelInfo,
    embedding_model: ModelInfo | None,
    memory_context: ContextBundle,
    source_context: SourceContextBundle,
    evidence_selection: MemoryEvidenceSelection,
) -> None:
    signature = context_package.model_signature
    if (
        primary_model.provider != signature.provider
        or primary_model.backend_model_id != signature.model_identifier
        or primary_model.quantization != signature.quantization
    ):
        raise UnifiedReplayProjectionError(
            "Unified replay primary model conflicts with ContextPackage signature."
        )

    try:
        configuration = json.loads(signature.context_configuration_json or "{}")
    except json.JSONDecodeError as exc:
        raise UnifiedReplayProjectionError(
            "Unified ContextPackage configuration is invalid JSON."
        ) from exc
    if not isinstance(configuration, dict):
        raise UnifiedReplayProjectionError(
            "Unified ContextPackage configuration must be a JSON object."
        )
    configured_embedding = configuration.get("embedding_model_id")
    actual_embedding = (
        None if embedding_model is None else embedding_model.backend_model_id
    )
    if configured_embedding != actual_embedding:
        raise UnifiedReplayProjectionError(
            "Unified replay embedding model conflicts with ContextPackage configuration."
        )
    if configuration.get("evidence_policy_id") != evidence_selection.policy_id:
        raise UnifiedReplayProjectionError(
            "Unified replay evidence policy conflicts with ContextPackage configuration."
        )

    refs = {item.ref_id: item for item in context_package.included_refs}
    for personal_item in memory_context.memory_items:
        ref = refs.get(personal_item.context_id)
        if (
            ref is None
            or ref.entity_type != "personal_memory"
            or ref.entity_id != personal_item.memory_id
            or ref.revision_id != personal_item.revision_id
        ):
            raise UnifiedReplayProjectionError(
                "Unified replay Personal Memory item conflicts with ContextPackage refs."
            )
    for canonical_item in memory_context.items:
        ref = refs.get(canonical_item.context_id)
        if (
            ref is None
            or ref.entity_type != canonical_item.entity_type.value
            or ref.entity_id != canonical_item.entity_id
            or ref.revision_id != canonical_item.revision_id
        ):
            raise UnifiedReplayProjectionError(
                "Unified replay canonical context item conflicts with ContextPackage refs."
            )
        classification = evidence_selection.classification_for(
            entity_type=canonical_item.entity_type,
            entity_id=canonical_item.entity_id,
            revision_id=canonical_item.revision_id,
        )
        if classification.evidence_class is not EvidenceClass.CANONICAL:
            raise UnifiedReplayProjectionError(
                "Unified replay canonical context lost canonical evidence classification."
            )
    for source_item in source_context.items:
        ref = refs.get(source_item.context_id)
        if (
            ref is None
            or ref.entity_type != "source_anchor"
            or ref.entity_id != source_item.anchor_id
            or ref.revision_id is not None
        ):
            raise UnifiedReplayProjectionError(
                "Unified replay source context item conflicts with ContextPackage refs."
            )

    context_ids = tuple(item.context_id for item in memory_context.items) + tuple(
        item.context_id for item in source_context.items
    )
    if len(set(context_ids)) != len(context_ids):
        raise UnifiedReplayProjectionError(
            "Unified replay context IDs are not unique across retrieval domains."
        )


def _encode_model(model: ModelInfo) -> dict[str, Any]:
    return {
        "provider": model.provider,
        "backend_model_id": model.backend_model_id,
        "display_name": model.display_name,
        "model_type": model.model_type,
        "context_capacity": model.context_capacity,
        "quantization": model.quantization,
        "loaded": model.loaded,
        "vision": model.vision,
        "trained_for_tool_use": model.trained_for_tool_use,
        "loaded_context_length": model.loaded_context_length,
    }


def _decode_model(raw: dict[str, Any]) -> ModelInfo:
    return ModelInfo(
        provider=_str(raw, "provider"),
        backend_model_id=_str(raw, "backend_model_id"),
        display_name=_str(raw, "display_name"),
        model_type=_str(raw, "model_type"),
        context_capacity=_optional_int(raw, "context_capacity"),
        quantization=_optional_str(raw, "quantization"),
        loaded=_bool(raw, "loaded"),
        vision=_optional_bool(raw, "vision"),
        trained_for_tool_use=_optional_bool(raw, "trained_for_tool_use"),
        loaded_context_length=_optional_int(raw, "loaded_context_length"),
    )


def _encode_memory_context(bundle: ContextBundle) -> dict[str, Any]:
    return {
        "query": bundle.query,
        "mode": bundle.mode,
        "memory_items": [
            {
                "context_id": item.context_id,
                "memory_id": str(item.memory_id),
                "revision_id": str(item.revision_id),
                "memory_kind": item.memory_kind,
                "scope_kind": item.scope_kind,
                "scope_entity_id": (
                    None if item.scope_entity_id is None else str(item.scope_entity_id)
                ),
                "content": item.content,
            }
            for item in bundle.memory_items
        ],
        "items": [
            {
                "context_id": item.context_id,
                "entity_id": str(item.entity_id),
                "revision_id": str(item.revision_id),
                "entity_type": item.entity_type.value,
                "title": item.title,
                "text": item.text,
                "score": item.score,
                "contradiction_count": item.contradiction_count,
                "duplicate_count": item.duplicate_count,
                "truncated": item.truncated,
            }
            for item in bundle.items
        ],
        "omitted_memory_count": bundle.omitted_memory_count,
        "omitted_count": bundle.omitted_count,
        "estimated_tokens": bundle.estimated_tokens,
        "max_estimated_tokens": bundle.max_estimated_tokens,
        "rendered_text": bundle.rendered_text,
    }


def _decode_memory_context(raw: dict[str, Any]) -> ContextBundle:
    mode = _str(raw, "mode")
    if mode not in {"lexical", "hybrid"}:
        raise UnifiedReplayProjectionError("Unified replay memory-context mode is invalid.")
    memory_items = tuple(
        MemoryContextItem(
            context_id=_str(item, "context_id"),
            memory_id=_uuid(item, "memory_id"),
            revision_id=_uuid(item, "revision_id"),
            memory_kind=_str(item, "memory_kind"),
            scope_kind=_str(item, "scope_kind"),
            scope_entity_id=_optional_uuid(item, "scope_entity_id"),
            content=_str(item, "content"),
        )
        for item in _object_list(raw, "memory_items")
    )
    items = tuple(
        ContextItem(
            context_id=_str(item, "context_id"),
            entity_id=_uuid(item, "entity_id"),
            revision_id=_uuid(item, "revision_id"),
            entity_type=_enum(SearchEntityType, item, "entity_type"),
            title=_optional_str(item, "title"),
            text=_str(item, "text"),
            score=_float(item, "score"),
            contradiction_count=_int(item, "contradiction_count"),
            duplicate_count=_int(item, "duplicate_count"),
            truncated=_bool(item, "truncated"),
        )
        for item in _object_list(raw, "items")
    )
    return ContextBundle(
        query=_str(raw, "query"),
        mode=cast(Any, mode),
        memory_items=memory_items,
        items=items,
        omitted_memory_count=_int(raw, "omitted_memory_count"),
        omitted_count=_int(raw, "omitted_count"),
        estimated_tokens=_int(raw, "estimated_tokens"),
        max_estimated_tokens=_int(raw, "max_estimated_tokens"),
        rendered_text=_str(raw, "rendered_text"),
    )


def _encode_source_context(bundle: SourceContextBundle) -> dict[str, Any]:
    return {
        "query": bundle.query,
        "mode": bundle.mode,
        "items": [
            {
                "context_id": item.context_id,
                "anchor_id": str(item.anchor_id),
                "source_id": str(item.source_id),
                "representation_id": str(item.representation_id),
                "start_offset": item.start_offset,
                "end_offset": item.end_offset,
                "page_start": item.page_start,
                "page_end": item.page_end,
                "quoted_hash_hex": item.quoted_hash.hex(),
                "source_name": item.source_name,
                "source_uri": item.source_uri,
                "text": item.text,
                "score": item.score,
                "lexical_score": item.lexical_score,
                "semantic_score": item.semantic_score,
                "truncated": item.truncated,
            }
            for item in bundle.items
        ],
        "omitted_count": bundle.omitted_count,
        "estimated_tokens": bundle.estimated_tokens,
        "max_estimated_tokens": bundle.max_estimated_tokens,
        "rendered_text": bundle.rendered_text,
    }


def _decode_source_context(raw: dict[str, Any]) -> SourceContextBundle:
    if _str(raw, "mode") != "archive_hybrid":
        raise UnifiedReplayProjectionError("Unified replay source-context mode is invalid.")
    return SourceContextBundle(
        query=_str(raw, "query"),
        mode="archive_hybrid",
        items=tuple(
            SourceContextItem(
                context_id=_str(item, "context_id"),
                anchor_id=_uuid(item, "anchor_id"),
                source_id=_uuid(item, "source_id"),
                representation_id=_uuid(item, "representation_id"),
                start_offset=_int(item, "start_offset"),
                end_offset=_int(item, "end_offset"),
                page_start=_optional_int(item, "page_start"),
                page_end=_optional_int(item, "page_end"),
                quoted_hash=_hex_bytes(item, "quoted_hash_hex", 32),
                source_name=_optional_str(item, "source_name"),
                source_uri=_optional_str(item, "source_uri"),
                text=_str(item, "text"),
                score=_float(item, "score"),
                lexical_score=_float(item, "lexical_score"),
                semantic_score=_float(item, "semantic_score"),
                truncated=_bool(item, "truncated"),
            )
            for item in _object_list(raw, "items")
        ),
        omitted_count=_int(raw, "omitted_count"),
        estimated_tokens=_int(raw, "estimated_tokens"),
        max_estimated_tokens=_int(raw, "max_estimated_tokens"),
        rendered_text=_str(raw, "rendered_text"),
    )


def _encode_evidence_selection(selection: MemoryEvidenceSelection) -> dict[str, Any]:
    return {
        "policy_id": selection.policy_id,
        "results": [
            {
                "entity_id": str(item.entity_id),
                "revision_id": str(item.revision_id),
                "entity_type": item.entity_type.value,
                "title": item.title,
                "text": item.text,
                "score": item.score,
                "lexical_score": item.lexical_score,
                "semantic_score": item.semantic_score,
                "authority_score": item.authority_score,
                "contradiction_count": item.contradiction_count,
                "duplicate_count": item.duplicate_count,
            }
            for item in selection.results
        ],
        "classifications": [
            {
                "entity_id": str(item.entity_id),
                "revision_id": str(item.revision_id),
                "entity_type": item.entity_type.value,
                "evidence_class": item.evidence_class.value,
                "message_type": item.message_type,
                "epistemic_status": (
                    None if item.epistemic_status is None else item.epistemic_status.value
                ),
            }
            for item in selection.classifications
        ],
    }


def _decode_evidence_selection(raw: dict[str, Any]) -> MemoryEvidenceSelection:
    results = tuple(
        HybridSearchResult(
            entity_id=_uuid(item, "entity_id"),
            revision_id=_uuid(item, "revision_id"),
            entity_type=_enum(SearchEntityType, item, "entity_type"),
            title=_optional_str(item, "title"),
            text=_str(item, "text"),
            score=_float(item, "score"),
            lexical_score=_float(item, "lexical_score"),
            semantic_score=_float(item, "semantic_score"),
            authority_score=_float(item, "authority_score"),
            contradiction_count=_int(item, "contradiction_count"),
            duplicate_count=_int(item, "duplicate_count"),
        )
        for item in _object_list(raw, "results")
    )
    classifications = tuple(
        MemoryEvidenceClassification(
            entity_id=_uuid(item, "entity_id"),
            revision_id=_uuid(item, "revision_id"),
            entity_type=_enum(SearchEntityType, item, "entity_type"),
            evidence_class=_enum(EvidenceClass, item, "evidence_class"),
            message_type=_optional_str(item, "message_type"),
            epistemic_status=(
                None
                if item.get("epistemic_status") is None
                else _enum(EpistemicStatus, item, "epistemic_status")
            ),
        )
        for item in _object_list(raw, "classifications")
    )
    if len(results) != len(classifications):
        raise UnifiedReplayProjectionError(
            "Unified replay evidence results/classifications have different sizes."
        )
    result_keys = {
        (item.entity_type, item.entity_id, item.revision_id) for item in results
    }
    classification_keys = {
        (item.entity_type, item.entity_id, item.revision_id) for item in classifications
    }
    if result_keys != classification_keys or len(result_keys) != len(results):
        raise UnifiedReplayProjectionError(
            "Unified replay evidence selection has inconsistent identities."
        )
    return MemoryEvidenceSelection(
        policy_id=_str(raw, "policy_id"),
        results=results,
        classifications=classifications,
    )


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise UnifiedReplayProjectionError(f"{label} must be a JSON object.")
    return cast(dict[str, Any], value)


def _object_list(raw: dict[str, Any], key: str) -> tuple[dict[str, Any], ...]:
    value = raw.get(key)
    if not isinstance(value, list):
        raise UnifiedReplayProjectionError(f"{key} must be a JSON array.")
    return tuple(_object(item, key) for item in value)


def _str(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value:
        raise UnifiedReplayProjectionError(f"{key} must be a non-empty string.")
    return value


def _optional_str(raw: dict[str, Any], key: str) -> str | None:
    value = raw.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise UnifiedReplayProjectionError(f"{key} must be a string or null.")
    return value


def _int(raw: dict[str, Any], key: str) -> int:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise UnifiedReplayProjectionError(f"{key} must be an integer.")
    return value


def _optional_int(raw: dict[str, Any], key: str) -> int | None:
    value = raw.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise UnifiedReplayProjectionError(f"{key} must be an integer or null.")
    return value


def _float(raw: dict[str, Any], key: str) -> float:
    value = raw.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UnifiedReplayProjectionError(f"{key} must be numeric.")
    return float(value)


def _bool(raw: dict[str, Any], key: str) -> bool:
    value = raw.get(key)
    if not isinstance(value, bool):
        raise UnifiedReplayProjectionError(f"{key} must be boolean.")
    return value


def _optional_bool(raw: dict[str, Any], key: str) -> bool | None:
    value = raw.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise UnifiedReplayProjectionError(f"{key} must be boolean or null.")
    return value


def _uuid(raw: dict[str, Any], key: str) -> uuid.UUID:
    value = _str(raw, key)
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise UnifiedReplayProjectionError(f"{key} must be a UUID string.") from exc


def _optional_uuid(raw: dict[str, Any], key: str) -> uuid.UUID | None:
    value = raw.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise UnifiedReplayProjectionError(f"{key} must be a UUID string or null.")
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise UnifiedReplayProjectionError(f"{key} must be a UUID string or null.") from exc


def _require_uuid(raw: dict[str, Any], key: str, expected: uuid.UUID) -> None:
    if _uuid(raw, key) != expected:
        raise UnifiedReplayProjectionError(
            f"Unified replay {key} conflicts with durable operation state."
        )


def _hex_bytes(raw: dict[str, Any], key: str, expected_length: int) -> bytes:
    value = _str(raw, key)
    try:
        decoded = bytes.fromhex(value)
    except ValueError as exc:
        raise UnifiedReplayProjectionError(f"{key} must be hexadecimal bytes.") from exc
    if len(decoded) != expected_length:
        raise UnifiedReplayProjectionError(
            f"{key} must decode to {expected_length} bytes."
        )
    return decoded


def _enum(enum_type: type[Any], raw: dict[str, Any], key: str) -> Any:
    value = _str(raw, key)
    try:
        return enum_type(value)
    except ValueError as exc:
        raise UnifiedReplayProjectionError(f"{key} has an unsupported value.") from exc
