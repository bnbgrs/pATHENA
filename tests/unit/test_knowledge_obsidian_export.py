from __future__ import annotations

from pathlib import Path

from athena.desktop.knowledge_obsidian_export import preview_note
from athena.knowledge.obsidian_projection import ObsidianNote


def _note() -> ObsidianNote:
    return ObsidianNote(
        relative_path="Knowledge/Example--00000000-0000-0000-0000-000000000001.md",
        markdown="# Example\n\nCanonical body\n",
    )


def test_preview_create_does_not_write(tmp_path: Path) -> None:
    preview = preview_note(tmp_path, _note())

    assert preview.state == "create"
    assert preview.replace_required is False
    assert preview.relative_path == _note().relative_path
    assert not Path(preview.destination).exists()
    assert list(tmp_path.iterdir()) == []


def test_preview_identical_is_unchanged(tmp_path: Path) -> None:
    note = _note()
    destination = tmp_path / note.relative_path
    destination.parent.mkdir(parents=True)
    destination.write_text(note.markdown, encoding="utf-8")

    preview = preview_note(tmp_path, note)

    assert preview.state == "unchanged"
    assert preview.replace_required is False
    assert destination.read_text(encoding="utf-8") == note.markdown


def test_preview_divergent_requires_explicit_replace_without_mutation(tmp_path: Path) -> None:
    note = _note()
    destination = tmp_path / note.relative_path
    destination.parent.mkdir(parents=True)
    destination.write_text("user-authored local note\n", encoding="utf-8")

    preview = preview_note(tmp_path, note)

    assert preview.state == "conflict"
    assert preview.replace_required is True
    assert destination.read_text(encoding="utf-8") == "user-authored local note\n"


def test_preview_blocks_non_file_destination(tmp_path: Path) -> None:
    note = _note()
    destination = tmp_path / note.relative_path
    destination.mkdir(parents=True)

    preview = preview_note(tmp_path, note)

    assert preview.state == "blocked"
    assert preview.replace_required is False
