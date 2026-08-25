"""Deterministic, read-only Obsidian projection for canonical Knowledge snapshots.

The projection is intentionally side-effect free: canonical storage remains authoritative and
callers decide whether, where, and how projected Markdown is persisted.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from athena.knowledge.models import KnowledgeUnitSnapshot

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")
_MAX_STEM_LENGTH = 80


@dataclass(frozen=True, slots=True)
class ObsidianNote:
    """One deterministic Markdown projection ready for an Obsidian vault."""

    relative_path: str
    markdown: str


def project_knowledge_snapshot(snapshot: KnowledgeUnitSnapshot) -> ObsidianNote:
    """Project one canonical snapshot without mutating or persisting canonical state."""

    if not isinstance(snapshot, KnowledgeUnitSnapshot):
        raise TypeError("snapshot must be a KnowledgeUnitSnapshot.")

    revision = snapshot.revision
    payload = revision.payload
    title = payload.title or _fallback_title(payload.body)
    stem = _safe_stem(title)
    relative_path = f"Knowledge/{stem}--{snapshot.knowledge_id}.md"

    frontmatter: dict[str, str | int] = {
        "athena_knowledge_id": str(snapshot.knowledge_id),
        "athena_revision_id": str(revision.revision_id),
        "athena_revision_no": revision.revision_no,
        "athena_provenance_id": str(revision.provenance_id),
        "athena_kind": payload.knowledge_kind.value,
        "athena_epistemic_status": payload.epistemic_status.value,
        "athena_lifecycle_state": snapshot.lifecycle_state,
        "athena_created_at_us": revision.created_at_us,
    }
    if payload.valid_from_us is not None:
        frontmatter["athena_valid_from_us"] = payload.valid_from_us
    if payload.valid_to_us is not None:
        frontmatter["athena_valid_to_us"] = payload.valid_to_us

    markdown = _render_markdown(
        title=_single_line_title(title),
        body=payload.body,
        frontmatter=frontmatter,
    )
    return ObsidianNote(relative_path=relative_path, markdown=markdown)


def _render_markdown(*, title: str, body: str, frontmatter: dict[str, str | int]) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, str):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(("---", "", f"# {title}", "", body, ""))
    return "\n".join(lines)


def _fallback_title(body: str) -> str:
    first_line = body.splitlines()[0].strip()
    if not first_line:
        return "Untitled knowledge"
    return first_line[:_MAX_STEM_LENGTH]


def _single_line_title(title: str) -> str:
    return _WHITESPACE.sub(" ", title.strip())


def _safe_stem(title: str) -> str:
    stem = _INVALID_FILENAME_CHARS.sub("-", title.strip())
    stem = _WHITESPACE.sub(" ", stem).strip(" .-")
    if not stem:
        stem = "Untitled knowledge"
    return stem[:_MAX_STEM_LENGTH].rstrip(" .-") or "Untitled knowledge"
