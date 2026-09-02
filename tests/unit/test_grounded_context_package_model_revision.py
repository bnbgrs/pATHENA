from __future__ import annotations

import json
import uuid

from athena.chat.grounded_context_package import _decode_package, _encode_package
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextModelSignature,
    ContextPackage,
    ContextPackageBudget,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)


def _package(*, model_revision: str | None) -> ContextPackage:
    message_id = uuid.uuid4()
    return ContextPackage(
        request_id=uuid.uuid4(),
        model_signature=ContextModelSignature(
            model_signature_id=uuid.uuid4(),
            provider="lm_studio",
            model_identifier="model",
            model_revision=model_revision,
            quantization=None,
            generation_parameters_json='{"reasoning_mode":"off"}',
            context_configuration_json=None,
            signature_hash_hex="00" * 32,
        ),
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=3000,
            output_reserve=512,
            safety_margin=128,
        ),
        sections=(
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
                entity_id=message_id,
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
            current_user_tokens=1,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=1,
            estimated_total_tokens=641,
        ),
        snapshot_commit_seq=0,
    )


def test_grounded_context_package_preserves_model_revision_roundtrip() -> None:
    encoded, digest = _encode_package(_package(model_revision="revision-7"))

    decoded = _decode_package(encoded, digest)

    assert decoded.model_signature.model_revision == "revision-7"
    assert json.loads(encoded)["model_signature"]["model_revision"] == "revision-7"


def test_grounded_context_package_decodes_legacy_payload_without_model_revision() -> None:
    encoded, _digest = _encode_package(_package(model_revision=None))
    payload = json.loads(encoded)
    del payload["model_signature"]["model_revision"]
    legacy = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    import hashlib

    digest = hashlib.sha256(legacy.encode("utf-8")).hexdigest()

    decoded = _decode_package(legacy, digest)

    assert decoded.model_signature.model_revision is None
