"""Deterministic identity keys for durable Research work."""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Mapping, Sequence
from typing import Any

from athena.research.models import (
    ResearchSynthesisInputKind,
    ResearchSynthesisStage,
)
from athena.research.validation import _canonical_json_value


def _uuid_value(value: object, label: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{label} must be a UUID.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must not be negative.")
    return value


def _canonical_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text.")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be canonical non-empty text.")
    return value


def _synthesis_work_idempotency_key(
    *,
    scope_id: uuid.UUID,
    stage: ResearchSynthesisStage,
    level: int,
    ordinal: int,
    inputs: object,
    descriptor: object,
    pipeline_version: str,
    prompt_template_id: str,
    prompt_template_version: str,
) -> bytes:
    validated_scope_id = _uuid_value(scope_id, "Research synthesis scope_id")
    if not isinstance(stage, ResearchSynthesisStage):
        raise TypeError("Research synthesis stage must be a ResearchSynthesisStage.")
    validated_level = _nonnegative_int(level, "Research synthesis level")
    validated_ordinal = _nonnegative_int(ordinal, "Research synthesis ordinal")
    if not isinstance(inputs, Sequence) or isinstance(inputs, (str, bytes, bytearray)):
        raise TypeError("Research synthesis inputs must be a sequence.")
    normalized_inputs: list[tuple[ResearchSynthesisInputKind, uuid.UUID]] = []
    for item in inputs:
        if not isinstance(item, tuple) or len(item) != 2:
            raise TypeError("Research synthesis inputs must contain (kind, UUID) tuples.")
        kind, ref_id = item
        if not isinstance(kind, ResearchSynthesisInputKind):
            raise TypeError("Research synthesis input kind is invalid.")
        normalized_inputs.append(
            (kind, _uuid_value(ref_id, "Research synthesis input reference"))
        )
    if not isinstance(descriptor, Mapping):
        raise TypeError("Research synthesis descriptor must be a mapping.")
    validated_pipeline = _canonical_text(
        pipeline_version,
        "Research synthesis pipeline_version",
    )
    validated_prompt_id = _canonical_text(
        prompt_template_id,
        "Research synthesis prompt_template_id",
    )
    validated_prompt_version = _canonical_text(
        prompt_template_version,
        "Research synthesis prompt_template_version",
    )

    identity = {
        "scope_id": str(validated_scope_id),
        "stage": stage.value,
        "level": validated_level,
        "ordinal": validated_ordinal,
        "inputs": [
            {"kind": kind.value, "id": str(ref_id)}
            for kind, ref_id in normalized_inputs
        ],
        "descriptor": dict(descriptor),
        "pipeline_version": validated_pipeline,
        "prompt_template_id": validated_prompt_id,
        "prompt_template_version": validated_prompt_version,
    }
    digest = hashlib.sha256()
    digest.update(b"athena.exhaustive-research.synthesis-work.v1\0")
    digest.update(_canonical_json_value(identity).encode("utf-8"))
    return digest.digest()


def _work_idempotency_key(
    *,
    scope_id: uuid.UUID,
    source_id: uuid.UUID,
    content_sha256: bytes,
) -> bytes:
    validated_scope_id = _uuid_value(scope_id, "Research work scope_id")
    validated_source_id = _uuid_value(source_id, "Research work source_id")
    if not isinstance(content_sha256, bytes):
        raise TypeError("Research work content_sha256 must be bytes.")
    if len(content_sha256) != 32:
        raise ValueError("Research work content_sha256 must be a 32-byte SHA-256 digest.")

    digest = hashlib.sha256()
    digest.update(b"athena.exhaustive-research.work.v1\0")
    digest.update(validated_scope_id.bytes)
    digest.update(validated_source_id.bytes)
    digest.update(content_sha256)
    return digest.digest()
