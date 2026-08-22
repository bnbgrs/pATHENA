"""Durable identity helpers for Unified Local grounded chat."""

from __future__ import annotations

import json
import uuid

from athena.chat.request_fingerprint import (
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)

UNIFIED_GROUNDED_RECEIPT_VERSION = 1


def build_unified_grounded_fingerprint(
    *,
    chat_id: uuid.UUID,
    content: str,
    retrieval_query_override: str | None,
    requested_model_id: str | None,
    requested_embedding_model_id: str | None,
    max_memory_context_tokens: int,
    max_memory_context_items: int,
    max_memory_items: int,
    max_source_context_tokens: int,
    max_source_context_items: int,
    max_recent_conversation_turns: int,
    memory_scope_kind: str | None,
    memory_scope_entity_id: uuid.UUID | None,
    effective_context_limit: int | None,
    output_reserve: int,
    safety_margin: int,
    temperature: float | None,
    reasoning_mode: str | None,
    allow_model_prior: bool,
) -> ChatRequestFingerprint:
    """Fingerprint every caller-controlled input that can change durable output."""
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content=content,
        requested_model_id=requested_model_id,
        requested_embedding_model_id=requested_embedding_model_id,
        effective_context_limit=effective_context_limit,
        max_output_tokens=output_reserve,
        temperature=temperature,
        reasoning_mode=reasoning_mode,
        retrieval_configuration={
            "unified_local_request_version": 1,
            "retrieval_query_override": retrieval_query_override,
            "max_memory_context_tokens": max_memory_context_tokens,
            "max_memory_context_items": max_memory_context_items,
            "max_memory_items": max_memory_items,
            "max_source_context_tokens": max_source_context_tokens,
            "max_source_context_items": max_source_context_items,
            "max_recent_conversation_turns": max_recent_conversation_turns,
            "memory_scope_kind": memory_scope_kind,
            "memory_scope_entity_id": (
                None
                if memory_scope_entity_id is None
                else str(memory_scope_entity_id)
            ),
            "safety_margin": safety_margin,
            "allow_model_prior": allow_model_prior,
        },
    )


def build_unified_grounded_receipt(
    *,
    assistant_text: str,
    provider_id: str,
    model_id: str,
    operation_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    context_package_request_id: uuid.UUID,
    embedding_model_id: str | None,
) -> str:
    """Build the minimum crash-safe receipt for one Unified provider result."""
    return json.dumps(
        {
            "assistant_text": assistant_text,
            "context_package_request_id": str(context_package_request_id),
            "embedding_model_id": embedding_model_id,
            "model_id": model_id,
            "operation_id": str(operation_id),
            "processing_run_id": str(processing_run_id),
            "provider_id": provider_id,
            "unified_grounded_receipt_version": UNIFIED_GROUNDED_RECEIPT_VERSION,
        },
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )