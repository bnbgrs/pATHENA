from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge_history import KnowledgeHistoryApiService
from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
)

KNOWLEDGE_ID = uuid.UUID("018f0000-0000-7000-8000-000000000001")
ACTOR_ID = uuid.UUID("018f0000-0000-7000-8000-000000000002")


class _HistoryReader:
    def __init__(self, revisions: tuple[KnowledgeUnitRevision, ...]) -> None:
        self.revisions = revisions
        self.calls: list[uuid.UUID] = []

    def history(self, knowledge_id: uuid.UUID) -> tuple[KnowledgeUnitRevision, ...]:
        self.calls.append(knowledge_id)
        return self.revisions


def _revision(
    number: int,
    *,
    body: str,
    title: str | None = "Title",
    knowledge_id: uuid.UUID = KNOWLEDGE_ID,
    created_at_us: int | None = None,
) -> KnowledgeUnitRevision:
    return KnowledgeUnitRevision(
        knowledge_id=knowledge_id,
        revision_id=uuid.UUID(f"018f0000-0000-7000-8000-{number:012d}"),
        revision_no=number,
        created_at_us=number * 100 if created_at_us is None else created_at_us,
        created_by_actor_id=ACTOR_ID,
        provenance_id=uuid.UUID(f"018f0000-0000-7001-8000-{number:012d}"),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title=title,
            body=body,
            epistemic_status=EpistemicStatus.ASSERTED,
        ),
    )


def test_revision_history_projects_real_revision_facts_and_derived_diff() -> None:
    reader = _HistoryReader(
        (
            _revision(1, body="alpha"),
            _revision(2, body="beta", title="Updated"),
        )
    )
    service = KnowledgeHistoryApiService(knowledge=reader)

    response = service.revision_history(str(KNOWLEDGE_ID))

    assert reader.calls == [KNOWLEDGE_ID]
    assert response.knowledge_id == str(KNOWLEDGE_ID)
    assert len(response.entries) == 2
    assert response.entries[0].revision_no == 1
    assert response.entries[0].changes_from_previous == ()
    assert response.entries[1].revision_no == 2
    assert response.entries[1].actor_id == str(ACTOR_ID)
    assert tuple(change.field for change in response.entries[1].changes_from_previous) == (
        "title",
        "body",
    )
    assert response.entries[1].changes_from_previous[0].previous == "Title"
    assert response.entries[1].changes_from_previous[0].current == "Updated"
    assert response.entries[1].changes_from_previous[1].previous == "alpha"
    assert response.entries[1].changes_from_previous[1].current == "beta"


def test_revision_history_rejects_invalid_uuid_before_repository_access() -> None:
    reader = _HistoryReader((_revision(1, body="alpha"),))
    service = KnowledgeHistoryApiService(knowledge=reader)

    with pytest.raises(ValueError):
        service.revision_history("not-a-uuid")

    assert reader.calls == []


def test_revision_history_rejects_empty_history() -> None:
    service = KnowledgeHistoryApiService(knowledge=_HistoryReader(()))

    with pytest.raises(ValueError, match="at least one revision"):
        service.revision_history(str(KNOWLEDGE_ID))


def test_revision_history_rejects_noncontiguous_revisions() -> None:
    reader = _HistoryReader(
        (
            _revision(1, body="alpha"),
            _revision(3, body="gamma"),
        )
    )
    service = KnowledgeHistoryApiService(knowledge=reader)

    with pytest.raises(ValueError, match="contiguous"):
        service.revision_history(str(KNOWLEDGE_ID))


def test_revision_history_rejects_cross_entity_revision() -> None:
    other_id = uuid.UUID("018f0000-0000-7000-8000-000000000099")
    reader = _HistoryReader(
        (
            _revision(1, body="alpha"),
            _revision(2, body="beta", knowledge_id=other_id),
        )
    )
    service = KnowledgeHistoryApiService(knowledge=reader)

    with pytest.raises(ValueError, match="another entity"):
        service.revision_history(str(KNOWLEDGE_ID))


def test_revision_history_rejects_timestamp_regression() -> None:
    reader = _HistoryReader(
        (
            _revision(1, body="alpha", created_at_us=200),
            _revision(2, body="beta", created_at_us=100),
        )
    )
    service = KnowledgeHistoryApiService(knowledge=reader)

    with pytest.raises(ValueError, match="timestamp"):
        service.revision_history(str(KNOWLEDGE_ID))
