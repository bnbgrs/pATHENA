from __future__ import annotations

from athena.desktop.pathena_research_proposal_clarity_2600 import (
    _REFINEMENTS,
    _TARGETS,
    _evidence_from_tooltip,
    _parse_payload_text,
    _shorten,
    _summary,
    UI_REFINEMENT_TASKS_2501_2600,
)


def test_research_proposal_clarity_defines_exactly_100_tasks() -> None:
    assert len(_TARGETS) == 20
    assert len(_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2501_2600) == 100
    assert len(set(UI_REFINEMENT_TASKS_2501_2600)) == 100


def test_existing_humanized_proposal_row_is_parsed_without_domain_changes() -> None:
    parsed = _parse_payload_text(
        'Claim · Pending · {"statement":"A durable finding","epistemic_status":"supported"}'
    )
    assert parsed is not None
    proposal_type, state, payload = parsed
    assert proposal_type == "claim"
    assert state == "pending"
    assert payload["statement"] == "A durable finding"


def test_payload_meaning_is_selected_by_frozen_athena_proposal_type() -> None:
    assert _summary("knowledge", {"title": "Research summary", "body": "Body"}) == (
        "Research summary"
    )
    assert _summary("claim", {"statement": "Observed fact"}) == "Observed fact"
    assert _summary("contradiction", {"text": "Sources disagree"}) == "Sources disagree"


def test_evidence_context_is_humanized_without_losing_ordinal() -> None:
    assert _evidence_from_tooltip("id\nevidence=finding:0\naccepted_entity=-") == (
        "Evidence · Finding 1"
    )
    assert _evidence_from_tooltip("id\nevidence=summary:-\naccepted_entity=-") == (
        "Evidence · Summary"
    )


def test_long_payload_copy_is_bounded_for_scanability() -> None:
    value = _shorten("x" * 200, limit=40)
    assert len(value) == 40
    assert value.endswith("…")


def test_slice_covers_review_only_and_decision_context_surfaces() -> None:
    keys = {target.key for target in _TARGETS}
    assert "researchProposalAcceptButton" in keys
    assert "researchProposalSeparateButton" in keys
    assert "researchProposalRejectButton" in keys
    assert "researchProposalDecisionContext" in keys
    assert "researchDecisionFlow" in keys
