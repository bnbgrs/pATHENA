from __future__ import annotations

from uuid import UUID

import pytest

from athena.knowledge.concept_note_provenance import ConceptNoteRevisionRef
from athena.knowledge.concept_note_update import (
    ConceptNoteChangeRelevance,
    ConceptNoteUpdateAction,
    ConceptNoteUpdatePolicy,
)


def _ref(entity: int, revision: int) -> ConceptNoteRevisionRef:
    return ConceptNoteRevisionRef(
        entity_id=UUID(int=entity),
        revision_id=UUID(int=revision),
    )


def test_relevant_new_revision_creates_proposal_not_automatic_write() -> None:
    decision = ConceptNoteUpdatePolicy().decide(
        current_inputs=(_ref(1, 10),),
        candidate_inputs=(_ref(1, 10), _ref(2, 20)),
        relevance=ConceptNoteChangeRelevance.RELEVANT,
    )

    assert decision.action is ConceptNoteUpdateAction.PROPOSE_UPDATE
    assert decision.new_input_revisions == (_ref(2, 20),)
    assert decision.reason == "relevant_new_input_revisions"


def test_unknown_relevance_keeps_current_note_fail_closed() -> None:
    decision = ConceptNoteUpdatePolicy().decide(
        current_inputs=(_ref(1, 10),),
        candidate_inputs=(_ref(1, 10), _ref(2, 20)),
        relevance=ConceptNoteChangeRelevance.UNKNOWN,
    )

    assert decision.action is ConceptNoteUpdateAction.KEEP_CURRENT
    assert decision.new_input_revisions == (_ref(2, 20),)
    assert decision.reason == "relevance_not_confirmed"


def test_irrelevant_new_revision_does_not_rewrite_note() -> None:
    decision = ConceptNoteUpdatePolicy().decide(
        current_inputs=(_ref(1, 10),),
        candidate_inputs=(_ref(1, 10), _ref(2, 20)),
        relevance=ConceptNoteChangeRelevance.IRRELEVANT,
    )

    assert decision.action is ConceptNoteUpdateAction.KEEP_CURRENT
    assert decision.reason == "new_inputs_not_relevant"


def test_no_new_revision_keeps_current_note_even_when_marked_relevant() -> None:
    decision = ConceptNoteUpdatePolicy().decide(
        current_inputs=(_ref(1, 10),),
        candidate_inputs=(_ref(1, 10),),
        relevance=ConceptNoteChangeRelevance.RELEVANT,
    )

    assert decision.action is ConceptNoteUpdateAction.KEEP_CURRENT
    assert decision.new_input_revisions == ()
    assert decision.reason == "no_new_input_revisions"


def test_duplicate_candidate_revisions_fail_closed() -> None:
    duplicate = _ref(2, 20)

    with pytest.raises(ValueError, match="candidate_inputs must not contain duplicate"):
        ConceptNoteUpdatePolicy().decide(
            current_inputs=(_ref(1, 10),),
            candidate_inputs=(duplicate, duplicate),
            relevance=ConceptNoteChangeRelevance.RELEVANT,
        )


def test_non_revision_input_fails_closed() -> None:
    with pytest.raises(TypeError, match="ConceptNoteRevisionRef"):
        ConceptNoteUpdatePolicy().decide(
            current_inputs=(_ref(1, 10),),
            candidate_inputs=(object(),),  # type: ignore[arg-type]
            relevance=ConceptNoteChangeRelevance.RELEVANT,
        )
