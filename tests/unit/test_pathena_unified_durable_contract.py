from __future__ import annotations

import json
import uuid

from athena.chat.grounded_provider_result_contract import validate_provider_result_contract
from athena.chat.unified_durable import (
    build_unified_grounded_fingerprint,
    build_unified_grounded_receipt,
)


def _fingerprint(
    chat_id: uuid.UUID,
    *,
    content: str = "hello",
    retrieval_query_override: str | None = None,
    allow_model_prior: bool = True,
):
    return build_unified_grounded_fingerprint(
        chat_id=chat_id,
        content=content,
        retrieval_query_override=retrieval_query_override,
        requested_model_id="primary",
        requested_embedding_model_id="embedding",
        max_memory_context_tokens=1200,
        max_memory_context_items=8,
        max_memory_items=8,
        max_source_context_tokens=1200,
        max_source_context_items=8,
        max_recent_conversation_turns=8,
        memory_scope_kind="global",
        memory_scope_entity_id=None,
        effective_context_limit=4096,
        output_reserve=1024,
        safety_margin=256,
        temperature=0.2,
        reasoning_mode="off",
        allow_model_prior=allow_model_prior,
    )


def test_unified_fingerprint_is_stable_for_identical_request() -> None:
    chat_id = uuid.uuid4()
    assert _fingerprint(chat_id) == _fingerprint(chat_id)


def test_unified_fingerprint_changes_for_retrieval_override() -> None:
    chat_id = uuid.uuid4()
    assert _fingerprint(chat_id) != _fingerprint(
        chat_id,
        retrieval_query_override="different retrieval intent",
    )


def test_unified_fingerprint_changes_for_grounding_policy() -> None:
    chat_id = uuid.uuid4()
    assert _fingerprint(chat_id) != _fingerprint(
        chat_id,
        allow_model_prior=False,
    )


def test_unified_receipt_binds_operation_run_package_and_model() -> None:
    operation_id = uuid.uuid4()
    run_id = uuid.uuid4()
    package_id = uuid.uuid4()
    payload_json = build_unified_grounded_receipt(
        assistant_text="answer",
        provider_id="lm_studio",
        model_id="primary",
        operation_id=operation_id,
        processing_run_id=run_id,
        context_package_request_id=package_id,
        embedding_model_id="embedding",
    )
    validate_provider_result_contract(
        assistant_content="answer",
        receipt_payload_json=payload_json,
    )
    payload = json.loads(payload_json)
    assert payload["operation_id"] == str(operation_id)
    assert payload["processing_run_id"] == str(run_id)
    assert payload["context_package_request_id"] == str(package_id)
    assert payload["provider_id"] == "lm_studio"
    assert payload["model_id"] == "primary"
    assert payload["embedding_model_id"] == "embedding"
    assert payload["unified_grounded_receipt_version"] == 1