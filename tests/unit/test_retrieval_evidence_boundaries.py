from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import EpistemicStatus
from athena.retrieval.evidence import (
    EvidenceClass,
    MemoryEvidenceClassification,
    MemoryEvidenceSelection,
)
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType


def _result(entity_type: SearchEntityType = SearchEntityType.KNOWLEDGE) -> HybridSearchResult:
    return HybridSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=entity_type,
        title=None,
        text="evidence",
        score=1.0,
        lexical_score=0.5,
        semantic_score=0.5,
        authority_score=1.0,
        contradiction_count=0,
        duplicate_count=0,
    )


def _classification(result: HybridSearchResult) -> MemoryEvidenceClassification:
    if result.entity_type is SearchEntityType.CHAT_MESSAGE:
        return MemoryEvidenceClassification(
            entity_id=result.entity_id,
            revision_id=result.revision_id,
            entity_type=result.entity_type,
            evidence_class=EvidenceClass.USER_STATEMENT,
            message_type="user",
            epistemic_status=None,
        )
    return MemoryEvidenceClassification(
        entity_id=result.entity_id,
        revision_id=result.revision_id,
        entity_type=result.entity_type,
        evidence_class=EvidenceClass.CANONICAL,
        message_type=None,
        epistemic_status=EpistemicStatus.SUPPORTED,
    )


def test_canonical_evidence_requires_epistemic_status() -> None:
    result = _result()
    with pytest.raises(ValueError, match="requires epistemic status"):
        MemoryEvidenceClassification(
            entity_id=result.entity_id,
            revision_id=result.revision_id,
            entity_type=result.entity_type,
            evidence_class=EvidenceClass.CANONICAL,
            message_type=None,
            epistemic_status=None,
        )


def test_user_statement_requires_user_chat_message() -> None:
    result = _result(SearchEntityType.CHAT_MESSAGE)
    with pytest.raises(ValueError, match="requires a user chat message"):
        MemoryEvidenceClassification(
            entity_id=result.entity_id,
            revision_id=result.revision_id,
            entity_type=result.entity_type,
            evidence_class=EvidenceClass.USER_STATEMENT,
            message_type="assistant",
            epistemic_status=None,
        )


def test_conversation_record_rejects_user_message() -> None:
    result = _result(SearchEntityType.CHAT_MESSAGE)
    with pytest.raises(ValueError, match="non-user chat message"):
        MemoryEvidenceClassification(
            entity_id=result.entity_id,
            revision_id=result.revision_id,
            entity_type=result.entity_type,
            evidence_class=EvidenceClass.CONVERSATION_RECORD,
            message_type="user",
            epistemic_status=None,
        )


def test_selection_requires_exact_classification_coverage() -> None:
    first = _result()
    second = _result(SearchEntityType.CLAIM)
    with pytest.raises(ValueError, match="exactly cover"):
        MemoryEvidenceSelection(
            policy_id="typed-provenance-v1",
            results=(first, second),
            classifications=(_classification(first),),
        )


def test_selection_rejects_duplicate_result_revision() -> None:
    result = _result()
    classification = _classification(result)
    with pytest.raises(ValueError, match="duplicate entity revisions"):
        MemoryEvidenceSelection(
            policy_id="typed-provenance-v1",
            results=(result, result),
            classifications=(classification,),
        )


def test_valid_selection_supports_lookup() -> None:
    result = _result(SearchEntityType.CHAT_MESSAGE)
    classification = _classification(result)
    selection = MemoryEvidenceSelection(
        policy_id="typed-provenance-v1",
        results=(result,),
        classifications=(classification,),
    )
    assert selection.classification_for(
        entity_type=result.entity_type,
        entity_id=result.entity_id,
        revision_id=result.revision_id,
    ) is classification
