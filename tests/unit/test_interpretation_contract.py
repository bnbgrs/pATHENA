from __future__ import annotations

import uuid

import pytest

from athena.knowledge.interpretation import (
    InterpretationInputRevision,
    InterpretationOrigin,
    InterpretationProposal,
)


def _input_revision() -> InterpretationInputRevision:
    return InterpretationInputRevision(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
    )


def test_user_interpretation_carries_actor_without_model_provenance() -> None:
    actor_id = uuid.uuid4()
    source = _input_revision()

    proposal = InterpretationProposal.user(
        text="The source set suggests a change in strategy.",
        actor_id=actor_id,
        input_revisions=(source,),
    )

    assert proposal.interpretation_id.version == 7
    assert proposal.origin is InterpretationOrigin.USER
    assert proposal.actor_id == actor_id
    assert proposal.input_revisions == (source,)
    assert proposal.model_signature_id is None
    assert proposal.processing_run_id is None
    assert proposal.pipeline_version is None


def test_model_interpretation_requires_and_preserves_exact_provenance() -> None:
    model_signature_id = uuid.uuid4()
    processing_run_id = uuid.uuid4()
    sources = (_input_revision(), _input_revision())

    proposal = InterpretationProposal.model(
        text="The two sources together suggest a strategy change.",
        model_signature_id=model_signature_id,
        processing_run_id=processing_run_id,
        input_revisions=sources,
        pipeline_version="knowledge-interpretation-v1",
    )

    assert proposal.interpretation_id.version == 7
    assert proposal.origin is InterpretationOrigin.MODEL
    assert proposal.actor_id is None
    assert proposal.model_signature_id == model_signature_id
    assert proposal.processing_run_id == processing_run_id
    assert proposal.input_revisions == sources
    assert proposal.pipeline_version == "knowledge-interpretation-v1"


@pytest.mark.parametrize(
    ("input_revisions", "pipeline_version"),
    [
        ((), "knowledge-interpretation-v1"),
        ((_input_revision(),), ""),
        ((_input_revision(),), "   "),
    ],
)
def test_model_interpretation_fails_closed_on_incomplete_provenance(
    input_revisions: tuple[InterpretationInputRevision, ...],
    pipeline_version: str,
) -> None:
    with pytest.raises(ValueError):
        InterpretationProposal.model(
            text="A model-generated interpretation.",
            model_signature_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            input_revisions=input_revisions,
            pipeline_version=pipeline_version,
        )


def test_user_interpretation_cannot_claim_model_provenance() -> None:
    with pytest.raises(ValueError, match="must not claim model provenance"):
        InterpretationProposal(
            interpretation_id=uuid.uuid4(),
            created_at_us=1,
            text="A user-authored interpretation.",
            origin=InterpretationOrigin.USER,
            input_revisions=(),
            actor_id=uuid.uuid4(),
            model_signature_id=uuid.uuid4(),
        )


def test_model_interpretation_cannot_claim_user_authorship() -> None:
    with pytest.raises(ValueError, match="must not claim user authorship"):
        InterpretationProposal(
            interpretation_id=uuid.uuid4(),
            created_at_us=1,
            text="A model-authored interpretation.",
            origin=InterpretationOrigin.MODEL,
            input_revisions=(_input_revision(),),
            actor_id=uuid.uuid4(),
            model_signature_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            pipeline_version="knowledge-interpretation-v1",
        )


def test_interpretation_proposals_coexist_without_overwriting_identity() -> None:
    actor_id = uuid.uuid4()

    first = InterpretationProposal.user(text="Interpretation A", actor_id=actor_id)
    second = InterpretationProposal.user(text="Interpretation B", actor_id=actor_id)

    assert first.interpretation_id != second.interpretation_id
    assert first.text == "Interpretation A"
    assert second.text == "Interpretation B"
