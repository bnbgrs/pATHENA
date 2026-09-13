from __future__ import annotations

import pytest

from athena.knowledge.identity_relation_policy import (
    IdentityRelationDecision,
    IdentityRelationPolicy,
)


def test_string_similarity_alone_never_permits_same_as() -> None:
    assessment = IdentityRelationPolicy.assess(
        semantic_identity_confirmed=False,
        different_from_confirmed=False,
        string_similarity_only=True,
    )

    assert assessment.decision is IdentityRelationDecision.REQUIRE_REVIEW
    assert assessment.permits_same_as is False
    assert assessment.reason == "string_similarity_is_not_identity_evidence"


def test_explicit_semantic_identity_permits_same_as() -> None:
    assessment = IdentityRelationPolicy.assess(
        semantic_identity_confirmed=True,
        different_from_confirmed=False,
        string_similarity_only=False,
    )

    assert assessment.decision is IdentityRelationDecision.ALLOW_SAME_AS
    assert assessment.permits_same_as is True


def test_explicit_different_from_keeps_entities_distinct() -> None:
    assessment = IdentityRelationPolicy.assess(
        semantic_identity_confirmed=False,
        different_from_confirmed=True,
        string_similarity_only=True,
    )

    assert assessment.decision is IdentityRelationDecision.KEEP_DISTINCT
    assert assessment.permits_same_as is False


def test_conflicting_explicit_identity_evidence_requires_review() -> None:
    assessment = IdentityRelationPolicy.assess(
        semantic_identity_confirmed=True,
        different_from_confirmed=True,
        string_similarity_only=False,
    )

    assert assessment.decision is IdentityRelationDecision.REQUIRE_REVIEW
    assert assessment.permits_same_as is False
    assert assessment.reason == "conflicting_explicit_identity_evidence"


def test_absent_identity_evidence_requires_review() -> None:
    assessment = IdentityRelationPolicy.assess(
        semantic_identity_confirmed=False,
        different_from_confirmed=False,
        string_similarity_only=False,
    )

    assert assessment.decision is IdentityRelationDecision.REQUIRE_REVIEW
    assert assessment.permits_same_as is False


@pytest.mark.parametrize(
    "field",
    [
        "semantic_identity_confirmed",
        "different_from_confirmed",
        "string_similarity_only",
    ],
)
def test_identity_policy_rejects_non_boolean_signals(field: str) -> None:
    values: dict[str, object] = {
        "semantic_identity_confirmed": False,
        "different_from_confirmed": False,
        "string_similarity_only": False,
    }
    values[field] = 1

    with pytest.raises(TypeError, match=f"{field} must be a bool"):
        IdentityRelationPolicy.assess(**values)  # type: ignore[arg-type]
