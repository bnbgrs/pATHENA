import uuid

import pytest

from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
)
from athena.knowledge.revision_change_explanation import explain_knowledge_revision_change

KNOWLEDGE_ID = uuid.UUID("00000000-0000-7000-8000-000000000001")
ACTOR_ID = uuid.UUID("00000000-0000-7000-8000-000000000010")


def _revision(
    revision_no: int,
    *,
    body: str,
    title: str | None = None,
    status: EpistemicStatus = EpistemicStatus.ASSERTED,
    knowledge_id: uuid.UUID = KNOWLEDGE_ID,
    created_at_us: int | None = None,
) -> KnowledgeUnitRevision:
    suffix = revision_no + 1
    return KnowledgeUnitRevision(
        knowledge_id=knowledge_id,
        revision_id=uuid.UUID(f"00000000-0000-7000-8000-{suffix:012d}"),
        revision_no=revision_no,
        created_at_us=created_at_us if created_at_us is not None else revision_no * 1_000_000,
        created_by_actor_id=ACTOR_ID,
        provenance_id=uuid.UUID(f"00000000-0000-7000-9000-{suffix:012d}"),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.FACT,
            title=title,
            body=body,
            epistemic_status=status,
        ),
    )


def test_explains_adjacent_revision_from_recorded_reason_and_payload_diff() -> None:
    previous = _revision(1, body="old", title="Fact")
    current = _revision(
        2,
        body="new",
        title="Fact",
        status=EpistemicStatus.SUPPORTED,
    )

    explanation = explain_knowledge_revision_change(
        previous,
        current,
        recorded_reason=" user correction ",
    )

    assert explanation.knowledge_id == KNOWLEDGE_ID
    assert explanation.previous_revision_id == previous.revision_id
    assert explanation.current_revision_id == current.revision_id
    assert explanation.changed_by_actor_id == ACTOR_ID
    assert explanation.recorded_reason == "user correction"
    assert tuple(change.field for change in explanation.changes) == ("body", "epistemic_status")
    assert explanation.changes[0].previous == "old"
    assert explanation.changes[0].current == "new"
    assert "Recorded reason: user correction." in explanation.text
    assert "Changed payload fields: body, epistemic_status." in explanation.text
    assert "1970-01-01T00:00:02+00:00" in explanation.text


def test_unsupplied_reason_does_not_claim_persisted_reason_is_unavailable() -> None:
    previous = _revision(1, body="same")
    current = _revision(2, body="same")

    explanation = explain_knowledge_revision_change(previous, current)

    assert explanation.recorded_reason is None
    assert explanation.changes == ()
    assert "No recorded reason was supplied to this explanation." in explanation.text
    assert "No recorded reason is available." not in explanation.text
    assert "No payload fields changed." in explanation.text


def test_rejects_revisions_from_different_knowledge_units() -> None:
    previous = _revision(1, body="old")
    current = _revision(2, body="new", knowledge_id=uuid.uuid4())

    with pytest.raises(ValueError, match="same KnowledgeUnit"):
        explain_knowledge_revision_change(previous, current)


def test_rejects_non_adjacent_revision_pair() -> None:
    previous = _revision(1, body="old")
    current = _revision(3, body="new")

    with pytest.raises(ValueError, match="direct successor"):
        explain_knowledge_revision_change(previous, current)


def test_rejects_timestamp_regression() -> None:
    previous = _revision(1, body="old", created_at_us=2_000_000)
    current = _revision(2, body="new", created_at_us=1_000_000)

    with pytest.raises(ValueError, match="timestamp must not precede"):
        explain_knowledge_revision_change(previous, current)


def test_rejects_malformed_recorded_reason_boundary() -> None:
    with pytest.raises(TypeError, match="recorded_reason must be text or None"):
        explain_knowledge_revision_change(
            _revision(1, body="old"),
            _revision(2, body="new"),
            recorded_reason=object(),  # type: ignore[arg-type]
        )
