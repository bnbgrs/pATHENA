from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge_model_disclosure import disclose_knowledge_revision_model
from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
)
from athena.model.provenance import ModelSignature, ProcessingRun


KNOWLEDGE_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
REVISION_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
ACTOR_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")
PROVENANCE_ID = uuid.UUID("44444444-4444-4444-8444-444444444444")
SIGNATURE_ID = uuid.UUID("55555555-5555-4555-8555-555555555555")
RUN_ID = uuid.UUID("66666666-6666-4666-8666-666666666666")


def _revision() -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=KNOWLEDGE_ID,
        revision_id=REVISION_ID,
        revision_no=2,
        created_at_us=2_000_000,
        created_by_actor_id=ACTOR_ID,
        provenance_id=PROVENANCE_ID,
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title="Recorded fact",
            body="The persisted body.",
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )


def _signature() -> ModelSignature:
    return ModelSignature(
        model_signature_id=SIGNATURE_ID,
        provider="lm_studio",
        model_identifier="local-model",
        model_revision="rev-7",
        quantization="Q4_K_M",
        generation_parameters_json='{"temperature":0.2}',
        context_configuration_json='{"context_length":8192}',
        signature_hash=b"s" * 32,
        created_at_us=1_000_000,
    )


def _run(*, signature_id: uuid.UUID | None = SIGNATURE_ID, status: str = "succeeded") -> ProcessingRun:
    return ProcessingRun(
        processing_run_id=RUN_ID,
        run_type="knowledge.extraction",
        started_at_us=1_100_000,
        finished_at_us=1_200_000 if status != "running" else None,
        status=status,
        trigger_actor_id=ACTOR_ID,
        pipeline_version="knowledge-v3",
        input_snapshot_json='{"message_revision":"abc"}',
        configuration_hash=b"c" * 32,
        model_signature_id=signature_id,
        prompt_template_id="knowledge.extract",
        prompt_template_version="3",
        error_detail=None,
    )


def test_user_revision_discloses_no_model_without_fabrication() -> None:
    response = disclose_knowledge_revision_model(_revision(), actor_kind="user")

    assert response.knowledge_id == str(KNOWLEDGE_ID)
    assert response.revision_id == str(REVISION_ID)
    assert response.actor_kind == "user"
    assert response.model_generated is False
    assert response.provider is None
    assert response.model_identifier is None
    assert response.model_revision is None
    assert response.processing_run_id is None


def test_primary_model_revision_discloses_recorded_signature_and_run() -> None:
    response = disclose_knowledge_revision_model(
        _revision(),
        actor_kind="primary_model",
        processing_run=_run(),
        model_signature=_signature(),
    )

    assert response.model_generated is True
    assert response.provider == "lm_studio"
    assert response.model_identifier == "local-model"
    assert response.model_revision == "rev-7"
    assert response.quantization == "Q4_K_M"
    assert response.processing_run_id == str(RUN_ID)
    assert response.pipeline_version == "knowledge-v3"
    assert response.prompt_template_id == "knowledge.extract"
    assert response.prompt_template_version == "3"


def test_primary_model_revision_without_model_provenance_fails_closed() -> None:
    with pytest.raises(ValueError, match="require ProcessingRun and ModelSignature"):
        disclose_knowledge_revision_model(_revision(), actor_kind="primary_model")


def test_partial_model_provenance_fails_closed() -> None:
    with pytest.raises(ValueError, match="requires ProcessingRun and ModelSignature together"):
        disclose_knowledge_revision_model(
            _revision(),
            actor_kind="system",
            processing_run=_run(),
        )


def test_mismatched_processing_run_signature_fails_closed() -> None:
    with pytest.raises(ValueError, match="another ModelSignature"):
        disclose_knowledge_revision_model(
            _revision(),
            actor_kind="primary_model",
            processing_run=_run(signature_id=uuid.UUID("77777777-7777-4777-8777-777777777777")),
            model_signature=_signature(),
        )


def test_failed_processing_run_is_not_presented_as_model_provenance() -> None:
    with pytest.raises(ValueError, match="succeeded ProcessingRun"):
        disclose_knowledge_revision_model(
            _revision(),
            actor_kind="primary_model",
            processing_run=_run(status="failed"),
            model_signature=_signature(),
        )


def test_user_revision_rejects_fabricated_model_participation() -> None:
    with pytest.raises(ValueError, match="must not claim model provenance"):
        disclose_knowledge_revision_model(
            _revision(),
            actor_kind="user",
            processing_run=_run(),
            model_signature=_signature(),
        )
