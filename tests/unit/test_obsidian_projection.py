from __future__ import annotations

import uuid

import pytest

from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
)
from athena.knowledge.obsidian_projection import project_knowledge_snapshot


def _snapshot(*, title: str | None = "Project / Decision: Alpha?", body: str = "Keep it local.") -> KnowledgeUnitSnapshot:
    knowledge_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
    revision = KnowledgeUnitRevision(
        knowledge_id=knowledge_id,
        revision_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        revision_no=3,
        created_at_us=1_700_000_000_000_000,
        created_by_actor_id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        provenance_id=uuid.UUID("44444444-4444-4444-4444-444444444444"),
        payload=KnowledgeUnitDraft(
            knowledge_kind=KnowledgeKind.DECISION,
            title=title,
            body=body,
            epistemic_status=EpistemicStatus.SUPPORTED,
            valid_from_us=1_699_999_000_000_000,
        ),
    )
    return KnowledgeUnitSnapshot(
        knowledge_id=knowledge_id,
        lifecycle_state="active",
        revision=revision,
    )


def test_projection_is_deterministic_and_obsidian_safe() -> None:
    note = project_knowledge_snapshot(_snapshot())

    assert note.relative_path == (
        "Knowledge/Project - Decision- Alpha--11111111-1111-1111-1111-111111111111.md"
    )
    assert note.markdown == (
        "---\n"
        'athena_knowledge_id: "11111111-1111-1111-1111-111111111111"\n'
        'athena_revision_id: "22222222-2222-2222-2222-222222222222"\n'
        "athena_revision_no: 3\n"
        'athena_provenance_id: "44444444-4444-4444-4444-444444444444"\n'
        'athena_kind: "decision"\n'
        'athena_epistemic_status: "supported"\n'
        'athena_lifecycle_state: "active"\n'
        "athena_created_at_us: 1700000000000000\n"
        "athena_valid_from_us: 1699999000000000\n"
        "---\n\n"
        "# Project / Decision: Alpha?\n\n"
        "Keep it local.\n"
    )


def test_projection_uses_body_for_missing_title_without_writing_anything() -> None:
    note = project_knowledge_snapshot(
        _snapshot(title=None, body="First line becomes title\nSecond line stays body")
    )

    assert note.relative_path.startswith("Knowledge/First line becomes title--")
    assert "# First line becomes title\n" in note.markdown
    assert note.markdown.endswith("First line becomes title\nSecond line stays body\n")


def test_projection_rejects_non_snapshot_input() -> None:
    with pytest.raises(TypeError, match="KnowledgeUnitSnapshot"):
        project_knowledge_snapshot(object())  # type: ignore[arg-type]
