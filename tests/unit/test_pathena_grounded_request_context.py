from __future__ import annotations

import hashlib
import json
import uuid

import pytest

from athena.chat.grounded_request_context import (
    GroundedRequestContextBindingError,
    validate_grounded_request_context_binding,
)
from athena.chat.request_fingerprint import (
    ChatRequestFingerprint,
    ChatSendMode,
    build_chat_request_fingerprint,
)
from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _package(operation_id: uuid.UUID):
    signature = ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization="Q4_K_M",
        generation_parameters_json='{"max_output_tokens":1000,"reasoning_mode":"off"}',
        context_configuration_json='{"context_package_version":1}',
        signature_hash=b"s" * 32,
        created_at_us=1,
    )
    return ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="system",
                role="system",
                content="system",
                included_ref_ids=(),
            ),
            ContextSection(
                name="current_user",
                role="user",
                content="hello",
                included_ref_ids=("CURRENT-USER",),
            ),
        ),
        included_refs=(
            ContextIncludedRef(
                ref_id="CURRENT-USER",
                entity_type="chat_message",
                entity_id=operation_id,
                revision_id=uuid.uuid4(),
            ),
        ),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=0,
            conversation_included_count=0,
            conversation_excluded_count=0,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=10,
            context_tokens=0,
            estimated_input_tokens=20,
            estimated_total_tokens=1220,
        ),
        snapshot_commit_seq=1,
    )


def _fingerprint(chat_id: uuid.UUID, *, mode: ChatSendMode = ChatSendMode.GROUNDED):
    return build_chat_request_fingerprint(
        mode=mode,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
    )


def test_valid_grounded_request_context_binding_is_accepted() -> None:
    validate_grounded_request_context_binding(
        package=_package(uuid.uuid4()),
        fingerprint=_fingerprint(uuid.uuid4()),
    )


def test_grounded_request_context_rejects_bad_fingerprint_checksum() -> None:
    fingerprint = _fingerprint(uuid.uuid4())
    corrupted = ChatRequestFingerprint(
        payload_json=fingerprint.payload_json,
        payload_sha256="0" * 64,
        format_version=fingerprint.format_version,
    )
    with pytest.raises(
        GroundedRequestContextBindingError,
        match="checksum",
    ):
        validate_grounded_request_context_binding(
            package=_package(uuid.uuid4()),
            fingerprint=corrupted,
        )


def test_grounded_request_context_rejects_direct_mode() -> None:
    with pytest.raises(
        GroundedRequestContextBindingError,
        match="Grounded mode",
    ):
        validate_grounded_request_context_binding(
            package=_package(uuid.uuid4()),
            fingerprint=_fingerprint(uuid.uuid4(), mode=ChatSendMode.DIRECT),
        )


def test_grounded_request_context_rejects_payload_version_drift() -> None:
    fingerprint = _fingerprint(uuid.uuid4())
    payload = json.loads(fingerprint.payload_json)
    assert isinstance(payload, dict)
    payload["fingerprint_format_version"] = 99
    payload_json = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    drifted = ChatRequestFingerprint(
        payload_json=payload_json,
        payload_sha256=hashlib.sha256(payload_json.encode("utf-8")).hexdigest(),
        format_version=fingerprint.format_version,
    )
    with pytest.raises(
        GroundedRequestContextBindingError,
        match="payload version is inconsistent",
    ):
        validate_grounded_request_context_binding(
            package=_package(uuid.uuid4()),
            fingerprint=drifted,
        )