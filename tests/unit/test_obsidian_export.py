from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.knowledge.models import (
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
)
from athena.knowledge.obsidian_export import (
    ObsidianConflictPolicy,
    ObsidianExportConflictError,
    ObsidianExportStatus,
    ObsidianVaultExporter,
)
from athena.knowledge.obsidian_projection import ObsidianNote, project_knowledge_snapshot


def _snapshot(*, body: str = "Keep it local.") -> KnowledgeUnitSnapshot:
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
            title="Project Alpha",
            body=body,
            epistemic_status=EpistemicStatus.SUPPORTED,
        ),
    )
    return KnowledgeUnitSnapshot(
        knowledge_id=knowledge_id,
        lifecycle_state="active",
        revision=revision,
    )


def test_export_creates_deterministic_note_and_is_idempotent(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    snapshot = _snapshot()
    note = project_knowledge_snapshot(snapshot)

    first = exporter.export_snapshot(snapshot)
    second = exporter.export_snapshot(snapshot)

    assert first.status is ObsidianExportStatus.CREATED
    assert second.status is ObsidianExportStatus.UNCHANGED
    assert first.path == tmp_path / Path(*note.relative_path.split("/"))
    assert first.path.read_text(encoding="utf-8") == note.markdown


def test_export_conflict_fails_closed_without_overwriting(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    snapshot = _snapshot()
    result = exporter.export_snapshot(snapshot)
    result.path.write_text("user-edited\n", encoding="utf-8")

    with pytest.raises(ObsidianExportConflictError, match="explicit REPLACE"):
        exporter.export_snapshot(snapshot)

    assert result.path.read_text(encoding="utf-8") == "user-edited\n"


def test_export_replace_requires_explicit_policy(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    original = _snapshot()
    first = exporter.export_snapshot(original)
    first.path.write_text("stale\n", encoding="utf-8")

    result = exporter.export_snapshot(
        original,
        conflict_policy=ObsidianConflictPolicy.REPLACE,
    )

    assert result.status is ObsidianExportStatus.REPLACED
    assert result.path.read_text(encoding="utf-8") == project_knowledge_snapshot(original).markdown


def test_error_policy_rejects_even_identical_existing_note(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    snapshot = _snapshot()
    exporter.export_snapshot(snapshot)

    with pytest.raises(ObsidianExportConflictError, match="already exists"):
        exporter.export_snapshot(
            snapshot,
            conflict_policy=ObsidianConflictPolicy.ERROR,
        )


def test_export_rejects_parent_traversal_before_writing(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    malicious = ObsidianNote(relative_path="../escape.md", markdown="escape")

    with pytest.raises(ValueError, match="portable relative segments"):
        exporter.export_note(malicious)

    assert not (tmp_path.parent / "escape.md").exists()


@pytest.mark.parametrize(
    "relative_path",
    (
        "Knowledge/./escape.md",
        "Knowledge//escape.md",
        "C:/escape.md",
        "Knowledge/C:/escape.md",
    ),
)
def test_export_rejects_nonportable_raw_segments(
    tmp_path: Path,
    relative_path: str,
) -> None:
    exporter = ObsidianVaultExporter(tmp_path)

    with pytest.raises(ValueError, match="portable relative segments"):
        exporter.export_note(ObsidianNote(relative_path=relative_path, markdown="escape"))


def test_export_rejects_backslash_path_alias(tmp_path: Path) -> None:
    exporter = ObsidianVaultExporter(tmp_path)
    malicious = ObsidianNote(relative_path=r"Knowledge\..\escape.md", markdown="escape")

    with pytest.raises(ValueError, match="POSIX-relative"):
        exporter.export_note(malicious)


def test_export_rejects_symlinked_parent_boundary(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    vault = tmp_path / "vault"
    vault.mkdir()
    knowledge = vault / "Knowledge"
    try:
        knowledge.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Filesystem does not permit directory symlink creation.")

    exporter = ObsidianVaultExporter(vault)

    with pytest.raises(NotADirectoryError, match="unsafe filesystem boundary"):
        exporter.export_snapshot(_snapshot())

    assert list(outside.iterdir()) == []


def test_exporter_requires_existing_real_vault_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing-vault"

    with pytest.raises(NotADirectoryError, match="existing real directory"):
        ObsidianVaultExporter(missing)
