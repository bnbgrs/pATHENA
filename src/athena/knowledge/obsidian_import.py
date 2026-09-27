"""Fail-closed reconciliation of externally edited Obsidian Knowledge projections."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from athena.chat.service import ChatService
from athena.knowledge.models import (
    KnowledgeUnitDraft,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
)
from athena.knowledge.obsidian_projection import project_knowledge_snapshot
from athena.knowledge.repository import (
    KnowledgeConflictError,
    KnowledgeRepository,
)

_PROJECTION_VERSION = 1
_ENTITY_TYPE = "knowledge_unit"


class ObsidianImportError(ValueError):
    """Raised when edited projection text cannot be trusted or mapped safely."""


class ObsidianImportConflictError(RuntimeError):
    """Raised when an edit is based on a stale canonical Knowledge revision."""


@dataclass(frozen=True, slots=True)
class ParsedObsidianKnowledgeEdit:
    """Validated user-editable content tied to one exported canonical base."""

    knowledge_id: uuid.UUID
    expected_revision_id: uuid.UUID
    expected_revision_no: int
    title: str
    body: str
    metadata: dict[str, str | int]


def parse_obsidian_knowledge_edit(markdown: str) -> ParsedObsidianKnowledgeEdit:
    """Parse only the deterministic managed Knowledge projection contract."""
    if not isinstance(markdown, str):
        raise TypeError("markdown must be text.")
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0] != "---":
        raise ObsidianImportError("Obsidian projection must start with front matter.")

    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ObsidianImportError("Obsidian projection front matter is not terminated.") from exc
    if end <= 1:
        raise ObsidianImportError("Obsidian projection front matter is empty.")

    metadata = _parse_frontmatter(lines[1:end])
    _validate_projection_identity(metadata)

    content = lines[end + 1 :]
    while content and content[0] == "":
        content.pop(0)
    if not content or not content[0].startswith("# "):
        raise ObsidianImportError("Obsidian Knowledge projection requires one H1 title.")
    title = content.pop(0)[2:].strip()
    if not title:
        raise ObsidianImportError("Obsidian Knowledge title must not be empty.")
    if content and content[0] == "":
        content.pop(0)
    body = "\n".join(content).rstrip("\n").strip()
    if not body:
        raise ObsidianImportError("Obsidian Knowledge body must not be empty.")

    knowledge_text = _alias_text(
        metadata,
        "athena_id",
        "athena_knowledge_id",
    )
    revision_text = _alias_text(
        metadata,
        "revision_id",
        "athena_revision_id",
    )
    revision_no = _alias_int(
        metadata,
        "revision_no",
        "athena_revision_no",
    )

    return ParsedObsidianKnowledgeEdit(
        knowledge_id=_canonical_uuid(knowledge_text, "athena_id"),
        expected_revision_id=_canonical_uuid(revision_text, "revision_id"),
        expected_revision_no=revision_no,
        title=title,
        body=body,
        metadata=metadata,
    )


class ObsidianKnowledgeReconciler:
    """Commit one explicit external edit as a normal user-authored revision."""

    def __init__(
        self,
        *,
        repository: KnowledgeRepository,
        chat: ChatService,
    ) -> None:
        self.repository = repository
        self.chat = chat

    def apply_markdown(self, markdown: str) -> KnowledgeUnitRevision:
        edit = parse_obsidian_knowledge_edit(markdown)
        current = self.repository.load_current(edit.knowledge_id)
        revision = current.revision

        if (
            revision.revision_id != edit.expected_revision_id
            or revision.revision_no != edit.expected_revision_no
        ):
            raise ObsidianImportConflictError(
                "Obsidian edit is based on a stale Knowledge revision."
            )

        _require_unchanged_projected_metadata(edit.metadata, current)

        current_payload = revision.payload
        projected_base_title = parse_obsidian_knowledge_edit(
            project_knowledge_snapshot(current).markdown
        ).title
        next_title = (
            current_payload.title
            if edit.title == projected_base_title
            else edit.title
        )
        if (
            current_payload.title == next_title
            and current_payload.body == edit.body
        ):
            return revision

        actor_id = self.chat.ensure_local_user()
        try:
            return self.repository.revise_knowledge_unit(
                actor_id=actor_id,
                knowledge_id=edit.knowledge_id,
                expected_revision_id=edit.expected_revision_id,
                draft=KnowledgeUnitDraft(
                    knowledge_kind=current_payload.knowledge_kind,
                    title=next_title,
                    body=edit.body,
                    valid_from_us=current_payload.valid_from_us,
                    valid_to_us=current_payload.valid_to_us,
                    epistemic_status=current_payload.epistemic_status,
                ),
                source_entity_id=edit.knowledge_id,
                source_revision_id=edit.expected_revision_id,
                input_role="obsidian_projection_base",
                reason="explicit user revision from obsidian projection",
            )
        except KnowledgeConflictError as exc:
            raise ObsidianImportConflictError(
                "Obsidian edit lost an optimistic revision race."
            ) from exc


def _parse_frontmatter(lines: list[str]) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {}
    for line in lines:
        if ": " not in line:
            raise ObsidianImportError("Obsidian front matter contains an invalid field.")
        key, raw = line.split(": ", 1)
        if not key or key in metadata:
            raise ObsidianImportError("Obsidian front matter contains a duplicate/empty key.")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            if raw.isascii() and raw.isdigit():
                value = int(raw)
            else:
                raise ObsidianImportError(
                    f"Obsidian front matter field {key!r} is not canonical JSON/int."
                ) from None
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise ObsidianImportError(
                f"Obsidian front matter field {key!r} has unsupported type."
            )
        metadata[key] = value
    return metadata


def _validate_projection_identity(metadata: dict[str, str | int]) -> None:
    entity_type = metadata.get("entity_type")
    if entity_type is not None and entity_type != _ENTITY_TYPE:
        raise ObsidianImportError("Obsidian entity_type must be knowledge_unit.")
    projection_version = metadata.get("projection_version")
    if projection_version is not None and projection_version != _PROJECTION_VERSION:
        raise ObsidianImportError("Unsupported Obsidian projection_version.")


def _alias_text(
    metadata: dict[str, str | int],
    canonical: str,
    legacy: str,
) -> str:
    values = [metadata.get(canonical), metadata.get(legacy)]
    present = [value for value in values if value is not None]
    if not present:
        raise ObsidianImportError(f"Missing Obsidian identity field {canonical!r}.")
    if any(not isinstance(value, str) for value in present):
        raise ObsidianImportError(f"Obsidian field {canonical!r} must be text.")
    if len(present) == 2 and present[0] != present[1]:
        raise ObsidianImportError(f"Obsidian identity aliases for {canonical!r} disagree.")
    return str(present[0])


def _alias_int(
    metadata: dict[str, str | int],
    canonical: str,
    legacy: str,
) -> int:
    values = [metadata.get(canonical), metadata.get(legacy)]
    present = [value for value in values if value is not None]
    if not present:
        raise ObsidianImportError(f"Missing Obsidian revision field {canonical!r}.")
    if any(type(value) is not int or value < 1 for value in present):
        raise ObsidianImportError(f"Obsidian field {canonical!r} must be an integer >= 1.")
    if len(present) == 2 and present[0] != present[1]:
        raise ObsidianImportError(f"Obsidian revision aliases for {canonical!r} disagree.")
    return int(present[0])


def _canonical_uuid(value: str, field: str) -> uuid.UUID:
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise ObsidianImportError(f"Obsidian field {field!r} must be a UUID.") from exc
    if str(parsed) != value:
        raise ObsidianImportError(f"Obsidian field {field!r} must use canonical UUID text.")
    return parsed


def _require_unchanged_projected_metadata(
    metadata: dict[str, str | int],
    current: KnowledgeUnitSnapshot,
) -> None:
    revision = current.revision
    payload = revision.payload
    expected: dict[str, str | int] = {
        "athena_kind": payload.knowledge_kind.value,
        "athena_epistemic_status": payload.epistemic_status.value,
        "athena_lifecycle_state": current.lifecycle_state,
        "athena_provenance_id": str(revision.provenance_id),
        "athena_created_at_us": revision.created_at_us,
    }
    if payload.valid_from_us is not None:
        expected["athena_valid_from_us"] = payload.valid_from_us
    if payload.valid_to_us is not None:
        expected["athena_valid_to_us"] = payload.valid_to_us

    for key, expected_value in expected.items():
        value = metadata.get(key)
        if value is not None and value != expected_value:
            raise ObsidianImportError(
                f"Projected metadata {key!r} cannot be edited through this v1 roundtrip."
            )
