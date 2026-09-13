from __future__ import annotations

import uuid

import pytest

from athena.knowledge.merge_split_policy import (
    KnowledgeIdentityPlanError,
    plan_knowledge_merge,
    plan_knowledge_split,
)


def test_merge_can_retain_left_identity_and_supersede_absorbed_entity() -> None:
    left = uuid.uuid4()
    right = uuid.uuid4()

    plan = plan_knowledge_merge(
        left_entity_id=left,
        right_entity_id=right,
        result_entity_id=left,
    )

    assert plan.result_entity_id == left
    assert plan.superseded_entity_ids == (right,)
    assert plan.retains_existing_identity is True


def test_merge_can_retain_right_identity() -> None:
    left = uuid.uuid4()
    right = uuid.uuid4()

    plan = plan_knowledge_merge(
        left_entity_id=left,
        right_entity_id=right,
        result_entity_id=right,
    )

    assert plan.superseded_entity_ids == (left,)
    assert plan.retains_existing_identity is True


def test_merge_with_new_identity_supersedes_both_originals() -> None:
    left = uuid.uuid4()
    right = uuid.uuid4()
    result = uuid.uuid4()

    plan = plan_knowledge_merge(
        left_entity_id=left,
        right_entity_id=right,
        result_entity_id=result,
    )

    assert plan.superseded_entity_ids == (left, right)
    assert plan.retains_existing_identity is False


def test_merge_rejects_same_entity_on_both_sides() -> None:
    entity_id = uuid.uuid4()

    with pytest.raises(KnowledgeIdentityPlanError, match="two distinct"):
        plan_knowledge_merge(
            left_entity_id=entity_id,
            right_entity_id=entity_id,
            result_entity_id=entity_id,
        )


def test_split_requires_new_unique_child_identities_and_supersedes_source() -> None:
    source = uuid.uuid4()
    first = uuid.uuid4()
    second = uuid.uuid4()

    plan = plan_knowledge_split(
        source_entity_id=source,
        result_entity_ids=(first, second),
    )

    assert plan.result_entity_ids == (first, second)
    assert plan.superseded_entity_ids == (source,)


@pytest.mark.parametrize(
    "result_ids, expected_message",
    [
        ((uuid.uuid4(),), "at least two"),
        ((uuid.UUID(int=1), uuid.UUID(int=1)), "must be unique"),
    ],
)
def test_split_rejects_invalid_result_sets(
    result_ids: tuple[uuid.UUID, ...],
    expected_message: str,
) -> None:
    with pytest.raises(KnowledgeIdentityPlanError, match=expected_message):
        plan_knowledge_split(
            source_entity_id=uuid.uuid4(),
            result_entity_ids=result_ids,
        )


def test_split_rejects_source_identity_as_result() -> None:
    source = uuid.uuid4()

    with pytest.raises(KnowledgeIdentityPlanError, match="new identities"):
        plan_knowledge_split(
            source_entity_id=source,
            result_entity_ids=(source, uuid.uuid4()),
        )


def test_planner_fails_closed_on_non_uuid_identity() -> None:
    with pytest.raises(TypeError, match="left_entity_id must be a UUID"):
        plan_knowledge_merge(  # type: ignore[arg-type]
            left_entity_id="not-a-uuid",
            right_entity_id=uuid.uuid4(),
            result_entity_id=uuid.uuid4(),
        )

    with pytest.raises(TypeError, match="tuple of UUIDs"):
        plan_knowledge_split(  # type: ignore[arg-type]
            source_entity_id=uuid.uuid4(),
            result_entity_ids=[uuid.uuid4(), uuid.uuid4()],
        )
