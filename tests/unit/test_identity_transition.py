from uuid import UUID

from athena.knowledge.identity_transition import MergeTransition, SplitTransition
import pytest


A = UUID("00000000-0000-0000-0000-000000000001")
B = UUID("00000000-0000-0000-0000-000000000002")
C = UUID("00000000-0000-0000-0000-000000000003")
D = UUID("00000000-0000-0000-0000-000000000004")


def test_merge_can_reuse_semantically_continuous_identity() -> None:
    transition = MergeTransition(source_entity_ids=(A, B), result_entity_id=A)

    assert transition.reuses_existing_identity is True
    assert transition.superseded_entity_ids == (B,)


def test_merge_can_create_new_identity_and_supersede_all_sources() -> None:
    transition = MergeTransition(source_entity_ids=(A, B), result_entity_id=C)

    assert transition.reuses_existing_identity is False
    assert transition.superseded_entity_ids == (A, B)


def test_merge_rejects_insufficient_or_duplicate_sources() -> None:
    with pytest.raises(ValueError, match="at least two"):
        MergeTransition(source_entity_ids=(A,), result_entity_id=A)

    with pytest.raises(ValueError, match="unique"):
        MergeTransition(source_entity_ids=(A, A), result_entity_id=B)


def test_split_creates_new_independently_addressable_identities() -> None:
    transition = SplitTransition(source_entity_id=A, result_entity_ids=(B, C))

    assert transition.result_entity_ids == (B, C)
    assert transition.superseded_entity_ids == (A,)


def test_split_rejects_reused_source_identity() -> None:
    with pytest.raises(ValueError, match="new identities"):
        SplitTransition(source_entity_id=A, result_entity_ids=(A, B))


def test_split_rejects_insufficient_or_duplicate_results() -> None:
    with pytest.raises(ValueError, match="at least two"):
        SplitTransition(source_entity_id=A, result_entity_ids=(B,))

    with pytest.raises(ValueError, match="unique"):
        SplitTransition(source_entity_id=A, result_entity_ids=(B, B))
